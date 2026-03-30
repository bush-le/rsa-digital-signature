"""
File Handler Module

Responsibilities:
- Binary-safe file reading
- Signature file I/O
- Error handling for file operations
"""

import os


class FileHandlerError(Exception):
    """Custom exception for file handling errors"""
    pass


def read_file(path: str) -> bytes:
    """
    Read file in binary mode (safe for all file types).
    
    Args:
        path: Path to file
        
    Returns:
        File contents as bytes
        
    Raises:
        FileHandlerError: If file cannot be read
    """
    try:
        if not os.path.exists(path):
            raise FileHandlerError(f"File not found: {path}")
        
        if not os.path.isfile(path):
            raise FileHandlerError(f"Path is not a file: {path}")
        
        with open(path, 'rb') as f:
            data = f.read()
        
        return data
    except FileHandlerError:
        raise
    except Exception as e:
        raise FileHandlerError(f"Failed to read file {path}: {str(e)}")


def write_signature(path: str, signature: bytes) -> None:
    """
    Write signature to file.
    
    Args:
        path: Path to signature file (typically .sig)
        signature: Signature data as bytes
        
    Raises:
        FileHandlerError: If write fails
    """
    try:
        if not isinstance(signature, bytes):
            raise TypeError("Signature must be bytes")
        
        # Create directory if it doesn't exist
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        with open(path, 'wb') as f:
            f.write(signature)
    except TypeError as e:
        raise FileHandlerError(f"Invalid input type: {str(e)}")
    except Exception as e:
        raise FileHandlerError(f"Failed to write signature to {path}: {str(e)}")


def read_signature(path: str) -> bytes:
    """
    Read signature from file.
    
    Args:
        path: Path to signature file
        
    Returns:
        Signature data as bytes
        
    Raises:
        FileHandlerError: If read fails
    """
    try:
        if not os.path.exists(path):
            raise FileHandlerError(f"Signature file not found: {path}")
        
        if not os.path.isfile(path):
            raise FileHandlerError(f"Path is not a file: {path}")
        
        with open(path, 'rb') as f:
            signature = f.read()
        
        return signature
    except FileHandlerError:
        raise
    except Exception as e:
        raise FileHandlerError(f"Failed to read signature from {path}: {str(e)}")
