# RSA Digital Signature System - Complete Documentation

**For:** Beginner to Intermediate Developers  
**Level:** B1-B2 English  
**Version:** 1.0  
**Date:** March 2026

---

## Table of Contents

1. [What is This Project?](#what-is-this-project)
2. [Overall Architecture](#overall-architecture)
3. [Folder Structure](#folder-structure)
4. [File Explanations](#file-explanations)
5. [How Components Work Together](#how-components-work-together)
6. [Detailed Workflows](#detailed-workflows)
7. [Cryptographic Concepts (Simple)](#cryptographic-concepts-simple)
8. [Common Questions](#common-questions)

---

## What is This Project?

This is a **digital signature application**. It allows you to:

1. **Create secure keys** for signing documents
2. **Sign files** to prove they come from you
3. **Verify signatures** to check if a file is authentic

Think of it like this:
- **Keys** = Your digital identity
- **Signature** = A mark that proves you created a document
- **Verification** = Checking that the document hasn't been changed

**Example:** You send a contract to someone. You sign it digitally. The person can verify that:
- The contract came from you (not someone pretending to be you)
- The contract hasn't been changed since you signed it

---

## Overall Architecture

This project has **three main parts**:

```
┌─────────────────────────────────────────────────┐
│                  USER (You)                      │
│            (Using the GUI Application)           │
└────────────────────┬────────────────────────────┘
                     │
          ┌──────────▼──────────┐
          │   UI LAYER (PyQt6)  │
          │  (main_window.py)   │
          │  - Buttons          │
          │  - File dialogs      │
          │  - Status messages   │
          └──────────┬──────────┘
                     │
          ┌──────────▼──────────┐
          │   CORE LOGIC LAYER  │
          │ ┌──────────────────┐ │
          │ │ rsa_logic.py     │ │ ← Crypto operations
          │ │ file_handler.py  │ │ ← File I/O
          │ └──────────────────┘ │
          └──────────┬──────────┘
                     │
          ┌──────────▼──────────┐
          │   DATA STORAGE      │
          │ - keys/ (files)     │
          │ - .sig files        │
          └─────────────────────┘
```

**How it works:**
1. You use the **GUI** (what you see on screen)
2. The GUI calls **core logic** (crypto operations)
3. Core logic **reads/writes files** and stores keys

---

## Folder Structure

### 📁 `core/`
**Purpose:** The brain of the application. All cryptography and file operations happen here.

**Contains:**
- `rsa_logic.py` → RSA encryption/signing code
- `file_handler.py` → File reading/writing code
- `__init__.py` → Makes this a Python module

**Do not modify:** Unless you understand cryptography!

---

### 📁 `ui/`
**Purpose:** What you see on your screen. The graphical interface.

**Contains:**
- `main_window.py` → The application window (3 tabs)
- `__init__.py` → Makes this a Python module

**What it does:**
- Shows buttons and text boxes
- Opens file dialogs
- Displays results to the user
- **Does NOT do cryptography** (that's in `core/`)

---

### 📁 `keys/`
**Purpose:** Stores your RSA keys (secret files).

**Contains:**
- `private.pem` → Your secret key (keep this safe!)
- `public.pem` → Your public key (can share this)

**Important:** These files are created when you click "Generate Keys" in the app.

---

### 📄 `main.py`
**Purpose:** Starts the application.

**What it does:**
```
main.py
  ↓
Creates a PyQt6 application
  ↓
Shows the main window
  ↓
User interacts with GUI
```

When you run `python main.py`, this file loads the GUI and starts the app.

---

### 📄 `requirements.txt`
**Purpose:** Lists all libraries the project needs.

Contains:
- `PyQt6` → For the GUI
- `python-docx` → For document handling (optional)
- `PyPDF2` → For PDF handling (optional)

**Note:** No `cryptography` library needed - This project uses Pure Python RSA implementation!

---

### 📄 `.gitignore`
**Purpose:** Tells Git which files NOT to save.

Why? Because:
- **Keys should never be stored in Git** (security risk)
- Test files and temporary files aren't needed

---

## File Explanations

### 📝 `core/rsa_logic.py`

#### **Purpose**
Handles all RSA cryptographic operations. This is where the "magic" happens.

#### **Main Functions**

**1. `generate_keys(key_size=1024)`**
```
What it does: Creates a new RSA key pair
Input: key_size (512, 1024, 1536, or 2048 bits) - Educational implementation
Output: (private_key, public_key)

Why 1024 bits? → Educational implementation. For production, use 2048+ bits
```

**2. `save_private_key(private_key, path)` & `save_public_key(public_key, path)`**
```
What they do: Save keys to files
Input: key object + file path
Output: Creates .pem files on disk
```

**3. `load_private_key(path)` & `load_public_key(path)`**
```
What they do: Read keys from files
Input: file path
Output: key object (ready to use)
```

**4. `sign_data(data: bytes, private_key)`**
```
What it does: Create a digital signature
Input: file data + private key
Output: signature (256 bytes)

Process:
  1. Computer reads the file
  2. Creates a hash (fingerprint) of the file
  3. Uses private key to "encrypt" the hash
  4. This encrypted hash = signature
```

**5. `verify_signature(data: bytes, signature: bytes, public_key)`**
```
What it does: Check if a signature is valid
Input: file data + signature + public key
Output: True (valid) or False (invalid)

Process:
  1. Computer creates a hash of the file
  2. Uses public key to "decrypt" the signature
  3. Compares the two hashes
  4. If they match → signature is valid
```

#### **How it Works Internally**

**Simplified explanation:**

```
RSA uses a pair of keys:
  - Private key (secret) → Only you have it
  - Public key (shared) → Anyone can have it

Think of it like a mailbox:
  - Private key = You have the only key to your mailbox
  - Public key = Anyone can put mail in your mailbox
  - Only you can open it with your private key

For signing:
  1. You use your PRIVATE key → Creates a signature
  2. Others use your PUBLIC key → Verifies the signature
  3. This proves you created the signature
```

**In this project:**
- Uses **SHA-256** to create a file hash (fingerprint)
- Uses **PKCS#1 v1.5 padding** for signature security (pure Python implementation)
- Keys are **1024-bit default** (512-2048 bits flexible, educational implementation)

---

### 📝 `core/file_handler.py`

#### **Purpose**
Handles all file reading and writing safely. Separates file operations from cryptography.

#### **Main Functions**

**1. `read_file(path: str) -> bytes`**
```
What it does: Reads a file from disk
Input: file path
Output: file contents as bytes

Example:
  data = read_file("document.pdf")
  # Now data contains all the bytes from the file

Why bytes? → Works with any file type (images, PDFs, text, etc.)
```

**2. `write_signature(path: str, signature: bytes)`**
```
What it does: Saves a signature to a file
Input: file path + signature data
Output: Creates a .sig file

Example:
  write_signature("document.pdf.sig", signature_data)
  # Creates "document.pdf.sig" file
```

**3. `read_signature(path: str) -> bytes`**
```
What it does: Reads a signature file
Input: file path
Output: signature data

Example:
  sig = read_signature("document.pdf.sig")
  # Now sig contains the signature bytes
```

#### **How it Works Internally**

```
File handling is simple:
  1. Opens a file in "binary mode" (works with any file type)
  2. Reads all data
  3. Returns it as bytes
  4. Checks for errors (file not found, permission denied, etc.)
  5. Shows friendly error messages
```

**Why separate from RSA logic?**
- Keeps code clean and organized
- Easy to maintain
- Easy to change file handling without touching cryptography

---

### 📝 `ui/main_window.py`

#### **Purpose**
Creates the graphical user interface (GUI). This is what you see when you run the app.

#### **Main Class: `RSADigitalSignatureWindow`**

This class manages the entire window with 3 tabs:

**Tab 1: Key Generation**
```
┌─────────────────────────────┐
│ Generate Keys Button        │
├─────────────────────────────┤
│ Status Display Area         │
│ (Shows what's happening)    │
└─────────────────────────────┘

When you click "Generate Keys":
  1. GUI calls: generate_keys(1024)  # Educational implementation
  2. Waits for result
  3. Shows status messages
  4. If success → shows "Keys generated!"
  5. If error → shows error message
```

**Tab 2: Sign File**
```
┌─────────────────────────────┐
│ Browse Button (select file) │
├─────────────────────────────┤
│ Sign File Button            │
├─────────────────────────────┤
│ Status Display Area         │
└─────────────────────────────┘

When you click "Sign File":
  1. Opens file dialog
  2. Loads your private key
  3. Reads the file
  4. Calls sign_data()
  5. Saves signature as "filename.sig"
  6. Shows status
```

**Tab 3: Verify Signature**
```
┌─────────────────────────────┐
│ Browse Original File        │
├─────────────────────────────┤
│ Browse Signature File (.sig)│
├─────────────────────────────┤
│ Verify Button               │
├─────────────────────────────┤
│ Result Display Area         │
│ (Green = Valid / Red = Bad) │
└─────────────────────────────┘

When you click "Verify Signature":
  1. Loads your public key
  2. Reads the file
  3. Reads the signature
  4. Calls verify_signature()
  5. Shows result (VALID or INVALID)
```

#### **How UI Interacts with Core Logic**

```
User clicks button
        ↓
GUI (main_window.py) gets the click
        ↓
GUI calls core functions:
  - generate_keys()
  - sign_data()
  - verify_signature()
  - read_file()
  - write_signature()
        ↓
Core returns result
        ↓
GUI displays result to user
```

**Important rule:** The GUI **never does cryptography itself**. It only:
- Gets user input
- Calls core functions
- Shows results

---

### 📝 `main.py`

#### **Purpose**
The entry point. Starts the application.

#### **What it Does**

```python
def main():
    # 1. Create a PyQt6 application
    app = QApplication(sys.argv)
    
    # 2. Set the app style to 'Fusion' (looks good)
    app.setStyle('Fusion')
    
    # 3. Create the main window
    window = RSADigitalSignatureWindow()
    
    # 4. Show the window
    window.show()
    
    # 5. Start the event loop (wait for user clicks)
    sys.exit(app.exec())
```

**In simple terms:**
```
main.py
  └─→ Creates app
      └─→ Creates window
          └─→ Shows window
              └─→ Waits for user input
                  └─→ User clicks buttons
                      └─→ GUI responds
                          └─→ User closes app
                              └─→ Exit
```

---

## How Components Work Together

### **The Complete Flow**

```
┌──────────────────────────────────────────────────────────────┐
│ YOU (User)                                                   │
└──────────────────────┬───────────────────────────────────────┘
                       │ Click "Generate Keys"
                       ↓
┌──────────────────────────────────────────────────────────────┐
│ GUI (main_window.py)                                         │
│  - Gets user input                                           │
│  - Shows file dialogs                                        │
│  - Displays status messages                                  │
└──────────────────────┬───────────────────────────────────────┘
                       │ Call: generate_keys()
                       ↓                      │ Call: save_keys()
                       ↓                      ↓
┌──────────────────────────────────────────────────────────────┐
│ CORE LOGIC (core/rsa_logic.py + file_handler.py)            │
│  - Generates RSA keys                                        │
│  - Signs files                                               │
│  - Verifies signatures                                       │
│  - Reads/writes files                                        │
└──────────────────────┬───────────────────────────────────────┘
                       │ Return result
                       ↓
┌──────────────────────────────────────────────────────────────┐
│ GUI (main_window.py)                                         │
│  - Receives result from core                                 │
│  - Displays "Success" or error message                       │
└──────────────────────┬───────────────────────────────────────┘
                       │ Show on screen
                       ↓
┌──────────────────────────────────────────────────────────────┐
│ YOU (User)                                                   │
│  - See the result                                            │
│  - Continue using the app                                    │
└──────────────────────────────────────────────────────────────┘
```

### **Key Properties of This Design**

**1. Separation of Concerns**
- GUI only handles user interaction
- Core handles cryptography
- File handler handles files
- Each part has one job

**2. No Mixing of Responsibilities**
```
✓ Correct:     GUI → Core → File Handler
✗ Incorrect:   GUI does cryptography
✗ Incorrect:   Core shows error dialogs
```

**3. Easy to Maintain**
- Want to change GUI? Edit `ui/main_window.py`
- Want to change crypto? Edit `core/rsa_logic.py`
- Want to change file handling? Edit `core/file_handler.py`
- They don't interfere with each other

---

## Detailed Workflows

### **Workflow 1: Key Generation**

#### **What Happens (User Perspective)**
```
1. Open application
2. Go to "Key Generation" tab
3. Enter key size (default: 1024)
4. Click "Generate Keys"
5. Wait 5-10 seconds
6. See "Keys generated successfully!"
7. Keys are ready for signing
```

#### **What Happens (Technical)**

```
STEP 1: User clicks "Generate Keys"
         │
         └→ GUI calls: generate_keys(1024)  # Pure Python RSA
                │
                └→ core/rsa_logic.py receives request
                       │
                       └→ Generates prime numbers (p, q)
                           │
                           └→ Computes modulus n = p × q
                               │
                               └→ Creates private key (d secret)
                               │
                               └→ Creates public key (e, n public)
                                   │
                                   └→ Returns both keys
                                       │
STEP 2: GUI receives keys
         │
         └→ GUI calls: save_private_key(private, "keys/private.pem")
                │
                └→ core/file_handler.py writes to disk
                │
         └→ GUI calls: save_public_key(public, "keys/public.pem")
                │
                └→ core/file_handler.py writes to disk
                    │
STEP 3: GUI shows success message
         │
         └→ User sees: "Keys saved to keys/private.pem and keys/public.pem"
         └→ User sees: "Ready to sign and verify files"
```

#### **File Creation**

After this workflow, two files are created:

**`keys/private.pem`** (Keep secret!)
```
-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDi+...
... (many lines of encoded key data)
-----END PRIVATE KEY-----
```

**`keys/public.pem`** (Can share)
```
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA4vjz...
... (many lines of encoded key data)
-----END PUBLIC KEY-----
```

---

### **Workflow 2: Signing a File**

#### **What Happens (User Perspective)**
```
1. Click "Sign File" tab
2. Click "Browse..." and select a file (e.g., contract.pdf)
3. Click "Sign File"
4. Wait 1-2 seconds
5. See "File signed successfully!"
6. See "Signature saved to: contract.pdf.sig"
```

#### **What Happens (Technical)**

```
STEP 1: User selects file and clicks "Sign File"
         │
         └→ GUI gets file path: "contract.pdf"
         └→ GUI calls: load_private_key("keys/private.pem")
                │
                └→ core reads private key from disk
                    │
STEP 2: GUI calls: read_file("contract.pdf")
         │
         └→ core reads file as bytes
         └→ Returns: b'\x25\x50\x44...' (entire file)
                │
STEP 3: GUI calls: sign_data(file_bytes, private_key)
         │
         └→ core/rsa_logic.py:
                │
                ├→ Step 1: Hash the file with SHA-256
                │           Result: file_hash (32 bytes)
                │
                ├→ Step 2: "Encrypt" hash with private key
                │           Result: signature (256 bytes)
                │           This proves YOU created it
                │
                └→ Returns: signature bytes
                │
STEP 4: GUI calls: write_signature("contract.pdf.sig", signature)
         │
         └→ core saves signature to disk as binary file
                │
STEP 5: GUI shows success message
         │
         └→ User sees: "Signature saved to: contract.pdf.sig"
```

#### **Files Created**

After this workflow:

**`contract.pdf`** (original file - unchanged)
```
The file stays exactly the same
```

**`contract.pdf.sig`** (signature file - new)
```
Binary file containing the digital signature
Size: 256 bytes
Mathematically connected to contract.pdf
```

---

### **Workflow 3: Verifying a Signature**

#### **What Happens (User Perspective)**
```
1. Click "Verify Signature" tab
2. Browse and select original file: "contract.pdf"
3. Browse and select signature file: "contract.pdf.sig"
4. Click "Verify Signature"
5. Result: Either
   - ✓ SIGNATURE VERIFIED (green)
   - ✗ SIGNATURE INVALID (red)
```

#### **What Happens (Technical)**

```
STEP 1: User selects both files and clicks "Verify"
         │
         └→ GUI gets:
            - File path: "contract.pdf"
            - Signature path: "contract.pdf.sig"
         └→ GUI calls: load_public_key("keys/public.pem")
                │
                └→ core reads public key from disk
                │
STEP 2: GUI calls: read_file("contract.pdf")
         │
         └→ core reads contract as bytes
         │
STEP 3: GUI calls: read_signature("contract.pdf.sig")
         │
         └→ core reads signature as bytes
                │
STEP 4: GUI calls: verify_signature(file_bytes, sig_bytes, public_key)
         │
         └→ core/rsa_logic.py:
                │
                ├→ Step 1: Hash the file with SHA-256
                │           Result: current_hash
                │
                ├→ Step 2: "Decrypt" signature with public key
                │           Result: original_hash
                │           (This is the hash from when it was signed)
                │
                ├→ Step 3: Compare hashes
                │
                └→ If current_hash == original_hash:
                   │  → Return True (signature is valid)
                   │  → File hasn't been changed
                   │  → Signature is authentic
                   │
                   Else:
                   │  → Return False (signature is invalid)
                   │  → File was changed
                   │  → OR wrong public key
                   │  → OR fake signature
                │
STEP 5: GUI receives result
         │
         └→ If True:  Display "✓ SIGNATURE VERIFIED"
                             (green background)
                             "File is authentic and has not been tampered."
           │
           └→ If False: Display "✗ SIGNATURE INVALID"
                             (red background)
                             "File has been modified or wrong public key used."
```

#### **Three Possible Scenarios**

**Scenario 1: Valid Signature (File unchanged)**
```
contract.pdf (unchanged)
contract.pdf.sig (original signature)
public.pem
         ↓
    Verification
         ↓
    Result: ✓ VALID
```

**Scenario 2: Invalid Signature (File modified)**
```
contract.pdf (modified - text changed)
contract.pdf.sig (original signature)
public.pem
         ↓
    Verification fails because:
    - File hash is different now
    - But signature hash (from signing) is the same
         ↓
    Result: ✗ INVALID
```

**Scenario 3: Invalid Signature (Wrong key)**
```
contract.pdf (unchanged)
contract.pdf.sig (signed with different key)
public.pem (from a different key pair)
         ↓
    Verification fails because:
    - Public key cannot decrypt the signature
    - Because signature was made with different private key
         ↓
    Result: ✗ INVALID
```

---

## Cryptographic Concepts (Simple)

### **What is Cryptography?**

Cryptography is the science of protecting information using mathematics. This project uses **RSA cryptography**.

### **RSA Explained Simply**

**Imagine this scenario:**
```
Alice wants to send a secret message to Bob.

Without RSA:
Alice: "Here's my password: 12345"
Hacker intercepts: "Got password! 12345"
Result: ✗ Message stolen

With RSA:
Alice uses Bob's public key to "lock" the message
Hacker intercepts locked message: "!@#$%^&*()"
Hacker tries to read: "Gibberish, can't read it"
Result: ✓ Message safe

Only Bob has the private key to "unlock" it
Bob uses private key to "unlock"
Bob reads: "Here's my password: 12345"
```

### **RSA With Digital Signatures**

**The purpose:** Prove you created a document without everyone seeing your private key.

```
Normal locking (encryption):
  Public key (lock) → Everyone has it
  Private key (unlock) → Only you have it

Digital signatures (opposite):
  Private key (sign) → Only you use it
  Public key (verify) → Everyone uses it

How it works:
  1. You "sign" a document with your PRIVATE key
  2. Anyone can "verify" with your PUBLIC key
  3. This proves YOU signed it (only you have private key)
  4. Changes to document = signature breaks
```

### **The Hash (Fingerprint)**

Before signing, we create a "fingerprint" called a **hash**.

```
SHA-256 hash:
  Document:  "The price is $100"
  Hash:      9f86d081884c7d6d9f... (256 bits)

     vs

  Document:  "The price is $999"
  Hash:      3ba8e75c8d8e887b2... (different!)

Even tiny change = completely different hash
```

**Why use hash?**
- File could be huge (10 MB)
- Hash is always 32 bytes
- Much faster to sign and verify
- If hash matches, file hasn't changed

---

## Common Questions

### **Q1: Where are my keys stored?**

**Answer:** In the `keys/` folder.

```
keys/
  ├─ private.pem  (your secret key)
  └─ public.pem   (you can share this)
```

**Important:** Keep `private.pem` secret! If someone has it, they can fake your signatures.

---

### **Q2: What if I lose my private key?**

**Answer:** You can't recover it. You must generate new keys.

This is by design for security. Generate new keys:
1. Go to "Key Generation" tab
2. Click "Generate Keys"
3. This overwrites old keys with new keys
4. Old signatures become useless

---

### **Q3: Can I share my public key?**

**Answer:** Yes! Share it freely.

**Why?** People need it to verify your signatures. Without your public key, they can't verify.

**How?** Send them the file `keys/public.pem`.

---

### **Q4: What if someone changes a file after I sign it?**

**Answer:** Verification will fail (signature becomes invalid).

```
Original:   "The contract cost is $1000"
            Sign → signature123

After:      "The contract cost is $10000"
            Verify with signature123 → INVALID!

The system detects the change.
```

---

### **Q5: How secure is this?**

**Answer:** This is an educational pure Python implementation. Security depends on key size:

Current implementation (2026):
- 512-1024 bit RSA: Educational demonstration (not for production) ✓
- 2048-bit RSA: Secure for most purposes (production-ready) ✓
- 4096-bit RSA: Extra secure (takes much longer to generate) ✓

---

### **Q6: How long does signing take?**

**Answer:** Usually 1-5 seconds (depends on file size and key size).

```
File size → Time
100 bytes → < 1 second
1 MB → 2-3 seconds
100 MB → 5-10 seconds
```

RSA is slower than other methods, but very secure.

---

### **Q7: What is the .sig file?**

**Answer:** Your signature stored in a file.

```
document.pdf     ← Original file
document.pdf.sig ← Signature (binary file)

To verify, you need both:
- Original file (document.pdf)
- Signature file (document.pdf.sig)
- Public key (keys/public.pem)
```

---

### **Q8: Can I sign multiple files with one key?**

**Answer:** Yes! Generate keys once, sign many files.

```
Generate Keys (once)
  ↓
keys/private.pem created

Sign file 1.pdf
  ↓
file1.pdf.sig created

Sign file 2.pdf
  ↓
file2.pdf.sig created

Sign file 3.pdf
  ↓
file3.pdf.sig created

Use same private key for all
```

---

### **Q9: What if I try to verify with the wrong public key?**

**Answer:** Verification fails (signature becomes invalid).

```
File signed with Alice's private.pem
Verify with Bob's public.pem
Result: ✗ INVALID

Only works with matching keys.
```

---

### **Q10: How do I delete a key?**

**Answer:** Delete the file from the `keys/` folder.

**Warning:** 
- Deleting `private.pem` → You can't sign new files
- Deleting `public.pem` → You can't verify signatures

If you accidentally delete, generate new keys.

---

### **Q11: What's the difference between private and public key?**

**Answer:**

| Property | Private Key | Public Key |
|----------|-------------|-----------|
| What is it | Secret number | Known number |
| Who has it | Only you | Everyone |
| Used for | Signing | Verifying |
| If stolen | Very bad | No problem |
| File name | private.pem | public.pem |

Think of it like:
- Private key = How you write your signature
- Public key = How people recognize your signature

---

### **Q12: Can you reverse-engineer a signature to get the file?**

**Answer:** No. Signatures are one-way.

```
File → Sign → Signature (one-way, can't go back)
File ← ? ← Signature (impossible)

Signature only proves authenticity, not encryption.
```

---

## Running the Application

### **Step 1: Open Terminal**

```bash
cd rsa-project
```

### **Step 2: Activate Virtual Environment**

**Linux/Mac (Bash/Zsh):**
```bash
source venv/bin/activate
```

**Fish Shell:**
```fish
source venv/bin/activate.fish
```

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

### **Step 3: Start Application**

```bash
python main.py
```

The GUI window should appear.

### **Step 4: Use the Application**

1. **Tab 1 - Key Generation:**
   - Click "Generate Keys"
   - Wait for completion
   
2. **Tab 2 - Sign File:**
   - Click Browse to select a file
   - Click "Sign File"
   
3. **Tab 3 - Verify Signature:**
   - Select the file
   - Select the .sig signature file
   - Click "Verify Signature"

---

## Summary

### **What You Learned**

1. **Architecture:** 3-layer design (GUI → Core → Files)
2. **Components:** Each module has one responsibility
3. **Workflow:** How signing and verification work
4. **Security:** Why RSA is secure
5. **Files:** What each file does

### **Key Takeaways**

```
✓ This app creates digital signatures
✓ Uses RSA cryptography (secure)
✓ GUI is separate from crypto logic
✓ Private key must stay secret
✓ Public key can be shared
✓ Signatures prove authenticity
✓ Signatures detect tampering
```

### **Next Steps**

- Run the application: `python main.py`
- Generate keys
- Sign a test file
- Verify the signature
- Try modifying the file and verify again (should fail)

---

## Glossary

| Term | Meaning |
|------|---------|
| **RSA** | Rivest-Shamir-Adleman (encryption algorithm) |
| **Key** | Secret number used for signing/verifying |
| **Signature** | Proof of authenticity (256 bytes) |
| **Hash** | Fingerprint of a file (32 bytes with SHA-256) |
| **Private Key** | Secret key (only you have it) |
| **Public Key** | Shared key (everyone can have it) |
| **PEM** | Text format for storing keys |
| **PKCS8** | Standard format for private keys |
| **Tamper** | Unauthorized change to a file |
| **Verification** | Checking if a signature is valid |
| **GUI** | Graphical User Interface (what you see) |
| **Core** | Main logic (calculations) |
| **Bytes** | Basic unit of computer data |

---

## Document Information

**Created:** 2026-03-19  
**Level:** Beginner to Intermediate (B1-B2)  
**Language:** English  
**Total Sections:** 13  
**Code Examples:** 15+  
**Diagrams:** 8+  

---

**End of Documentation**

For technical questions, refer to `docs/spec.md` (technical specification).
For code examples, see `test_core.py` and `test_e2e.py`.
