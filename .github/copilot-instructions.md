# AI Coding Agent Instructions

When creating new code or editing existing code, please use Australian English for all comments, documentation, and variable names. If a library or function has a specific spelling convention that is not Australian English, please use the original spelling.

If in `Ask` mode, you must use Australian English for all responses, including code comments and documentation.

When adding code with new libraries, ensure that the libraries are included in the `requirements.txt` file.
If there are libraries that are not included in the `requirements.txt` file, please add them if they are not already present.

## Project Overview

This is a collection of security-focused Python experiments and utilities. The primary themes are cryptography, hashing, authentication, and mathematical algorithms.

## Core Architecture Patterns

### Security-First Approach

-   **Cryptography**: Uses industry-standard libraries (e.g. `argon2-cffi`, `pynacl`) with secure parameters
-   **Password handling**: Always use `getpass.getpass()` for sensitive input, never plain `input()`
-   **Database security**: Obfuscated table/column names (e.g., `As8JS_users`, `c9ujs_uuid`) for security through obscurity
-   **Timing attacks**: Implement decoy delays (e.g. with `time.sleep(random.uniform(0.2, 0.4))`) in authentication flows
-   **Password Hashing/Key-Derivation Functions (KDF)**: Prefer Argon2id over bcrypt for new projects, as it is more secure and configurable
-   **Encryption of Files**: Use the file extension `.enc` for encrypted files, and ensure all files are encrypted with a secure algorithm (e.g. XChaCha20-Poly1305 or AES-GCM)

### Database Conventions

-   **SQLite3**: Primary database engine across projects
-   **Schema validation**: Always validate database structure before operations (see `arg_hashing/pw.py:validate_database_structure()`)
-   **Error handling**: Catch specific SQLite exceptions (`IntegrityError`, `OperationalError`, `DatabaseError`)
-   **UUIDs**: Use `uuid.uuid4()` for primary keys, not auto-incrementing integers

### File Processing Patterns

-   **Chunked processing**: For large files, use 1MB chunks (see `encrypt/new-algo.py:encrypt_file()`)
-   **Binary file format**: Use `struct.pack("<I", value)` for metadata headers (little-endian uint32)
-   **Error resilience**: Always wrap file operations in try-catch blocks with specific error messages

## Key Components

### Encryption Module (`encrypt/`)

-   **Algorithm**: XChaCha20-Poly1305 with Argon2id KDF
-   **File format**: `[salt_size][salt][chunk_count][chunk_size][encrypted_chunk]...`
-   **Security parameters**:
    -   Argon2id: 3 iterations, 64MB memory, 1 thread
    -   Salt: 32 bytes, Nonce: 24 bytes, Key: 32 bytes
-   **CLI interface**: `python new-algo.py encrypt/decrypt <input> <output>`

### Authentication Systems (`B_hashing/`, `arg_hashing/`)

-   **B_hashing**: bcrypt-based with 14 rounds
-   **arg_hashing**: Argon2id-based with environment variable support
-   **Common pattern**: User creation with UUID, username, hashed password, DoB, permissions

### Utilities

-   **Password generation** (`pass/ranWord.py`): Secure random with complexity requirements
-   **Mathematical algorithms** (`collatz/`, `Doomsday Algorithm/`): Pure Python implementations

## Development Workflow

### Dependencies

Install with: `pip install -r requirements.txt`
Key libraries: `cryptography`, `pynacl`, `argon2-cffi`, `bcrypt`, `pyperclip`

### Code Style

-   **Classes**: Use PascalCase, prefer composition over inheritance
-   **Error handling**: Specific exception types with user-friendly messages
-   **Input validation**: Always validate user input with multiple retry attempts
-   **Documentation**: Inline docstrings for cryptographic functions

### Testing Approach

-   **Manual testing**: Most modules include interactive CLI interfaces
-   **Demo scripts**: See `encrypt/test_chunked.py` for example usage patterns
-   **Database testing**: Validate schema before operations

## Security Considerations

-   Never log passwords or sensitive data
-   Use secure random generation (`secrets`, `os.urandom()`)
-   Implement proper key derivation (no plain text storage)
-   Include timing attack mitigations in authentication flows
-   Validate all user inputs with proper error handling

## Common Anti-Patterns to Avoid

-   Don't use `input()` for passwords (use `getpass.getpass()`)
-   Don't hardcode database paths (use relative paths with validation)
-   Don't ignore SQLite-specific exceptions (catch and handle properly)
-   Don't implement custom crypto (use established libraries)
-   Don't skip input validation (always validate with retry logic)
