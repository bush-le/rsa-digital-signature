"""
RSA Digital Signature Logic Module - Pure Python Implementation

This module implements RSA cryptography from scratch WITHOUT using
cryptography library. All mathematical operations are coded manually.

Responsibilities:
- RSA key generation (1024-bit)
- Prime number generation using Miller-Rabin test
- RSA signing with PKCS#1 v1.5 padding + SHA-256
- RSA signature verification
- Key storage in PEM format
"""

import hashlib
import random
import os
from typing import Tuple


class RSASignatureError(Exception):
    """Custom exception for RSA signature errors"""
    pass


# ============================================================================
# PART 1: PRIME NUMBER GENERATION (Foundation)
# ============================================================================

def is_even(n: int) -> bool:
    """Check if number is even"""
    return n % 2 == 0


def gcd(a: int, b: int) -> int:
    """
    Calculate Greatest Common Divisor using Euclidean algorithm.
    
    GCD(a, b) is the largest number that divides both a and b.
    Used for checking if numbers are coprime.
    """
    while b:
        a, b = b, a % b
    return a


def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """
    Calculate Extended GCD: finds gcd and Bézout coefficients.
    
    Returns (gcd, x, y) where:
        gcd = GCD(a, b)
        ax + by = gcd
    
    Used to find modular multiplicative inverse.
    """
    if b == 0:
        return a, 1, 0
    
    gcd_val, x1, y1 = extended_gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    
    return gcd_val, x, y


def mod_inverse(a: int, m: int) -> int:
    """
    Calculate modular multiplicative inverse of a modulo m.
    
    Finds x such that: (a * x) % m = 1
    
    This is used in RSA to calculate the private exponent d
    from the public exponent e.
    """
    gcd_val, x, _ = extended_gcd(a % m, m)
    
    if gcd_val != 1:
        raise RSASignatureError("Modular inverse does not exist")
    
    return (x % m + m) % m


def power_mod(base: int, exp: int, mod: int) -> int:
    """
    Calculate (base ^ exp) % mod efficiently.
    
    Uses binary exponentiation to avoid computing huge numbers.
    This is critical for RSA performance.
    
    Algorithm:
    - If exp is even: base^exp = (base^2)^(exp/2)
    - If exp is odd: base^exp = base * base^(exp-1)
    """
    result = 1
    base = base % mod
    
    while exp > 0:
        # If exponent is odd, multiply result by base
        if exp % 2 == 1:
            result = (result * base) % mod
        
        # Reduce exponent and square base
        exp = exp >> 1  # Divide by 2
        base = (base * base) % mod
    
    return result


def miller_rabin_test(n: int, k: int = 40) -> bool:
    """
    Miller-Rabin primality test.
    
    Probabilistic test that checks if n is prime.
    - If returns False: n is definitely NOT prime
    - If returns True: n is probably prime (confidence = 1 - 4^(-k))
    
    With k=40 rounds, probability of error is < 2^(-80)
    
    How it works:
    1. Write n-1 = 2^r * d (where d is odd)
    2. For k iterations:
       - Choose random a in [2, n-2]
       - Compute x = a^d mod n
       - If x = 1 or x = n-1: continue
       - Square x, r-1 times
       - If x ever equals n-1: continue
       - Otherwise: n is composite
    3. If all iterations pass: probably prime
    """
    # Small primes are prime
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    if n in small_primes:
        return True
    if n < 2 or is_even(n):
        return False
    
    # Write n-1 as 2^r * d
    r, d = 0, n - 1
    while is_even(d):
        r += 1
        d //= 2
    
    # Witness loop - k iterations
    for _ in range(k):
        # Choose random witness
        a = random.randint(2, n - 2)
        
        # Compute x = a^d mod n
        x = power_mod(a, d, n)
        
        # If x = 1 or x = n-1, continue
        if x == 1 or x == n - 1:
            continue
        
        # Square x, r-1 times
        composite = True
        for _ in range(r - 1):
            x = power_mod(x, 2, n)
            if x == n - 1:
                composite = False
                break
        
        if composite:
            return False  # Definitely composite
    
    return True  # Probably prime


def generate_prime(bit_length: int) -> int:
    """
    Generate a random prime number with specified bit length.
    
    Algorithm:
    1. Generate random odd number of desired length
    2. Test primality using Miller-Rabin
    3. If not prime, move to next odd number
    4. Repeat until prime found
    """
    while True:
        # Generate random number with bit_length bits
        num = random.getrandbits(bit_length)
        
        # Make it odd (all primes except 2 are odd)
        num = num | (1 << (bit_length - 1))  # Ensure high bit set
        num = num | 1  # Make odd
        
        # Test primality
        if miller_rabin_test(num):
            return num


