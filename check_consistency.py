#!/usr/bin/env python3
"""Comprehensive system consistency checker"""

import os
import sys

print("\n" + "=" * 75)
print("COMPREHENSIVE SYSTEM CONSISTENCY CHECK")
print("=" * 75)

errors = []
warnings = []
success = []

# Check 1: UI Dropdown
print("\n[1] UI/MAIN_WINDOW.PY - DROPDOWN SELECTOR")
print("─" * 75)
try:
    with open("ui/main_window.py", "r") as f:
        ui_content = f.read()
        
    checks = [
        ("QComboBox in imports", "QComboBox" in ui_content),
        ("key_size_combo created", "self.key_size_combo = QComboBox()" in ui_content),
        ("All sizes available", '"512", "1024", "1536", "2048"' in ui_content),
        ("Default is 1024", 'setCurrentText("1024")' in ui_content),
        ("No validation errors removed", "key_size_combo.currentText()" in ui_content),
        ("QLineEdit key_size_input REMOVED", "self.key_size_input = QLineEdit" not in ui_content),
    ]
    
    for check_name, result in checks:
        if result:
            print(f"  ✅ {check_name}")
            success.append(check_name)
        else:
            print(f"  ❌ {check_name}")
            errors.append(f"UI: {check_name}")
except Exception as e:
    print(f"  ❌ Error reading file: {e}")
    errors.append(f"UI read error: {e}")

# Check 2: Pure Python RSA
print("\n[2] CORE/RSA_LOGIC.PY - PURE PYTHON IMPLEMENTATION")
print("─" * 75)
try:
    with open("core/rsa_logic.py", "r") as f:
        rsa_content = f.read()
    
    checks = [
        ("No cryptography imports", "from cryptography" not in rsa_content),
        ("No import cryptography", "import cryptography" not in rsa_content),
        ("Miller-Rabin implemented", "miller_rabin" in rsa_content.lower()),
        ("Power_mod implemented", "power_mod" in rsa_content),
        ("RSA signing implemented", "def sign_data" in rsa_content),
        ("RSA verification implemented", "def verify_signature" in rsa_content),
        ("SHA-256 via hashlib", "import hashlib" in rsa_content),
    ]
    
    for check_name, result in checks:
        if result:
            print(f"  ✅ {check_name}")
            success.append(check_name)
        else:
            print(f"  ❌ {check_name}")
            errors.append(f"RSA: {check_name}")
except Exception as e:
    print(f"  ❌ Error reading file: {e}")
    errors.append(f"RSA read error: {e}")

# Check 3: Requirements
print("\n[3] REQUIREMENTS.TXT")
print("─" * 75)
try:
    with open("requirements.txt", "r") as f:
        req_content = f.read()
    
    checks = [
        ("No cryptography dependency", "cryptography" not in req_content.lower()),
        ("PyQt6 present", "PyQt6" in req_content),
        ("hashlib NOT needed", "hashlib" not in req_content),  # stdlib
    ]
    
    for check_name, result in checks:
        if result:
            print(f"  ✅ {check_name}")
            success.append(check_name)
        else:
            if "hashlib" in check_name:
                print(f"  ⚠️  {check_name} (OK - hashlib is stdlib)")
            else:
                print(f"  ❌ {check_name}")
                errors.append(f"Requirements: {check_name}")
    
    print(f"\nFile content:\n{req_content}")
except Exception as e:
    print(f"  ❌ Error reading file: {e}")
    errors.append(f"Requirements read error: {e}")

# Check 4: Test files
print("\n[4] TEST FILES - KEY SIZE")
print("─" * 75)
try:
    with open("test_core.py", "r") as f:
        test_core = f.read()
    with open("test_e2e.py", "r") as f:
        test_e2e = f.read()
    
    checks = [
        ("test_core uses 1024", "generate_keys(1024)" in test_core),
        ("test_e2e uses 1024", "generate_keys(1024)" in test_e2e),
        ("No 2048 in test_core", "generate_keys(2048)" not in test_core),
        ("No 2048 in test_e2e", "generate_keys(2048)" not in test_e2e),
    ]
    
    for check_name, result in checks:
        if result:
            print(f"  ✅ {check_name}")
            success.append(check_name)
        else:
            print(f"  ❌ {check_name}")
            errors.append(f"Tests: {check_name}")
except Exception as e:
    print(f"  ❌ Error reading file: {e}")
    errors.append(f"Tests read error: {e}")

# Check 5: Core module imports
print("\n[5] CORE MODULE IMPORTS")
print("─" * 75)
try:
    from core import (
        generate_keys, sign_data, verify_signature,
        read_file, write_signature, read_signature,
        save_private_key, save_public_key,
        load_private_key, load_public_key
    )
    functions = [
        "generate_keys", "sign_data", "verify_signature",
        "read_file", "write_signature", "read_signature",
        "save_private_key", "save_public_key",
        "load_private_key", "load_public_key"
    ]
    for func in functions:
        print(f"  ✅ {func}")
        success.append(func)
except ImportError as e:
    print(f"  ❌ Import error: {e}")
    errors.append(f"Import: {e}")

# Check 6: Python syntax
print("\n[6] PYTHON SYNTAX CHECK")
print("─" * 75)
import py_compile
files = ["main.py", "ui/main_window.py", "core/rsa_logic.py", "core/file_handler.py"]
for fname in files:
    try:
        py_compile.compile(fname, doraise=True)
        print(f"  ✅ {fname}")
        success.append(fname)
    except py_compile.PyCompileError as e:
        print(f"  ❌ {fname}: {e}")
        errors.append(f"Syntax: {fname}")

# Summary
print("\n" + "=" * 75)
print("SUMMARY")
print("=" * 75)
print(f"✅ Successful checks: {len(success)}")
print(f"❌ Errors: {len(errors)}")
print(f"⚠️  Warnings: {len(warnings)}")

if errors:
    print("\nERRORS TO FIX:")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)
else:
    print("\n" + "🎉 " * 20)
    print("ALL FILES ARE CONSISTENT AND SYNCHRONIZED!")
    print("✅ Pure Python RSA with 1024-bit default")
    print("✅ Dropdown UI selector installed")
    print("✅ All imports working")
    print("✅ No cryptography dependencies")
    print("🎉 " * 20)
    sys.exit(0)
