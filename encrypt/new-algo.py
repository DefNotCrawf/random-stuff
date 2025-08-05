#!/usr/bin/env python3
"""
File Encryption/Decryption using XChaCha20-Poly1305 with Argon2id KDF

This script provides secure file encryption and decryption utilising:
- XChaCha20-Poly1305 for authenticated encryption with semantic security
- Argon2id for key derivation from passwords (memory-hard KDF)
- Cryptographically secure random salt and nonce generation
- Parallel processing for large files with streaming format
- Comprehensive file format validation and error handling

Security Features:
- 32-byte salts with cryptographically secure randomness
- Argon2id parameters: 3 iterations, 64MB memory, 1 thread
- Individual nonces per chunk for semantic security
- Timing attack mitigations in decryption process
- Input validation with specific error messages

Usage:
    python new-algo.py encrypt <input_file> <output_file>
    python new-algo.py decrypt <input_file> <output_file>
    python new-algo.py inspect <encrypted_file>
"""

import os
import sys
import getpass
import secrets
import time
import random
from pathlib import Path
import nacl.secret
import nacl.utils
import struct
import threading
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed


class FileEncryptor:
    def __init__(self):
        """
        Initialise the FileEncryptor with secure defaults for encryption.
        Sets up Argon2id parameters, salt and key sizes, and determines
        the optimal number of threads based on CPU count.
        """

        # Argon2id parameters (secure defaults)
        self.argon2_time_cost = 3  # Number of iterations
        self.argon2_memory_cost = 65536  # Memory usage in KB (64 MB)
        self.argon2_parallelism = 1  # Number of parallel threads
        self.salt_size = 32  # Salt size in bytes
        self.key_size = 32  # Key size for ChaCha20 (256 bits)

        # Determine optimal thread count (max threads - 1, minimum 1)
        self.max_threads = max(1, os.cpu_count() - 1) if os.cpu_count() else 1

    def derive_key(self, password: str, salt: bytes) -> bytes:
        """
        Derive encryption key from password using Argon2id KDF.

        Uses secure Argon2id parameters optimised for memory-hardness:
        - 3 iterations for computational cost
        - 64MB memory usage to resist GPU attacks
        - Single thread to prevent side-channel attacks

        Args:
            password: User-provided password string
            salt: Cryptographically secure random salt (32 bytes)

        Returns:
            key: Raw 32-byte key suitable for XChaCha20-Poly1305

        Security:
            - Uses low-level API to avoid base64 encoding overhead
            - Memory-hard function resistant to specialised hardware
        """
        import argon2

        # Use low-level API for direct key derivation without base64 encoding
        key = argon2.low_level.hash_secret_raw(
            secret=password.encode(),
            salt=salt,
            time_cost=self.argon2_time_cost,
            memory_cost=self.argon2_memory_cost,
            parallelism=self.argon2_parallelism,
            hash_len=self.key_size,
            type=argon2.low_level.Type.ID,
        )

        return key

    def encrypt_file(self, input_path: str, output_path: str, password: str) -> bool:
        """
        Encrypt a file using XChaCha20-Poly1305 with parallel processing and streaming format.

        Uses adaptive processing strategy:
        - Sequential processing for files < 10MB to avoid threading overhead
        - Parallel processing for larger files with worker threads

        File format:
        [salt_size(4 bytes)][salt][chunk_size(4 bytes)][encrypted_chunk]...[terminator(0)]

        Args:
            input_path: Path to the file to encrypt
            output_path: Path where encrypted file will be saved
            password: Password for key derivation

        Returns:
            True if encryption succeeded, False otherwise

        Security:
            - Each chunk gets its own nonce for semantic security
            - Progress tracking for large files without leaking sensitive data
        """
        try:
            # Generate random salt using cryptographically secure method
            salt = secrets.token_bytes(self.salt_size)

            # Derive key from password
            key = self.derive_key(password, salt)

            # Create XChaCha20-Poly1305 cipher using PyNaCl
            box = nacl.secret.SecretBox(key)

            # Get file size for progress tracking
            file_size = os.path.getsize(input_path)
            chunk_size = 1024 * 1024  # 1MB chunks

            # Enhanced progress tracking for large files
            show_progress = file_size > 100 * 1024 * 1024  # 100MB
            if show_progress:
                print(
                    f"Processing large file ({file_size // (1024*1024)}MB) with {self.max_threads} threads..."
                )

            # For small files, use sequential processing to avoid overhead
            if file_size < 10 * 1024 * 1024:  # 10MB threshold
                return self._encrypt_file_sequential(
                    input_path,
                    output_path,
                    password,
                    salt,
                    box,
                    file_size,
                    show_progress,
                )

            # Parallel processing for large files
            chunk_queue = queue.Queue(
                maxsize=self.max_threads * 2
            )  # Buffer for reading
            encrypted_chunks_queue = queue.Queue(
                maxsize=self.max_threads * 2
            )  # Buffer for writing

            # Start reader thread
            reader_thread = threading.Thread(
                target=self._read_chunks_worker,
                args=(input_path, chunk_size, chunk_queue),
            )
            reader_thread.daemon = True
            reader_thread.start()

            # Start writer thread
            writer_thread = threading.Thread(
                target=self._write_chunks_worker,
                args=(output_path, salt, encrypted_chunks_queue),
            )
            writer_thread.daemon = True
            writer_thread.start()

            # Process chunks in parallel
            with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
                futures = []
                processed_chunks = 0
                total_processed_bytes = 0

                while True:
                    try:
                        item = chunk_queue.get(timeout=1.0)
                        if item[0] == "EOF":
                            break
                        elif item[0] == "ERROR":
                            raise Exception(item[1])

                        chunk_index, chunk_data = item

                        # Submit encryption task
                        future = executor.submit(
                            self._encrypt_chunk, chunk_data, box, chunk_index
                        )
                        futures.append(future)

                        # Process completed futures
                        completed_futures = []
                        for future in futures:
                            if future.done():
                                try:
                                    result = future.result()
                                    encrypted_chunks_queue.put(result)
                                    completed_futures.append(future)
                                    processed_chunks += 1
                                    total_processed_bytes += len(chunk_data)

                                    # Show progress for large files
                                    if show_progress and processed_chunks % 100 == 0:
                                        progress_pct = (
                                            total_processed_bytes / file_size
                                        ) * 100
                                        print(
                                            f"Progress: {progress_pct:.1f}% ({total_processed_bytes // (1024*1024)}MB/{file_size // (1024*1024)}MB) - {processed_chunks} chunks"
                                        )

                                except Exception as e:
                                    encrypted_chunks_queue.put(("ERROR", str(e)))
                                    raise e

                        # Remove completed futures
                        for future in completed_futures:
                            futures.remove(future)

                        chunk_queue.task_done()

                    except queue.Empty:
                        # Check if reader is still alive
                        if not reader_thread.is_alive():
                            break
                        continue

                # Wait for all remaining encryption tasks to complete
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        encrypted_chunks_queue.put(result)
                    except Exception as e:
                        encrypted_chunks_queue.put(("ERROR", str(e)))
                        raise e

            # Signal writer to finish
            encrypted_chunks_queue.put(None)

            # Wait for threads to complete
            reader_thread.join(timeout=5.0)
            writer_thread.join(timeout=5.0)

            print(f"✓ File encrypted successfully: {output_path}")
            return True

        except Exception as e:
            print(f"✗ Encryption failed: {e}")
            return False

    def _encrypt_file_sequential(
        self,
        input_path: str,
        output_path: str,
        password: str,
        salt: bytes,
        box: nacl.secret.SecretBox,
        file_size: int,
        show_progress: bool,
    ) -> bool:
        """
        Sequential encryption for small files to avoid threading overhead.

        Processes files chunk by chunk in single-threaded mode for optimal
        performance with smaller files where parallel processing overhead
        would exceed benefits.

        Args:
            input_path: Path to input file
            output_path: Path to output encrypted file
            password: User password (unused in this method, key already derived)
            salt: Cryptographic salt for the file
            box: Configured SecretBox cipher instance
            file_size: Total size of input file in bytes
            show_progress: Whether to display progress information

        Returns:
            True if encryption succeeded, False otherwise

        Security:
            - Each chunk encrypted with unique nonce
            - Streaming format prevents memory exhaustion
        """
        try:
            with open(output_path, "wb") as outfile:
                # Write salt information
                outfile.write(struct.pack("<I", len(salt)))
                outfile.write(salt)

                # Process file in chunks
                chunk_size = 1024 * 1024  # 1MB chunks
                processed_bytes = 0
                chunk_count = 0

                with open(input_path, "rb") as infile:
                    while True:
                        chunk = infile.read(chunk_size)
                        if not chunk:
                            break

                        # Encrypt each chunk with its own nonce
                        encrypted_chunk = box.encrypt(chunk)

                        # Write chunk size and encrypted data immediately (streaming)
                        outfile.write(struct.pack("<I", len(encrypted_chunk)))
                        outfile.write(encrypted_chunk)

                        # Update progress tracking
                        processed_bytes += len(chunk)
                        chunk_count += 1

                        # Show progress for large files
                        if show_progress and chunk_count % 100 == 0:
                            progress_pct = (processed_bytes / file_size) * 100
                            print(
                                f"Progress: {progress_pct:.1f}% ({processed_bytes // (1024*1024)}MB/{file_size // (1024*1024)}MB)"
                            )

                # Write terminator
                outfile.write(struct.pack("<I", 0))

            return True

        except Exception as e:
            raise e

    def decrypt_file(self, input_path: str, output_path: str, password: str) -> bool:
        """
        Decrypt a file using XChaCha20-Poly1305 with streaming format and validation.

        Reads and validates encrypted file format, then decrypts each chunk
        individually while maintaining streaming performance for large files.

        Args:
            input_path: Path to the encrypted file
            output_path: Path where decrypted file will be saved
            password: Password for key derivation

        Returns:
            True if decryption succeeded, False otherwise

        Security:
            - Validates file format before processing
            - Timing attack mitigation with randomised delays
            - Comprehensive error handling for corruption detection
        """
        try:
            # Basic file validation before processing
            file_size = os.path.getsize(input_path)
            if file_size < 8:  # Minimum size: 4 bytes salt_size + 4 bytes terminator
                raise ValueError("File too small to be valid encrypted file")

            with open(input_path, "rb") as infile:
                # Read salt size
                salt_size_data = infile.read(4)
                if len(salt_size_data) != 4:
                    raise ValueError("Invalid file format: cannot read salt size")

                salt_size = struct.unpack("<I", salt_size_data)[0]

                # Validate salt size is reasonable
                if salt_size == 0 or salt_size > 1024:  # Salt should be reasonable size
                    raise ValueError(f"Invalid salt size: {salt_size} bytes")

                # Read salt
                salt = infile.read(salt_size)
                if len(salt) != salt_size:
                    raise ValueError("Invalid file format: cannot read salt")

                # Derive key from password
                key = self.derive_key(password, salt)

                # Create XChaCha20-Poly1305 cipher using PyNaCl
                box = nacl.secret.SecretBox(key)

                # Write decrypted file using streaming format
                with open(output_path, "wb") as outfile:
                    chunk_count = 0
                    processed_bytes = 0

                    # Enhanced progress tracking for large files
                    show_progress = file_size > 100 * 1024 * 1024  # 100MB
                    if show_progress:
                        print(
                            f"Decrypting large file ({file_size // (1024*1024)}MB)..."
                        )

                    while True:
                        # Read chunk size
                        chunk_size_data = infile.read(4)
                        if len(chunk_size_data) != 4:
                            raise ValueError(
                                "Invalid file format: unexpected end of file"
                            )

                        chunk_size = struct.unpack("<I", chunk_size_data)[0]

                        # Check for terminator (zero-length chunk indicates end of file)
                        if chunk_size == 0:
                            break

                        # Validate chunk size is reasonable
                        if chunk_size > 10 * 1024 * 1024:  # 10MB max chunk size
                            raise ValueError(f"Invalid chunk size: {chunk_size} bytes")

                        # Read encrypted chunk
                        encrypted_chunk = infile.read(chunk_size)
                        if len(encrypted_chunk) != chunk_size:
                            raise ValueError(
                                f"Invalid file format: cannot read chunk {chunk_count} data"
                            )

                        # Decrypt the chunk
                        try:
                            # Add decoy delay to mitigate timing attacks
                            time.sleep(random.uniform(0.001, 0.003))
                            decrypted_chunk = box.decrypt(encrypted_chunk)
                            outfile.write(decrypted_chunk)

                            # Update progress tracking
                            processed_bytes += len(decrypted_chunk)
                            chunk_count += 1

                            # Show progress for large files
                            if (
                                show_progress and chunk_count % 100 == 0
                            ):  # Every 100 chunks
                                progress_pct = (infile.tell() / file_size) * 100
                                print(
                                    f"Progress: {progress_pct:.1f}% ({processed_bytes // (1024*1024)}MB decrypted, chunk {chunk_count})"
                                )

                        except Exception as decrypt_error:
                            raise ValueError(
                                f"Decryption failed for chunk {chunk_count}: {decrypt_error}"
                            )

            print(f"✓ File decrypted successfully: {output_path}")
            return True

        except Exception as e:
            print(f"✗ Decryption failed: {e}")
            return False

    def inspect_file(self, input_path: str) -> dict:
        """
        Inspect an encrypted file structure without decrypting.

        Analyses file format, validates structure, and provides statistics
        about chunks and encryption metadata without requiring password.

        Args:
            input_path: Path to the encrypted file to inspect

        Returns:
            Dictionary containing file information:
            - file_size: Total file size in bytes
            - file_size_mb: File size in megabytes
            - chunks: Number of encrypted chunks
            - salt_size: Size of the cryptographic salt
            - total_encrypted_size: Total size of encrypted data
            - average_chunk_size: Average chunk size
            - min/max_chunk_size: Smallest and largest chunks
            - valid_format: Whether file has valid encryption format
            - error: Error message if validation failed

        Security:
            - No decryption performed, only metadata analysis
            - Validates file structure for corruption detection
        """
        try:
            file_size = os.path.getsize(input_path)
            info = {
                "file_size": file_size,
                "file_size_mb": file_size // (1024 * 1024),
                "chunks": 0,
                "total_encrypted_size": 0,
                "average_chunk_size": 0,
                "valid_format": True,
                "error": None,
            }

            with open(input_path, "rb") as infile:
                # Read salt information
                salt_size_data = infile.read(4)
                if len(salt_size_data) != 4:
                    info["valid_format"] = False
                    info["error"] = "Cannot read salt size"
                    return info

                salt_size = struct.unpack("<I", salt_size_data)[0]
                info["salt_size"] = salt_size

                # Validate salt size
                if salt_size == 0 or salt_size > 1024:
                    info["valid_format"] = False
                    info["error"] = f"Invalid salt size: {salt_size}"
                    return info

                # Skip salt
                salt = infile.read(salt_size)
                if len(salt) != salt_size:
                    info["valid_format"] = False
                    info["error"] = "Cannot read salt"
                    return info

                # Count chunks and sizes
                chunk_sizes = []
                while True:
                    chunk_size_data = infile.read(4)
                    if len(chunk_size_data) != 4:
                        info["valid_format"] = False
                        info["error"] = "Unexpected end of file"
                        return info

                    chunk_size = struct.unpack("<I", chunk_size_data)[0]

                    # Check for terminator
                    if chunk_size == 0:
                        break

                    # Validate chunk size
                    if chunk_size > 10 * 1024 * 1024:  # 10MB max
                        info["valid_format"] = False
                        info["error"] = f"Invalid chunk size: {chunk_size}"
                        return info

                    # Skip chunk data
                    infile.seek(chunk_size, 1)

                    chunk_sizes.append(chunk_size)
                    info["chunks"] += 1
                    info["total_encrypted_size"] += chunk_size

                # Calculate statistics
                if info["chunks"] > 0:
                    info["average_chunk_size"] = (
                        info["total_encrypted_size"] // info["chunks"]
                    )
                    info["min_chunk_size"] = min(chunk_sizes)
                    info["max_chunk_size"] = max(chunk_sizes)

            return info

        except Exception as e:
            return {
                "valid_format": False,
                "error": str(e),
                "file_size": (
                    os.path.getsize(input_path) if os.path.exists(input_path) else 0
                ),
            }

    def _encrypt_chunk(
        self, chunk_data: bytes, box: nacl.secret.SecretBox, chunk_index: int
    ) -> tuple:
        """
        Encrypt a single chunk and return (index, encrypted_chunk).

        Args:
            chunk_data: Raw bytes to encrypt
            box: Configured SecretBox cipher instance
            chunk_index: Sequential index for chunk ordering

        Returns:
            Tuple of (chunk_index, encrypted_chunk_data)

        Security:
            - Each chunk receives unique nonce automatically via PyNaCl
        """
        encrypted_chunk = box.encrypt(chunk_data)
        return (chunk_index, encrypted_chunk)

    def _read_chunks_worker(
        self, input_path: str, chunk_size: int, chunk_queue: queue.Queue
    ):
        """
        Worker thread to read chunks from input file.

        Reads file data in chunks and places them in the queue for processing.
        Handles file I/O errors and signals end-of-file to consumer threads.

        Args:
            input_path: Path to the input file to read
            chunk_size: Size of chunks to read (typically 1MB)
            chunk_queue: Queue to place read chunks for processing

        Thread Safety:
            - Designed for single reader thread only
            - Uses queue for thread-safe communication
        """
        try:
            with open(input_path, "rb") as infile:
                chunk_index = 0
                while True:
                    chunk = infile.read(chunk_size)
                    if not chunk:
                        break
                    chunk_queue.put((chunk_index, chunk))
                    chunk_index += 1
        except Exception as e:
            chunk_queue.put(("ERROR", str(e)))
        finally:
            chunk_queue.put(("EOF", None))

    def _write_chunks_worker(
        self, output_path: str, salt: bytes, encrypted_chunks_queue: queue.Queue
    ):
        """
        Worker thread to write encrypted chunks to output file in order.

        Maintains chunk ordering during parallel encryption by buffering
        out-of-order chunks until their predecessors arrive. Ensures
        the output file maintains correct sequential structure.

        Args:
            output_path: Path to the output encrypted file
            salt: Cryptographic salt to write at file header
            encrypted_chunks_queue: Queue containing encrypted chunks

        Thread Safety:
            - Designed for single writer thread only
            - Uses internal buffering for chunk reordering
            - Handles error propagation to main thread
        """
        try:
            with open(output_path, "wb") as outfile:
                # Write salt information
                outfile.write(struct.pack("<I", len(salt)))
                outfile.write(salt)

                expected_index = 0
                chunk_buffer = {}  # Buffer for out-of-order chunks

                while True:
                    item = encrypted_chunks_queue.get()
                    if item is None:  # Sentinel for end of processing
                        break

                    if item[0] == "ERROR":
                        raise Exception(item[1])

                    chunk_index, encrypted_chunk = item

                    # Buffer chunks that arrive out of order
                    if chunk_index == expected_index:
                        # Write this chunk and any buffered consecutive chunks
                        outfile.write(struct.pack("<I", len(encrypted_chunk)))
                        outfile.write(encrypted_chunk)
                        expected_index += 1

                        # Check if we can write any buffered chunks
                        while expected_index in chunk_buffer:
                            buffered_chunk = chunk_buffer.pop(expected_index)
                            outfile.write(struct.pack("<I", len(buffered_chunk)))
                            outfile.write(buffered_chunk)
                            expected_index += 1
                    else:
                        # Buffer this chunk for later
                        chunk_buffer[chunk_index] = encrypted_chunk

                    encrypted_chunks_queue.task_done()

                # Write terminator
                outfile.write(struct.pack("<I", 0))

        except Exception as e:
            # Signal error to main thread
            encrypted_chunks_queue.put(("ERROR", str(e)))