# ============================================================================
# PART 2: RSA KEY GENERATION
# ============================================================================

class RSAPrivateKey:
    """RSA Private Key - used for signing"""
    
    def __init__(self, n: int, e: int, d: int, p: int, q: int):
        """
        Initialize private key.
        
        Parameters:
        - n: modulus (public)
        - e: public exponent
        - d: private exponent (secret!)
        - p, q: prime factors of n (secrets for CRT optimization)
        """
        self.n = n      # modulus
        self.e = e      # public exponent
        self.d = d      # private exponent (SECRET)
        self.p = p      # prime factor (SECRET)
        self.q = q      # prime factor (SECRET)
        self.size = n.bit_length()  # key size in bits


class RSAPublicKey:
    """RSA Public Key - used for verification"""
    
    def __init__(self, n: int, e: int):
        """
        Initialize public key.
        
        Parameters:
        - n: modulus
        - e: public exponent
        """
        self.n = n  # modulus
        self.e = e  # public exponent
        self.size = n.bit_length()  # key size in bits


def generate_keys(key_size: int = 1024) -> Tuple[RSAPrivateKey, RSAPublicKey]:
    """
    Generate RSA public-private key pair.
    
    RSA Algorithm:
    1. Choose two distinct large random primes p and q
    2. Compute n = p * q (modulus)
    3. Compute φ(n) = (p-1) * (q-1) (Euler's totient)
    4. Choose e such that 1 < e < φ(n) and gcd(e, φ(n)) = 1
       (Usually e = 65537)
    5. Compute d = e^(-1) mod φ(n) (modular inverse)
       d is calculated such that (e * d) ≡ 1 (mod φ(n))
    
    Public key: (n, e)
    Private key: (n, e, d) [or (n, d) in simplified form]
    
    Security relies on:
    - n is very hard to factor (finding p and q is hard)
    - e and d are inverses modulo φ(n)
    
    Args:
        key_size: Key size in bits (minimum 1024, default good for education)
    
    Returns:
        Tuple of (private_key, public_key)
    
    Raises:
        RSASignatureError: If key generation fails
    """
    try:
        if key_size < 512:
            raise ValueError("Key size must be at least 512 bits")
        
        # Step 1: Generate two large distinct primes
        print(f"[RSA] Generating {key_size}-bit primes... (may take 10-30 seconds)")
        
        half_size = key_size // 2
        
        while True:
            p = generate_prime(half_size)
            q = generate_prime(half_size)
            
            # Ensure p and q are distinct
            if p != q:
                break
        
        print(f"[RSA] ✓ Generated primes p and q")
        
        # Step 2: Calculate n = p * q
        n = p * q
        print(f"[RSA] ✓ Calculated modulus n (size: {n.bit_length()} bits)")
        
        # Step 3: Calculate φ(n) = (p-1)(q-1)
        # This is Euler's totient function
        phi_n = (p - 1) * (q - 1)
        print(f"[RSA] ✓ Calculated φ(n)")
        
        # Step 4: Choose public exponent e
        # Standard choice is 65537 (Fermat prime F_4)
        # Must satisfy: gcd(e, φ(n)) = 1
        e = 65537
        
        # Check if e is valid (gcd must be 1)
        while gcd(e, phi_n) != 1:
            e += 2
        
        print(f"[RSA] ✓ Selected public exponent e = {e}")
        
        # Step 5: Calculate private exponent d
        # d is the modular multiplicative inverse of e modulo φ(n)
        # This means: (e * d) % φ(n) = 1
        d = mod_inverse(e, phi_n)
        print(f"[RSA] ✓ Calculated private exponent d")
        
        # Create key objects
        private_key = RSAPrivateKey(n, e, d, p, q)
        public_key = RSAPublicKey(n, e)
        
        print(f"[RSA] ✓ Key pair generation complete!")
        
        return private_key, public_key
    
    except ValueError as e:
        raise RSASignatureError(f"Invalid key size: {str(e)}")
    except Exception as e:
        raise RSASignatureError(f"Key generation failed: {str(e)}")


# ============================================================================
# PART 3: PADDING AND HASHING
# ============================================================================

