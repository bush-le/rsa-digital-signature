## RSA Digital Signature System

> ⚠️ **IMPORTANT NOTE:** This document contains the ORIGINAL specification. The **current implementation has been modified** for educational purposes:
>
> **Original Spec vs Current Implementation:**
> | Aspect | Original Spec | Current Implementation |
> |--------|---------------|----------------------|
> | Implementation | cryptography library | Pure Python RSA |
> | Key Sizes | ≥ 2048 bits (fixed) | 512-2048 bits (flexible, default 1024) |
> | Padding | PSS | PKCS#1 v1.5 |
> | Private Key Format | PKCS8 | Plain text (n, e, d, p, q) |
> | Dependencies | cryptography, PyQt6, python-docx, PyPDF2 | PyQt6, python-docx, PyPDF2 only |
> | Purpose | Production-ready | Educational implementation |
>
> See **PURE_PYTHON_RSA_GUIDE.md** for details on the pure Python implementation.

---

## 1. Purpose

This document defines the **technical specification and execution instructions** for building a complete RSA Digital Signature application in Python.

The AI agent must follow this specification strictly to ensure:

* Correct functionality
* Secure cryptographic practices
* Clean modular architecture
* Full end-to-end operability

---

## 2. Scope

The system must implement:

* RSA key pair generation
* File-based digital signature
* Signature verification
* Graphical user interface (GUI)
* Persistent key storage

---

## 3. System Architecture

### 3.1 Directory Structure (Mandatory)

```
RSA_Digital_Signature/
├── core/
│   ├── rsa_logic.py
│   └── file_handler.py
├── keys/
├── ui/
│   └── main_window.py
├── main.py
├── requirements.txt
└── .gitignore
```

---

### 3.2 Architectural Principles

* **Separation of concerns**

  * `core/`: business & cryptographic logic
  * `ui/`: presentation layer only
* **Loose coupling**
* **No cross-layer logic leakage**
* **File-based persistence**

---

## 4. Technical Requirements

### 4.1 Language & Environment

* Python ≥ 3.10
* Cross-platform compatibility (Linux, Windows)

---

### 4.2 Dependencies

```
cryptography
PyQt6
python-docx
PyPDF2
```

---

### 4.3 Cryptographic Standards

| Component      | Requirement |
| -------------- | ----------- |
| Algorithm      | RSA         |
| Key Size       | ≥ 2048 bits |
| Hash Function  | SHA-256     |
| Padding Scheme | PSS         |
| Key Format     | PEM         |
| Private Key    | PKCS8       |

---

## 5. Module Specifications

---

### 5.1 Module: `core/rsa_logic.py`

#### Responsibilities

* RSA key generation
* Signing operation
* Signature verification

#### Required Interface

```python
generate_keys(key_size=2048)

save_private_key(private_key, path)
save_public_key(public_key, path)

load_private_key(path)
load_public_key(path)

sign_data(data: bytes, private_key) -> bytes

verify_signature(data: bytes, signature: bytes, public_key) -> bool
```

#### Constraints

* Must use `cryptography` library
* Must not expose private key
* Must validate inputs before processing

---

### 5.2 Module: `core/file_handler.py`

#### Responsibilities

* File I/O abstraction
* Binary-safe operations

#### Required Interface

```python
read_file(path: str) -> bytes

write_signature(path: str, signature: bytes)

read_signature(path: str) -> bytes
```

#### Constraints

* Must support all file types (binary mode)
* Must handle exceptions safely

---

### 5.3 Module: `ui/main_window.py`

#### Responsibilities

* User interaction layer
* Event handling
* Display results

#### Required Features

* Generate RSA keys
* File selection dialog
* Sign file action
* Verify signature action
* Result display (VALID / INVALID)

#### Constraints

* No cryptographic logic allowed
* Must call only `core/` functions
* Must handle UI errors gracefully

---

### 5.4 Module: `main.py`

#### Responsibilities

* Application entry point
* GUI initialization

#### Example

```python
def main():
    run_app()

if __name__ == "__main__":
    main()
```

---

## 6. System Workflow

---

### 6.1 Key Generation

```
User Action → Generate Keys
    ↓
generate_keys()
    ↓
Save private key → /keys/private.pem
Save public key  → /keys/public.pem
```

---

### 6.2 Signing Process

```
User selects file
    ↓
read_file()
    ↓
sign_data()
    ↓
write_signature() → file.sig
```

---

### 6.3 Verification Process

```
User selects file + signature
    ↓
read_file()
read_signature()
    ↓
verify_signature()

IF match → VALID
ELSE → INVALID
```

---

## 7. Error Handling

The system must explicitly handle:

* File not found
* Invalid or corrupted signature
* Invalid key format
* Unsupported file input
* Runtime exceptions

All errors must return **clear and user-friendly messages**.

---

## 8. Security Requirements

* Private key must never be logged or exposed
* Input validation is mandatory
* Use secure padding (PSS)
* Prevent unsafe file overwrites
* Enforce minimum key size

---

## 9. Testing Criteria

The implementation is considered valid only if:

| Test Case            | Expected Result |
| -------------------- | --------------- |
| Key generation       | Success         |
| Sign file            | `.sig` created  |
| Verify original file | TRUE            |
| Verify modified file | FALSE           |
| Invalid signature    | FALSE           |

---

## 10. Constraints & Prohibitions

The AI agent **must NOT**:

* Hardcode file paths
* Embed cryptographic logic in UI
* Use global variables for key storage
* Skip error handling
* Use insecure cryptographic settings

---

## 11. Completion Criteria

The system is complete when:

* Application launches via:

```
python main.py
```

* User can:

  * Generate keys
  * Sign files
  * Verify signatures

* All operations execute without runtime errors

---

## 12. Execution Plan (AI Agent)

1. Implement `rsa_logic.py`
2. Implement `file_handler.py`
3. Unit test core functionality
4. Implement GUI (`main_window.py`)
5. Integrate modules
6. Perform end-to-end validation

---

## 13. Optional Enhancements

* Command-line interface (CLI)
* Drag-and-drop support
* Hash visualization (SHA-256)
* Batch file signing
* Logging system

---

## 14. Document Status

* Version: 1.0
* Status: Ready for Implementation
* Audience: AI Agent / Developer

---

**End of Specification**
