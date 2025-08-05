from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import argon2
import os
import time
import hashlib


class AESFileEncryptor:
    """AES-256 file encryptor and decryptor using Argon2ID-based key derivation."""

    def __init__(self, parent=None):
        """
        Optionally accept a parent object for integration with GUI frameworks.
        Args:
            parent (object, optional): Parent object, e.g., a QWidget. Defaults to None.
        """
        self.parent = parent

    def _derive_key(self, salt: bytes, password: str) -> bytes:
        """Derive a 256-bit key from the password and salt using Argon2ID."""
        return argon2.low_level.hash_secret_raw(
            secret=password.encode(),
            salt=salt,
            time_cost=20,
            memory_cost=65536,  # 64 MiB
            parallelism=4,
            hash_len=32,
            type=argon2.low_level.Type.ID,
        )

    def _sha3_512_hash(self, filepath: str) -> str:
        """
        Compute the SHA3-512 hash of a file.
        This is done in 4 KiB 'chunks' to handle large files efficiently.
        """
        hasher = hashlib.sha3_512()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def encrypt_file(self, password: str, input_path: str, output_path: str):
        """
        Encrypt a file using AES-256-CBC in chunks, storing salt, IV,
        SHA3-512 hash, then ciphertext.
        """
        if not password:
            raise ValueError("Password must not be empty for encryption.")
        try:
            salt = os.urandom(16)
            key = self._derive_key(salt, password)
            iv = os.urandom(16)
            file_hash = self._sha3_512_hash(input_path)
            print(f"SHA3-512 hash of {input_path} (shortened): {file_hash:.12s}...")
            cipher = Cipher(
                algorithm=algorithms.AES(key),
                mode=modes.CBC(iv),
                backend=default_backend(),
            )
            encryptor = cipher.encryptor()
            padder = padding.PKCS7(128).padder()

            try:
                with open(input_path, "rb") as infile, open(
                    output_path, "wb"
                ) as outfile:
                    # Write salt, IV, and hash first
                    outfile.write(salt + iv + bytes.fromhex(file_hash))
                    chunk_size = 4096
                    finished = False
                    while not finished:
                        chunk = infile.read(chunk_size)
                        if len(chunk) == 0:
                            finished = True
                            # Finalise padding and encryption for the last block
                            padded = padder.finalize()
                            if padded:
                                ciphertext = encryptor.update(padded)
                                outfile.write(ciphertext)
                            outfile.write(encryptor.finalize())
                        else:
                            padded = padder.update(chunk)
                            if padded:
                                ciphertext = encryptor.update(padded)
                                outfile.write(ciphertext)
            except FileNotFoundError:
                raise FileNotFoundError(f"Input file not found: {input_path}")
            except PermissionError:
                raise PermissionError(
                    f"Permission denied when reading or writing: {input_path} or {output_path}"
                )
            except Exception as exc:
                raise IOError(
                    f"Failed to process files: {input_path}, {output_path}"
                ) from exc

        except Exception as exc:
            print(f"Encryption failed: {exc}")
            raise

    def decrypt_file(self, password: str, input_path: str, output_path: str):
        """Decrypt a file previously encrypted with this class in chunks and verify integrity.
        Raises:
            ValueError: If the password is incorrect, the file is corrupted, or the hash does not match.
        """
        if not password:
            raise ValueError("Password must not be empty for decryption.")
        # If file encryption fails and others
        try:
            # if error occurs when reading file
            try:
                with open(input_path, "rb") as infile:
                    salt = infile.read(16)
                    iv = infile.read(16)
                    file_hash_bytes = infile.read(64)
                    if len(salt) != 16 or len(iv) != 16 or len(file_hash_bytes) != 64:
                        raise ValueError(
                            "Encrypted file header is incomplete or corrupted."
                        )
                    key = self._derive_key(salt=salt, password=password)
                    cipher = Cipher(
                        algorithms.AES(key), modes.CBC(iv), backend=default_backend()
                    )
                    decryptor = cipher.decryptor()
                    unpadder = padding.PKCS7(128).unpadder()

                    # Prepare for hash verification
                    hasher = hashlib.sha3_512()

                    buffer = b""
                    chunk_size = 4096
                    try:
                        with open(output_path, "wb") as outf:
                            while True:
                                chunk = infile.read(chunk_size)
                                if not chunk:
                                    break
                                decrypted = decryptor.update(chunk)
                                buffer += decrypted
                                # Only keep the last block in buffer for padding removal
                                while len(buffer) > 16:
                                    outf.write(buffer[:16])
                                    hasher.update(buffer[:16])
                                    buffer = buffer[16:]
                            # Finalise decryption and remove padding
                            buffer += decryptor.finalize()
                            try:
                                unpadded = unpadder.update(buffer) + unpadder.finalize()
                            except ValueError as ve:
                                print(
                                    "Decryption failed: incorrect password or file is corrupted (invalid padding)."
                                )
                                raise ValueError(
                                    "Decryption failed: the password may be incorrect, or the file may be corrupted or tampered with."
                                ) from ve
                            outf.write(unpadded)
                            hasher.update(unpadded)
                    except PermissionError:
                        raise PermissionError(
                            f"Permission denied when writing: {output_path}"
                        )
                    except Exception as exc:
                        # Only wrap non-ValueError exceptions
                        if isinstance(exc, ValueError):
                            raise
                        raise IOError(
                            f"Failed to write output file: {output_path}"
                        ) from exc

                    computed_hash = hasher.digest()
                    print(f"Computed hash (shortened): {computed_hash.hex():.12s}...")
                    if computed_hash == file_hash_bytes:
                        print("File integrity check passed: SHA3-512 hash matches.")
                    else:
                        raise ValueError(
                            "File integrity check failed: SHA3-512 hash does not match."
                        )
            except FileNotFoundError:
                raise FileNotFoundError(f"Encrypted file not found: {input_path}")
            except PermissionError:
                raise PermissionError(f"Permission denied when reading: {input_path}")
            except Exception as exc:
                # Only wrap non-ValueError exceptions
                if isinstance(exc, ValueError):
                    raise
                raise IOError(f"Failed to read encrypted file: {input_path}") from exc

        except ValueError as e:
            print(f"Decryption failed: {e}")
            raise
        except Exception as e:
            print(f"Decryption failed due to an unexpected error: {e}")
            raise RuntimeError(
                "Decryption failed due to an unexpected error. Please check the input files and try again."
            ) from e