def sha256_hash(data: bytes) -> bytes:
    """
    Calculate SHA-256 hash of data.
    
    SHA-256 (Secure Hash Algorithm 256) produces a 32-byte hash.
    Uses Python's hashlib (standard library).
    
    Why hash before signing?
    - Files can be huge (100 MB+)
    - Hash is always 32 bytes
    - RSA is slow, hashing is fast
    - Following PKCS#1 standard
    """
    return hashlib.sha256(data).digest()


def pkcs1_v15_pad(data_hash: bytes, key_size: int) -> bytes:
    """
    PKCS#1 v1.5 padding for signatures.
    
    Format: 0x00 || 0x01 || PS || 0x00 || T
    
    Where:
    - 0x00: padding version indicator
    - 0x01: block type (0x01 for signatures)
    - PS: padding string of 0xFF bytes (at least 8 bytes)
    - 0x00: separator
    - T: DigestInfo (hash algorithm identifier + hash)
    
    Total length = key_size_in_bytes
    
    Why padding?
    - SecurityPrevents certain attacks
    - Standardized format
    - Contains hash algorithm info (allows multiple hash algos)
    """
    # Convert hash bytes to DigestInfo for SHA-256
    # This is the ASN.1 DER encoding for SHA-256
    sha256_info = bytes([
        0x30, 0x31,  # SEQUENCE length 49
        0x30, 0x0d,  # SEQUENCE length 13
        0x06, 0x09,  # OBJECT IDENTIFIER length 9
        0x60, 0x86, 0x48, 0x01, 0x65, 0x03, 0x04, 0x02, 0x01,  # SHA-256 OID
        0x05, 0x00,  # NULL
        0x04, 0x20   # OCTET STRING length 32
    ])
    
    # DigestInfo = algorithm identifier + hash value
    digest_info = sha256_info + data_hash
    
    # Calculate padding string length
    # Format: 0x00 || 0x01 || PS || 0x00 || digest_info
    key_size_bytes = (key_size + 7) // 8
    ps_length = key_size_bytes - len(digest_info) - 3
    
    if ps_length < 8:
        raise RSASignatureError("Key size too small for padding")
    
    # Build padded message
    ps = bytes([0xFF] * ps_length)
    padded = bytes([0x00, 0x01]) + ps + bytes([0x00]) + digest_info
    
    return padded


def pkcs1_v15_unpad(padded_data: bytes, key_size: int) -> bytes:
    """
    Remove PKCS#1 v1.5 padding and extract hash.
    
    Reverses the padding applied during signing.
    
    Returns:
        The extracted hash value
    """
    # Check header
    if len(padded_data) < 11 or padded_data[0] != 0x00 or padded_data[1] != 0x01:
        raise RSASignatureError("Invalid padding format")
    
    # Find separator byte (0x00)
    separator_index = padded_data.find(b'\x00', 2)
    if separator_index < 10:  # At least 8 bytes of 0xFF required
        raise RSASignatureError("Invalid padding: insufficient padding string")
    
    # Extract digest info (algorithm ID + hash)
    digest_info = padded_data[separator_index + 1:]
    
    # Verify SHA-256 algorithm identifier and extract hash
    sha256_prefix = bytes([
        0x30, 0x31, 0x30, 0x0d, 0x06, 0x09,
        0x60, 0x86, 0x48, 0x01, 0x65, 0x03, 0x04, 0x02, 0x01,
        0x05, 0x00, 0x04, 0x20
    ])
    
    if not digest_info.startswith(sha256_prefix):
        raise RSASignatureError("Invalid hash algorithm identifier")
    
    # Extract the hash value (last 32 bytes)
    hash_value = digest_info[len(sha256_prefix):]
    
    if len(hash_value) != 32:  # SHA-256 produces 32 bytes
        raise RSASignatureError("Invalid hash length")
    
    return hash_value


# ============================================================================
# PART 4: SIGNING AND VERIFICATION
# ============================================================================

