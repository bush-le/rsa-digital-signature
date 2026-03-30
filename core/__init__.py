"""
Core cryptographic and file handling modules
"""

from .rsa_logic import (
    generate_keys,
    save_private_key,
    save_public_key,
    load_private_key,
    load_public_key,
    sign_data,
    verify_signature,
    RSASignatureError
)

from .file_handler import (
    read_file,
    write_signature,
    read_signature,
    FileHandlerError
)

__all__ = [
    'generate_keys',
    'save_private_key',
    'save_public_key',
    'load_private_key',
    'load_public_key',
    'sign_data',
    'verify_signature',
    'read_file',
    'write_signature',
    'read_signature',
    'RSASignatureError',
    'FileHandlerError'
]
