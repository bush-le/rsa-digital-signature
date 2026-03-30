"""
GUI Main Window - PyQt6 Interface

Responsibilities:
- User interface for key generation
- File selection dialogs
- Sign/verify operations
- Result display
"""

import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QLineEdit, QTextEdit, QFileDialog,
    QMessageBox, QTabWidget, QGroupBox, QComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

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


class RSADigitalSignatureWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RSA Digital Signature System")
        self.setGeometry(100, 100, 900, 700)
        
        # Key paths
        self.keys_dir = "keys"
        self.private_key_path = os.path.join(self.keys_dir, "private.pem")
        self.public_key_path = os.path.join(self.keys_dir, "public.pem")
        
        # Ensure keys directory exists
        os.makedirs(self.keys_dir, exist_ok=True)
        
        # Cache for loaded keys
        self.private_key = None
        self.public_key = None
        
        # Initialize UI
        self.init_ui()
    
    def init_ui(self):
        """Initialize user interface with tabs"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        
        # Tab widget
        tabs = QTabWidget()
        tabs.addTab(self.create_keygen_tab(), "Key Generation")
        tabs.addTab(self.create_sign_tab(), "Sign File")
        tabs.addTab(self.create_verify_tab(), "Verify Signature")
        
        layout.addWidget(tabs)
        central_widget.setLayout(layout)
    
    def create_keygen_tab(self):
        """Tab 1: Key Generation"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("RSA Key Pair Generation")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Info
        info = QLabel("Generate a new 1024-bit RSA key pair (Pure Python Implementation)\nKeys will be saved in the 'keys/' directory")
        layout.addWidget(info)
        
        # Key size group
        size_group = QGroupBox("Key Configuration")
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Key Size (bits):"))
        self.key_size_combo = QComboBox()
        self.key_size_combo.addItems(["512", "1024", "1536", "2048"])
        self.key_size_combo.setCurrentText("1024")  # Default
        self.key_size_combo.setMaximumWidth(100)
        size_layout.addWidget(self.key_size_combo)
        size_layout.addStretch()
        size_group.setLayout(size_layout)
        layout.addWidget(size_group)
        
        # Generate button
        gen_btn = QPushButton("Generate Keys")
        gen_btn.setMinimumHeight(50)
        gen_btn.clicked.connect(self.on_generate_keys)
        layout.addWidget(gen_btn)
        
        # Status area
        layout.addWidget(QLabel("Status:"))
        self.keygen_status = QTextEdit()
        self.keygen_status.setReadOnly(True)
        self.keygen_status.setMaximumHeight(150)
        layout.addWidget(self.keygen_status)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_sign_tab(self):
        """Tab 2: Sign File"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Sign a File")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Select file
        file_group = QGroupBox("Select File to Sign")
        file_layout = QHBoxLayout()
        self.sign_file_path = QLineEdit()
        self.sign_file_path.setReadOnly(True)
        file_layout.addWidget(self.sign_file_path)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.on_browse_file_to_sign)
        file_layout.addWidget(browse_btn)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Sign button
        sign_btn = QPushButton("Sign File")
        sign_btn.setMinimumHeight(50)
        sign_btn.clicked.connect(self.on_sign_file)
        layout.addWidget(sign_btn)
        
        # Status area
        layout.addWidget(QLabel("Status:"))
        self.sign_status = QTextEdit()
        self.sign_status.setReadOnly(True)
        self.sign_status.setMaximumHeight(150)
        layout.addWidget(self.sign_status)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_verify_tab(self):
        """Tab 3: Verify Signature"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Verify Signature")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Select original file
        orig_group = QGroupBox("Select Original File")
        orig_layout = QHBoxLayout()
        self.verify_file_path = QLineEdit()
        self.verify_file_path.setReadOnly(True)
        orig_layout.addWidget(self.verify_file_path)
        browse_orig_btn = QPushButton("Browse...")
        browse_orig_btn.clicked.connect(self.on_browse_file_to_verify)
        orig_layout.addWidget(browse_orig_btn)
        orig_group.setLayout(orig_layout)
        layout.addWidget(orig_group)
        
        # Select signature file
        sig_group = QGroupBox("Select Signature File (.sig)")
        sig_layout = QHBoxLayout()
        self.sig_file_path = QLineEdit()
        self.sig_file_path.setReadOnly(True)
        sig_layout.addWidget(self.sig_file_path)
        browse_sig_btn = QPushButton("Browse...")
        browse_sig_btn.clicked.connect(self.on_browse_signature_file)
        sig_layout.addWidget(browse_sig_btn)
        sig_group.setLayout(sig_layout)
        layout.addWidget(sig_group)
        
        # Verify button
        verify_btn = QPushButton("Verify Signature")
        verify_btn.setMinimumHeight(50)
        verify_btn.clicked.connect(self.on_verify_signature)
        layout.addWidget(verify_btn)
        
        # Result area
        layout.addWidget(QLabel("Result:"))
        self.verify_result = QTextEdit()
        self.verify_result.setReadOnly(True)
        self.verify_result.setMaximumHeight(150)
        layout.addWidget(self.verify_result)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    # ===== Event Handlers =====
    
    def on_generate_keys(self):
        """Handle key generation"""
        try:
            self.keygen_status.clear()
            self.log_keygen("Starting key generation...")
            
            # Get key size from dropdown (always valid - selected from predefined options)
            key_size = int(self.key_size_combo.currentText())
            
            # Generate keys
            self.log_keygen(f"Generating {key_size}-bit RSA key pair (Pure Python)...")
            private_key, public_key = generate_keys(key_size)
            self.log_keygen("✓ Generated RSA key pair")
            
            # Save keys
            self.log_keygen(f"Saving private key to {self.private_key_path}...")
            save_private_key(private_key, self.private_key_path)
            self.log_keygen("✓ Saved private key")
            
            self.log_keygen(f"Saving public key to {self.public_key_path}...")
            save_public_key(public_key, self.public_key_path)
            self.log_keygen("✓ Saved public key")
            
            # Cache keys
            self.private_key = private_key
            self.public_key = public_key
            
            self.log_keygen("\n✓ KEY GENERATION SUCCESSFUL")
            self.log_keygen(f"Keys are ready for signing and verification.")
            
            QMessageBox.information(
                self,
                "Success",
                f"RSA key pair generated successfully!\n\n"
                f"Private Key: {self.private_key_path}\n"
                f"Public Key: {self.public_key_path}"
            )
        
        except RSASignatureError as e:
            self.log_keygen(f"ERROR: {str(e)}")
            QMessageBox.critical(self, "Key Generation Failed", str(e))
        except Exception as e:
            self.log_keygen(f"ERROR: Unexpected error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Unexpected error: {str(e)}")
    
    def on_browse_file_to_sign(self):
        """Browse for file to sign"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select file to sign",
            "",
            "All Files (*.*)"
        )
        if file_path:
            self.sign_file_path.setText(file_path)
    
    def on_sign_file(self):
        """Handle file signing"""
        try:
            self.sign_status.clear()
            
            file_path = self.sign_file_path.text().strip()
            if not file_path:
                self.log_sign("ERROR: No file selected")
                return
            
            # Load private key
            if not self.private_key:
                self.log_sign("Loading private key...")
                self.private_key = load_private_key(self.private_key_path)
            
            self.log_sign(f"Reading file: {file_path}")
            data = read_file(file_path)
            self.log_sign(f"✓ Read {len(data)} bytes")
            
            self.log_sign("Signing file with private key...")
            signature = sign_data(data, self.private_key)
            self.log_sign(f"✓ Signature generated ({len(signature)} bytes)")
            
            # Save signature
            sig_path = file_path + ".sig"
            self.log_sign(f"Saving signature to: {sig_path}")
            write_signature(sig_path, signature)
            self.log_sign("✓ Signature saved")
            
            self.log_sign("\n✓ FILE SIGNING SUCCESSFUL")
            
            QMessageBox.information(
                self,
                "Success",
                f"File signed successfully!\n\n"
                f"Signature saved to: {sig_path}"
            )
        
        except (RSASignatureError, FileHandlerError) as e:
            self.log_sign(f"ERROR: {str(e)}")
            QMessageBox.critical(self, "Signing Failed", str(e))
        except Exception as e:
            self.log_sign(f"ERROR: Unexpected error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Unexpected error: {str(e)}")
    
    def on_browse_file_to_verify(self):
        """Browse for original file to verify"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select original file to verify",
            "",
            "All Files (*.*)"
        )
        if file_path:
            self.verify_file_path.setText(file_path)
    
    def on_browse_signature_file(self):
        """Browse for signature file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select signature file (.sig)",
            "",
            "Signature Files (*.sig);;All Files (*.*)"
        )
        if file_path:
            self.sig_file_path.setText(file_path)
    
    def on_verify_signature(self):
        """Handle signature verification"""
        try:
            self.verify_result.clear()
            
            file_path = self.verify_file_path.text().strip()
            sig_path = self.sig_file_path.text().strip()
            
            if not file_path:
                self.log_verify("ERROR: No file selected")
                return
            if not sig_path:
                self.log_verify("ERROR: No signature file selected")
                return
            
            # Load public key
            if not self.public_key:
                self.log_verify("Loading public key...")
                self.public_key = load_public_key(self.public_key_path)
            
            self.log_verify(f"Reading file: {file_path}")
            data = read_file(file_path)
            self.log_verify(f"✓ Read {len(data)} bytes")
            
            self.log_verify(f"Reading signature: {sig_path}")
            signature = read_signature(sig_path)
            self.log_verify(f"✓ Read signature ({len(signature)} bytes)")
            
            self.log_verify("Verifying signature...")
            is_valid = verify_signature(data, signature, self.public_key)
            
            if is_valid:
                self.log_verify("\n✓ SIGNATURE VERIFIED")
                self.log_verify("File is authentic and has not been tampered.")
                self.highlight_result(True)
            else:
                self.log_verify("\n✗ SIGNATURE INVALID")
                self.log_verify("File has been modified or wrong public key used.")
                self.highlight_result(False)
        
        except (RSASignatureError, FileHandlerError) as e:
            self.log_verify(f"ERROR: {str(e)}")
            QMessageBox.critical(self, "Verification Failed", str(e))
        except Exception as e:
            self.log_verify(f"ERROR: Unexpected error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Unexpected error: {str(e)}")
    
    # ===== Helper Methods =====
    
    def log_keygen(self, message: str):
        """Append message to keygen status"""
        current = self.keygen_status.toPlainText()
        self.keygen_status.setText(current + message + "\n")
        self.keygen_status.verticalScrollBar().setValue(
            self.keygen_status.verticalScrollBar().maximum()
        )
    
    def log_sign(self, message: str):
        """Append message to sign status"""
        current = self.sign_status.toPlainText()
        self.sign_status.setText(current + message + "\n")
        self.sign_status.verticalScrollBar().setValue(
            self.sign_status.verticalScrollBar().maximum()
        )
    
    def log_verify(self, message: str):
        """Append message to verify status"""
        current = self.verify_result.toPlainText()
        self.verify_result.setText(current + message + "\n")
        self.verify_result.verticalScrollBar().setValue(
            self.verify_result.verticalScrollBar().maximum()
        )
    
    def highlight_result(self, is_valid: bool):
        """Highlight result in green or red"""
        if is_valid:
            self.verify_result.setStyleSheet("background-color: #90EE90;")
        else:
            self.verify_result.setStyleSheet("background-color: #FFB6C6;")