def sign_data(data: bytes, private_key: RSAPrivateKey) -> bytes:
    """
    Sign data using RSA private key with PKCS#1 v1.5 padding + SHA-256.
    
    RSA Signature Algorithm:
    1. Hash the data: H = SHA-256(M)
    2. Pad the hash: M' = PKCS#1_v1.5_pad(H)
    3. Convert padding to number: m = int(M')
    4. Compute signature: s = m^d mod n
    5. Convert back to bytes
    
    Why this order?
    - Hashing reduces data size
    - Padding prevents certain attacks
    - Exponentiation is the actual RSA operation
    - d is the private exponent
    
    Only the owner of private key can create valid signatures.
    
    Args:
        data: Data to sign (bytes)
        private_key: RSA private key
    
    Returns:
        Digital signature (bytes)
    
    Raises:
        RSASignatureError: If signing fails
    """
    try:
        if not isinstance(data, bytes):
            raise TypeError("Data must be bytes")
        
        print(f"[RSA] Signing data ({len(data)} bytes)...")
        
        # Step 1: Hash the data
        data_hash = sha256_hash(data)
        print(f"[RSA] ✓ SHA-256 hash computed")
        
        # Step 2: Apply PKCS#1 v1.5 padding
        padded = pkcs1_v15_pad(data_hash, private_key.size)
        print(f"[RSA] ✓ PKCS#1 v1.5 padding applied")
        
        # Step 3: Convert padded bytes to integer
        m = int.from_bytes(padded, byteorder='big')
        
        # Step 4: Compute RSA signature: s = m^d mod n
        # This is the core RSA operation
        # Only possible with private key (d)
        print(f"[RSA] Performing RSA exponentiation (computing m^d mod n)...")
        signature_int = power_mod(m, private_key.d, private_key.n)
        print(f"[RSA] ✓ Signature computed")
        
        # Step 5: Convert back to bytes
        key_size_bytes = (private_key.size + 7) // 8
        signature = signature_int.to_bytes(key_size_bytes, byteorder='big')
        
        print(f"[RSA] ✓ Signing complete (signature: {len(signature)} bytes)")
        
        return signature
    
    except TypeError as e:
        raise RSASignatureError(f"Invalid input type: {str(e)}")
    except Exception as e:
        raise RSASignatureError(f"Signing failed: {str(e)}")


def verify_signature(data: bytes, signature: bytes, public_key: RSAPublicKey) -> bool:
    """
    Verify RSA signature using public key.
    
    RSA Verification Algorithm:
    1. Convert signature from bytes to integer: s = int(signature)
    2. Decrypt signature: m = s^e mod n
    3. Remove padding and extract hash: H' = unpad(m)
    4. Hash the data: H = SHA-256(data)
    5. Compare: H == H'
    
    If hashes match → Signature is valid ✓
    If hashes differ → Signature is invalid ✗
    
    Why this works?
    - The receiver uses public key (e)
    - Only sender with private key (d) could have created valid s
    - Proves authenticity (who signed)
    - Proves integrity (file unchanged)
    
    Cannot forge signature without private key.
    Cannot change file without breaking signature.
    
    Args:
        data: Original data (bytes)
        signature: Digital signature (bytes)
        public_key: RSA public key
    
    Returns:
        True if signature is valid, False otherwise
    """
    try:
        if not isinstance(data, bytes):
            raise TypeError("Data must be bytes")
        if not isinstance(signature, bytes):
            raise TypeError("Signature must be bytes")
        
        print(f"[RSA] Verifying signature ({len(signature)} bytes)...")
        
        # Step 1: Convert signature bytes to integer
        signature_int = int.from_bytes(signature, byteorder='big')
        
        # Step 2: Decrypt signature: m = s^e mod n
        # This is possible with public key (e)
        # If signature was created with matching private key,
        # this will recover the padded hash
        print(f"[RSA] Performing RSA exponentiation (computing s^e mod n)...")
        m = power_mod(signature_int, public_key.e, public_key.n)
        print(f"[RSA] ✓ Signature decrypted")
        
        # Step 3: Convert back to bytes and remove padding
        key_size_bytes = (public_key.size + 7) // 8
        padded = m.to_bytes(key_size_bytes, byteorder='big')
        
        try:
            recovered_hash = pkcs1_v15_unpad(padded, public_key.size)
            print(f"[RSA] ✓ Padding removed, hash extracted")
        except RSASignatureError:
            print(f"[RSA] ✗ Invalid padding - signature is forged")
            return False
        
        # Step 4: Compute hash of received data
        data_hash = sha256_hash(data)
        print(f"[RSA] ✓ SHA-256 hash of data computed")
        
        # Step 5: Compare hashes
        if recovered_hash == data_hash:
            print(f"[RSA] ✓ Hashes match - SIGNATURE VALID")
            return True
        else:
            print(f"[RSA] ✗ Hashes don't match - SIGNATURE INVALID")
            return False
    
    except TypeError as e:
        raise RSASignatureError(f"Invalid input type: {str(e)}")
    except Exception as e:
        raise RSASignatureError(f"Verification failed: {str(e)}")


# ============================================================================
# PART 5: KEY PERSISTENCE (PEM Format)
# ============================================================================