if __name__ == "__main__":
    fe = AESFileEncryptor()
    # Remove the encrypted and decrypted files if they exist
    for file_path in [
        r"./pyfiles/.testing/pyinstall_help.txt.enc",
        r"./pyfiles/.testing/pyinstalled_help.txt",
    ]:
        try:
            os.remove(file_path)
            print(f"Removed file: {file_path}")
        except FileNotFoundError:
            print(f"File not found or doesn't exist: {file_path}")
            pass

    # Pause for 500 milliseconds before starting encryption/decryption
    time.sleep(0.5)

    start_encrypt = time.time()
    fe.encrypt_file(
        password=r"safasdfasdfasdfasdfsdfaasdf",
        input_path=r"./pyfiles/.testing/pyinstall_help.txt",
        output_path=r"./pyfiles/.testing/pyinstall_help.txt.enc",
    )
    end_encrypt = time.time()
    print(f"Encryption took {end_encrypt - start_encrypt:.3f} seconds.")

    start_decrypt = time.time()
    fe.decrypt_file(
        password=r"safasdfasdfasdfasdfsdfaasdf",
        input_path=r"./pyfiles/.testing/pyinstall_help.txt.enc",
        output_path=r"./pyfiles/.testing/pyinstalled_help.txt",
    )
    end_decrypt = time.time()
    print(f"Decryption took {end_decrypt - start_decrypt:.3f} seconds.")
