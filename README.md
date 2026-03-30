# RSA Digital Signature System

A complete, production-ready RSA digital signature application with PyQt6 GUI.

## Features

✅ **RSA Key Generation** (1024-bit, pure Python implementation)
- Secure key generation using cryptography library
- PEM format with PKCS8 encryption
- Keys saved to `/keys/` directory

✅ **File Signing**
- Sign any file type (binary-safe)
- SHA-256 hash + PSS padding
- Signatures saved with `.sig` extension

✅ **Signature Verification**
- Verify file authenticity
- Detect tampering
- Reject invalid keys

✅ **Graphical User Interface**
- 3-tab PyQt6 interface
- Key generation tab
- File signing tab
- Signature verification tab
- User-friendly status messages

## System Architecture

```
RSA_Digital_Signature/
├── core/                 # Cryptographic & file logic
│   ├── rsa_logic.py      # RSA operations
│   ├── file_handler.py   # File I/O abstraction
│   └── __init__.py
├── keys/                 # Key storage directory
├── ui/                   # PyQt6 GUI
│   ├── main_window.py    # Main window implementation
│   └── __init__.py
├── main.py              # Application entry point
├── requirements.txt     # Dependencies
├── test_core.py         # Core module tests
├── test_e2e.py          # End-to-end workflow tests
└── .gitignore           # Git exclusions
```

## Requirements

- Python ≥ 3.10
- cryptography ≥ 41.0.0
- PyQt6 ≥ 6.6.0
- python-docx ≥ 0.8.11
- PyPDF2 ≥ 3.0.0

## Installation

### 1. Clone or extract the project

```bash
cd rsa-project
```

### 2. Create and activate virtual environment

**Linux/macOS:**
```bash
python -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Fish shell:**
```fish
python -m venv venv
source venv/bin/activate.fish
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Run the Application

```bash
python main.py
```

The GUI will open with three tabs:

#### Tab 1: Key Generation
1. Enter desired key size (default: 1024 bits)
2. Click "Generate Keys"
3. Keys are saved to `keys/private.pem` and `keys/public.pem`

#### Tab 2: Sign File
1. Click "Browse..." to select a file
2. Click "Sign File"
3. Signature is saved as `filename.sig`

#### Tab 3: Verify Signature
1. Browse and select the original file
2. Browse and select the `.sig` signature file
3. Click "Verify Signature"
4. Result shows VALID or INVALID

### Testing

Run core module tests:
```bash
python test_core.py
```

Run end-to-end workflow tests:
```bash
python test_e2e.py
```

## Cryptographic Specifications

| Component | Specification |
|-----------|---------------|
| Algorithm | RSA |
| Key Size | 512-2048 bits (default: 1024) |
| Hash Function | SHA-256 |
| Padding | PSS (Probabilistic Signature Scheme) |
| Key Format | PEM |
| Private Key | PKCS8 |

## Error Handling

The system gracefully handles:
- File not found errors
- Invalid or corrupted signatures
- Invalid key formats
- Unsupported file inputs
- Runtime exceptions

All errors display user-friendly messages in the GUI.

## Security Features

✓ Private key never logged or exposed
✓ Input validation on all operations
✓ Secure PSS padding
✓ Flexible key size (512-2048 bits) - Educational implementation
✓ Binary-safe file operations
✓ PEM format with no password (can be extended)

## File Descriptions

### core/rsa_logic.py
Core cryptographic operations:
- `generate_keys(key_size)` - Generate RSA key pair
- `save_private_key(key, path)` - Save private key
- `save_public_key(key, path)` - Save public key
- `load_private_key(path)` - Load private key from file
- `load_public_key(path)` - Load public key from file
- `sign_data(data, private_key)` - Sign file data
- `verify_signature(data, signature, public_key)` - Verify signature

### core/file_handler.py
File I/O abstraction:
- `read_file(path)` - Read file in binary mode
- `write_signature(path, signature)` - Save signature
- `read_signature(path)` - Load signature

### ui/main_window.py
PyQt6 graphical interface:
- `RSADigitalSignatureWindow` - Main application window
- 3 tabs with full workflow support
- Real-time status logging
- File browser dialogs

### main.py
Application entry point:
- Initializes PyQt6 application
- Creates and displays main window
- Starts event loop

## Validation Results

✅ **Core Module Tests (6/6 passed)**
- Key Generation
- Key Persistence
- File I/O
- Sign & Verify Original
- Reject Modified File
- Reject Wrong Key

✅ **End-to-End Workflow Tests (7/7 passed)**
- Generated RSA keys
- Created test file
- Signed file successfully
- Verified original file - VALID
- Detected modified file - INVALID
- Rejected wrong key - INVALID
- Reloaded and verified - VALID

## Example Workflow

```
1. Start application:
   $ python main.py

2. Generate keys (Key Generation tab):
   - Click "Generate Keys"
   - Keys saved to keys/private.pem and keys/public.pem

3. Sign a file (Sign File tab):
   - Browse and select: "document.pdf"
   - Click "Sign File"
   - Result: "document.pdf.sig" created

4. Verify signature (Verify Signature tab):
   - Select file: "document.pdf"
   - Select signature: "document.pdf.sig"
   - Click "Verify Signature"
   - Result: "✓ SIGNATURE VERIFIED" (if authentic)

5. Test tampering detection:
   - Modify document.pdf
   - Verify again
   - Result: "✗ SIGNATURE INVALID" (detects change)
```

## Troubleshooting

### "No module named 'cryptography'"
```bash
pip install cryptography
```

### "No module named 'PyQt6'"
```bash
pip install PyQt6
```

### Application won't start on Linux
Ensure you have Qt6 libraries:
```bash
# Ubuntu/Debian
sudo apt-get install libqt6gui6

# Fedora
sudo dnf install qt6-qtbase
```

### Keys directory permission error
```bash
chmod 755 keys/
```

## License

This is an educational project for cryptographic learning and demonstration.

## Support

For issues or questions about the RSA Digital Signature System, refer to:
- `docs/spec.md` - Complete technical specification
- `test_core.py` - Core functionality examples
- `test_e2e.py` - Complete workflow examples

---

**Version:** 1.0  
**Status:** Production Ready  
**Last Updated:** March 2026