def save_private_key(private_key: RSAPrivateKey, path: str) -> None:
    """
    Save private key to PEM file.
    
    Format: Simple text-based format for key storage
    
    WARNING: This saves the PRIVATE KEY as plain text!
    In production, should encrypt with password.
    
    PEM Format:
    -----BEGIN RSA PRIVATE KEY-----
    [base64 encoded key data]
    -----END RSA PRIVATE KEY-----
    """
    try:
        # Create a simple text representation
        # Format: n|e|d (pipe-separated)
        key_data = f"{private_key.n}|{private_key.e}|{private_key.d}|{private_key.p}|{private_key.q}\n"
        
        # Save to file
        with open(path, 'w') as f:
            f.write("-----BEGIN RSA PRIVATE KEY-----\n")
            f.write(key_data)
            f.write("-----END RSA PRIVATE KEY-----\n")
        
        print(f"[RSA] ✓ Private key saved to {path}")
    except Exception as e:
        raise RSASignatureError(f"Failed to save private key: {str(e)}")


def save_public_key(public_key: RSAPublicKey, path: str) -> None:
    """
    Save public key to PEM file.
    
    Format: Simple text format
    Public keys are safe to share.
    
    PEM Format:
    -----BEGIN RSA PUBLIC KEY-----
    [base64 encoded key data]
    -----END RSA PUBLIC KEY-----
    """
    try:
        # Create text representation
        # Format: n|e (pipe-separated)
        key_data = f"{public_key.n}|{public_key.e}\n"
        
        # Save to file
        with open(path, 'w') as f:
            f.write("-----BEGIN RSA PUBLIC KEY-----\n")
            f.write(key_data)
            f.write("-----END RSA PUBLIC KEY-----\n")
        
        print(f"[RSA] ✓ Public key saved to {path}")
    except Exception as e:
        raise RSASignatureError(f"Failed to save public key: {str(e)}")


def load_private_key(path: str) -> RSAPrivateKey:
    """
    Load private key from PEM file.
    
    Args:
        path: Path to private key file
    
    Returns:
        RSAPrivateKey object
    
    Raises:
        RSASignatureError: If load fails
    """
    try:
        with open(path, 'r') as f:
            content = f.read()
        
        # Extract key data between BEGIN and END markers
        start = content.find("-----BEGIN RSA PRIVATE KEY-----")
        end = content.find("-----END RSA PRIVATE KEY-----")
        
        if start == -1 or end == -1:
            raise RSASignatureError("Invalid private key format")
        
        # Get the key data line
        key_line = content[start + 31:end].strip()
        
        # Parse key components
        if '|' not in key_line:
            raise RSASignatureError("Invalid key data format")
        
        parts = key_line.split('|')
        if len(parts) < 3:
            raise RSASignatureError("Invalid key data: missing components")
        
        n, e, d = int(parts[0]), int(parts[1]), int(parts[2])
        p = int(parts[3]) if len(parts) > 3 else 0
        q = int(parts[4]) if len(parts) > 4 else 0
        
        private_key = RSAPrivateKey(n, e, d, p, q)
        print(f"[RSA] ✓ Private key loaded from {path}")
        
        return private_key
    
    except FileNotFoundError:
        raise RSASignatureError(f"Private key file not found: {path}")
    except Exception as e:
        raise RSASignatureError(f"Failed to load private key: {str(e)}")


def load_public_key(path: str) -> RSAPublicKey:
    """
    Load public key from PEM file.
    
    Args:
        path: Path to public key file
    
    Returns:
        RSAPublicKey object
    
    Raises:
        RSASignatureError: If load fails
    """
    try:
        with open(path, 'r') as f:
            content = f.read()
        
        # Extract key data between BEGIN and END markers
        start = content.find("-----BEGIN RSA PUBLIC KEY-----")
        end = content.find("-----END RSA PUBLIC KEY-----")
        
        if start == -1 or end == -1:
            raise RSASignatureError("Invalid public key format")
        
        # Get the key data line
        key_line = content[start + 30:end].strip()
        
        # Parse key components
        if '|' not in key_line:
            raise RSASignatureError("Invalid key data format")
        
        parts = key_line.split('|')
        if len(parts) < 2:
            raise RSASignatureError("Invalid key data: missing components")
        
        n, e = int(parts[0]), int(parts[1])
        
        public_key = RSAPublicKey(n, e)
        print(f"[RSA] ✓ Public key loaded from {path}")
        
        return public_key
    
    except FileNotFoundError:
        raise RSASignatureError(f"Public key file not found: {path}")
    except Exception as e:
        raise RSASignatureError(f"Failed to load public key: {str(e)}")
