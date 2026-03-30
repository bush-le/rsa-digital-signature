"""
RSA Digital Signature Application - Entry Point

Run with:
    python main.py
"""

import sys
from PyQt6.QtWidgets import QApplication
from ui import RSADigitalSignatureWindow


def main():
    """Initialize and run the application"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Create and show main window
    window = RSADigitalSignatureWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
