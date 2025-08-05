## XChaCha20-Poly1305 File Encryption Script

This directory contains a secure file encryption script utilising industry-standard cryptographic algorithms:

-   **XChaCha20-Poly1305** for authenticated encryption with semantic security
-   **Argon2id** for memory-hard key derivation from passwords
-   **PyNaCl** library for high-performance cryptographic operations

### Features

-   ✅ XChaCha20-Poly1305 authenticated encryption with individual nonces per chunk
-   ✅ Argon2id key derivation function (KDF) with secure parameters
-   ✅ Cryptographically secure random salt generation (32 bytes)
-   ✅ Parallel processing for large files with adaptive threading
-   ✅ Streaming format to prevent memory exhaustion
-   ✅ Comprehensive file format validation and corruption detection
-   ✅ Timing attack mitigations in decryption process
-   ✅ Progress tracking for large files (>100MB)
-   ✅ File inspection without decryption for metadata analysis

### Usage

#### Command Line Interface

Encrypt a file:

```bash
python new-algo.py encrypt input.txt encrypted.enc
```

Decrypt a file:

```bash
python new-algo.py decrypt encrypted.enc decrypted.txt
```

Inspect encrypted file metadata:

```bash
python new-algo.py inspect encrypted.enc
```

#### Programmatic Usage

```python
from new_algo import FileEncryptor

encryptor = FileEncryptor()

# Encrypt
success = encryptor.encrypt_file("secret.txt", "secret.enc", "MyPassword123!")

# Decrypt
success = encryptor.decrypt_file("secret.enc", "secret_restored.txt", "MyPassword123!")

# Inspect without decryption
info = encryptor.inspect_file("secret.enc")
print(f"File has {info['chunks']} chunks and is {info['file_size_mb']}MB")
```

### Security Parameters

-   **Salt size**: 32 bytes (256 bits)
-   **Key size**: 32 bytes (256 bits)
-   **Nonce size**: 24 bytes (192 bits) for XChaCha20
-   **Authentication tag**: 16 bytes (128 bits) for Poly1305
-   **Argon2id parameters**:
    -   Time cost: 3 iterations
    -   Memory cost: 64 MB
    -   Parallelism: 1 thread

### Error Handling & Security Features

-   **Input validation**: Comprehensive file format validation before processing
-   **Corruption detection**: Authentication tags verify data integrity
-   **Timing attack mitigation**: Randomised delays during decryption
-   **Memory safety**: Streaming format prevents memory exhaustion attacks
-   **Password security**: Uses `getpass` for secure password input
-   **Thread safety**: Proper synchronisation for parallel processing

### File Format

The encrypted file format uses a streaming design to handle large files efficiently:

```
[4 bytes: salt_size] [salt_size bytes: salt] [chunk_data]... [4 bytes: terminator(0)]
```

Where each chunk follows the format:

```
[4 bytes: chunk_size] [chunk_size bytes: encrypted_data]
```

And `encrypted_data` contains:

-   24-byte nonce (XChaCha20)
-   Ciphertext
-   16-byte authentication tag (Poly1305)

### Performance Characteristics

-   **Small files (<10MB)**: Sequential processing for optimal performance
-   **Large files (≥10MB)**: Parallel processing with worker threads
-   **Memory usage**: Constant memory footprint via streaming (1MB chunks)
-   **Threading**: Adaptive thread count based on CPU cores (max cores - 1)
-   **Progress tracking**: Real-time progress for files >100MB

### Demo

Run the demo to see the encryption in action:

```bash
python demo.py
```

### Dependencies

```bash
pip install cryptography argon2-cffi pynacl
```
