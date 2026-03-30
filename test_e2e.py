"""
End-to-End Workflow Test

Test complete workflow:
1. Generate keys
2. Create test file
3. Sign file
4. Verify with original file (should PASS)
5. Verify with modified file (should FAIL)
6. Verify with wrong key (should FAIL)
"""

import os
import sys
import shutil

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
    read_signature
)


def cleanup():
    """Clean up test artifacts"""
    test_files = [
        "test_workflow.txt",
        "test_workflow.txt.sig",
        "test_workflow_modified.txt",
        "test_workflow_modified.txt.sig",
        "test_workflow_wrong_key.txt.sig",
        "wrong_private.pem",
        "wrong_public.pem"
    ]
    for f in test_files:
        if os.path.exists(f):
            os.remove(f)
    
    # Clean test key directory
    if os.path.exists("test_keys"):
        shutil.rmtree("test_keys")


def e2e_test():
    """Run end-to-end workflow test"""
    print("\n" + "#"*70)
    print("# END-TO-END WORKFLOW TEST")
    print("#"*70)
    
    cleanup()
    
    # Step 1: Generate main keys
    print("\n[STEP 1] Generate RSA keys...")
    try:
        private_key, public_key = generate_keys(1024)
        print("✓ Generated 1024-bit RSA key pair")
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False
    
    # Save keys to test directory
    os.makedirs("test_keys", exist_ok=True)
    try:
        save_private_key(private_key, "test_keys/private.pem")
        save_public_key(public_key, "test_keys/public.pem")
        print("✓ Saved keys to test_keys/")
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False
    
    # Step 2: Create test file
    print("\n[STEP 2] Create test file...")
    test_file = "test_workflow.txt"
    test_content = b"This is a document to be digitally signed.\nIt contains important information that must be verified."
    
    try:
        with open(test_file, 'wb') as f:
            f.write(test_content)
        print(f"✓ Created test file: {test_file}")
        print(f"  Content: {len(test_content)} bytes")
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False
    
    # Step 3: Sign file
    print("\n[STEP 3] Sign the file...")
    try:
        file_data = read_file(test_file)
        signature = sign_data(file_data, private_key)
        sig_file = test_file + ".sig"
        write_signature(sig_file, signature)
        print(f"✓ Signed {test_file}")
        print(f"✓ Signature saved to: {sig_file}")
        print(f"  Signature size: {len(signature)} bytes")
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False
    
    # Step 4: Verify original file (should PASS)
    print("\n[STEP 4] Verify signature with ORIGINAL file...")
    try:
        file_data = read_file(test_file)
        read_sig = read_signature(sig_file)
        is_valid = verify_signature(file_data, read_sig, public_key)
        
        if is_valid:
            print("✓ Signature VERIFIED - File is authentic")
        else:
            print("✗ FAILED: Signature should be valid for original file!")
            return False
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False
    
    # Step 5: Verify modified file (should FAIL)
    print("\n[STEP 5] Verify signature with MODIFIED file...")
    try:
        # Create modified version
        modified_file = "test_workflow_modified.txt"
        modified_content = b"This is a document to be digitally signed.\nIt contains TAMPERED information that must be verified."
        
        with open(modified_file, 'wb') as f:
            f.write(modified_content)
        
        # Try to verify with signature
        modified_data = read_file(modified_file)
        read_sig = read_signature(sig_file)
        is_valid = verify_signature(modified_data, read_sig, public_key)
        
        if not is_valid:
            print("✓ Signature correctly REJECTED - File was modified")
        else:
            print("✗ FAILED: Signature should NOT be valid for modified file!")
            return False
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False
    
    # Step 6: Verify with wrong key (should FAIL)
    print("\n[STEP 6] Verify signature with WRONG public key...")
    try:
        # Generate different key pair
        wrong_private, wrong_public = generate_keys(1024)
        
        # Try to verify original file with wrong public key
        file_data = read_file(test_file)
        read_sig = read_signature(sig_file)
        is_valid = verify_signature(file_data, read_sig, wrong_public)
        
        if not is_valid:
            print("✓ Signature correctly REJECTED - Wrong public key")
        else:
            print("✗ FAILED: Signature should NOT be valid with wrong key!")
            return False
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False
    
    # Step 7: Reload keys from files
    print("\n[STEP 7] Reload keys from disk and verify again...")
    try:
        loaded_private = load_private_key("test_keys/private.pem")
        loaded_public = load_public_key("test_keys/public.pem")
        
        file_data = read_file(test_file)
        read_sig = read_signature(sig_file)
        is_valid = verify_signature(file_data, read_sig, loaded_public)
        
        if is_valid:
            print("✓ Successfully loaded keys from disk")
            print("✓ Verification works with reloaded keys")
        else:
            print("✗ FAILED: Reloaded keys don't verify!")
            return False
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False
    
    # Summary
    print("\n" + "="*70)
    print("END-TO-END TEST PASSED")
    print("="*70)
    print("\n✓ All workflow steps completed successfully:")
    print("  1. Generated RSA keys")
    print("  2. Created test file")
    print("  3. Signed file successfully")
    print("  4. Verified original file - VALID")
    print("  5. Detected modified file - INVALID")
    print("  6. Rejected wrong key - INVALID")
    print("  7. Reloaded and verified - VALID")
    print("\n✓ System is READY FOR PRODUCTION")
    
    cleanup()
    return True


if __name__ == "__main__":
    success = e2e_test()
    sys.exit(0 if success else 1)