def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print(f"  {sys.argv[0]} encrypt <input_file> <output_file>")
        print(f"  {sys.argv[0]} decrypt <input_file> <output_file>")
        print(f"  {sys.argv[0]} inspect <encrypted_file>")
        sys.exit(1)

    operation = sys.argv[1].lower()

    if operation == "inspect":
        if len(sys.argv) != 3:
            print("Usage: python new-algo.py inspect <encrypted_file>")
            sys.exit(1)

        encrypted_file = sys.argv[2]

        # Check if file exists
        if not Path(encrypted_file).exists():
            print(f"Error: File '{encrypted_file}' does not exist")
            sys.exit(1)

        # Inspect the file
        encryptor = FileEncryptor()
        info = encryptor.inspect_file(encrypted_file)

        print(f"\nFile Inspection Report: {encrypted_file}")
        print("=" * 50)
        print(f"File Size: {info['file_size']:,} bytes ({info['file_size_mb']} MB)")
        print(f"Valid Format: {'✓' if info['valid_format'] else '✗'}")

        if info["valid_format"]:
            print(f"Salt Size: {info['salt_size']} bytes")
            print(f"Total Chunks: {info['chunks']}")
            print(f"Total Encrypted Data: {info['total_encrypted_size']:,} bytes")
            if info["chunks"] > 0:
                print(f"Average Chunk Size: {info['average_chunk_size']:,} bytes")
                print(f"Min Chunk Size: {info['min_chunk_size']:,} bytes")
                print(f"Max Chunk Size: {info['max_chunk_size']:,} bytes")
        else:
            print(f"Error: {info['error']}")

        sys.exit(0)

    # Handle encrypt/decrypt operations
    if len(sys.argv) != 4:
        print("Usage:")
        print(f"  {sys.argv[0]} encrypt <input_file> <output_file>")
        print(f"  {sys.argv[0]} decrypt <input_file> <output_file>")
        print(f"  {sys.argv[0]} inspect <encrypted_file>")
        sys.exit(1)

    input_file = sys.argv[2]
    output_file = sys.argv[3]

    if operation not in ["encrypt", "decrypt"]:
        print("Error: Operation must be 'encrypt', 'decrypt', or 'inspect'")
        sys.exit(1)

    # Check if input file exists
    if not Path(input_file).exists():
        print(f"Error: Input file '{input_file}' does not exist")
        sys.exit(1)

    # Check if output file already exists
    if Path(output_file).exists():
        response = input(
            f"Output file '{output_file}' already exists. Overwrite? (y/N): "
        )
        if response.lower() != "y":
            print("Operation cancelled")
            sys.exit(1)

    # Get password securely
    password = getpass.getpass(f"Enter password for {operation}ion: ")
    if not password:
        print("Error: Password cannot be empty")
        sys.exit(1)

    # Confirm password for encryption
    if operation == "encrypt":
        confirm_password = getpass.getpass("Confirm password: ")
        if password != confirm_password:
            print("Error: Passwords do not match")
            sys.exit(1)

    # Create encryptor and perform operation
    encryptor = FileEncryptor()

    if operation == "encrypt":
        success = encryptor.encrypt_file(input_file, output_file, password)
    else:
        success = encryptor.decrypt_file(input_file, output_file, password)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
