"""
Manual test script to validate core functionality
Tests: keygen → sign → verify (original & modified)

NOTE: Uses 1024-bit keys for speed (pure Python educational implementation)
      For production security, use 2048+ bits with optimized RSA libraries
"""

import os
import sys
from core import (
    generate_keys,
    save_private_key,
    save_public_key,
    load_private_key,
    load_public_key,
    sign_data,
    verify_signature,
    read_file,
    write_signature,
    read_signature,
    RSASignatureError,
    FileHandlerError
)


def test_key_generation():
    """Test 1: Key generation"""
    print("\n" + "="*60)
    print("TEST 1: RSA Key Generation (1024-bit)")
    print("="*60)
    
    try:
        private_key, public_key = generate_keys(1024)
        print("✓ Generated 1024-bit RSA key pair")
        print(f"  Private Key Type: {type(private_key).__name__}")
        print(f"  Public Key Type: {type(public_key).__name__}")
        print(f"  Key Size: {private_key.size} bits")
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False


def test_key_persistence():
    """Test 2: Save and load keys"""
    print("\n" + "="*60)
    print("TEST 2: Key Persistence (Save/Load)")
    print("="*60)
    
    try:
        # Generate and save keys
        private_key, public_key = generate_keys(1024)
        
        private_path = "keys/test_private.pem"
        public_path = "keys/test_public.pem"
        
        save_private_key(private_key, private_path)
        save_public_key(public_key, public_path)
        print(f"✓ Saved keys:")
        print(f"  - Private: {private_path}")
        print(f"  - Public: {public_path}")
        
        # Load keys and verify
        loaded_private = load_private_key(private_path)
        loaded_public = load_public_key(public_path)
        print("✓ Successfully loaded keys from files")
        
        # Verify they match
        assert loaded_private.n == private_key.n
        assert loaded_public.n == public_key.n
        print("✓ Loaded keys match originals")
        
        # Cleanup
        os.remove(private_path)
        os.remove(public_path)
        
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False


def test_file_operations():
    """Test 3: File I/O"""
    print("\n" + "="*60)
    print("TEST 3: File I/O Operations")
    print("="*60)
    
    try:
        test_file = "test_file.txt"
        test_data = b"Hello, RSA Digital Signatures!"
        
        # Write test file
        with open(test_file, 'wb') as f:
            f.write(test_data)
        print(f"✓ Created test file: {test_file}")
        
        # Read using file_handler
        read_data = read_file(test_file)
        assert read_data == test_data, "File content mismatch"
        print("✓ Read file successfully (binary mode)")
        
        # Cleanup
        os.remove(test_file)
        
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False


def test_sign_and_verify():
    """Test 4: Sign and verify original file"""
    print("\n" + "="*60)
    print("TEST 4: Sign & Verify (Original File)")
    print("="*60)
    
    try:
        # Generate keys
        print("Generating RSA keys (1024-bit)... this may take 10-30 seconds...")
        private_key, public_key = generate_keys(1024)
        
        # Create test file
        test_file = "test_original.txt"
        test_data = b"This is the original file content."
        with open(test_file, 'wb') as f:
            f.write(test_data)
        print(f"✓ Created test file: {test_file}")
        
        # Read and sign
        file_data = read_file(test_file)
        signature = sign_data(file_data, private_key)
        print(f"✓ Signed file (signature size: {len(signature)} bytes)")
        
        # Verify
        sig_file = test_file + ".sig"
        write_signature(sig_file, signature)
        print(f"✓ Saved signature: {sig_file}")
        
        read_sig = read_signature(sig_file)
        is_valid = verify_signature(file_data, read_sig, public_key)
        
        if is_valid:
            print("✓ Signature VERIFIED - Original file is authentic")
        else:
            print("✗ Signature INVALID - Unexpected result!")
            return False
        
        # Cleanup
        os.remove(test_file)
        os.remove(sig_file)
        
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_verify_modified_file():
    """Test 5: Verify fails on modified file"""
    print("\n" + "="*60)
    print("TEST 5: Verify Modified File (Should FAIL)")
    print("="*60)
    
    try:
        # Generate keys
        print("Generating RSA keys (1024-bit)... this may take 10-30 seconds...")
        private_key, public_key = generate_keys(1024)
        
        # Create and sign original file
        test_file = "test_modified.txt"
        original_data = b"Original content"
        with open(test_file, 'wb') as f:
            f.write(original_data)
        print(f"✓ Created original file: {test_file}")
        
        signature = sign_data(original_data, private_key)
        sig_file = test_file + ".sig"
        write_signature(sig_file, signature)
        print(f"✓ Signed original file")
        
        # Modify file
        modified_data = b"Modified content - tampered!"
        with open(test_file, 'wb') as f:
            f.write(modified_data)
        print(f"✓ Modified file contents")
        
        # Verify (should fail)
        read_sig = read_signature(sig_file)
        is_valid = verify_signature(modified_data, read_sig, public_key)
        
        if not is_valid:
            print("✓ Signature correctly REJECTED - File was tampered")
        else:
            print("✗ ERROR: Signature validated for modified file!")
            return False
        
        # Cleanup
        os.remove(test_file)
        os.remove(sig_file)
        
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_wrong_key():
    """Test 6: Verify fails with wrong public key"""
    print("\n" + "="*60)
    print("TEST 6: Wrong Public Key (Should FAIL)")
    print("="*60)
    
    try:
        # Generate two independent key pairs
        print("Generating first RSA key pair (1024-bit)... this may take 10-30 seconds...")
        private_key1, public_key1 = generate_keys(1024)
        
        print("Generating second RSA key pair (1024-bit)... this may take 10-30 seconds...")
        private_key2, public_key2 = generate_keys(1024)
        
        # Sign with key1
        test_data = b"Sensitive data"
        signature = sign_data(test_data, private_key1)
        print("✓ Signed data with Key1")
        
        # Try to verify with key2 (should fail)
        is_valid = verify_signature(test_data, signature, public_key2)
        
        if not is_valid:
            print("✓ Signature correctly REJECTED - Wrong public key")
        else:
            print("✗ ERROR: Signature validated with wrong key!")
            return False
        
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests and report"""
    print("\n" + "#"*60)
    print("# RSA DIGITAL SIGNATURE SYSTEM - CORE VALIDATION")
    print("# Pure Python Implementation (NO cryptography library)")
    print("#"*60)
    
    results = []
    
    # Quick tests first
    results.append(("Key Generation", test_key_generation()))
    results.append(("Key Persistence", test_key_persistence()))
    results.append(("File I/O", test_file_operations()))
    
    # Slower tests with full keygen
    results.append(("Sign & Verify Original", test_sign_and_verify()))
    results.append(("Reject Modified File", test_verify_modified_file()))
    results.append(("Reject Wrong Key", test_wrong_key()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ Core modules validated successfully!")
        print("✓ Pure Python RSA implementation is working!")
        return True
    else:
        print("\n✗ Some tests failed. Review the output above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
