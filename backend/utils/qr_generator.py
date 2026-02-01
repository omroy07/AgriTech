"""
QR Code Generation Utility for Supply Chain Traceability
Generates unique, encrypted QR codes for produce batches with integrity verification
"""

import qrcode
import base64
import hashlib
import hmac
import json
import os
from io import BytesIO
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2


class QRGenerator:
    """
    Handles generation and verification of encrypted QR codes for produce batches.
    Ensures data integrity and tamper detection.
    """
    
    def __init__(self, secret_key=None):
        """
        Initialize QR Generator with encryption key.
        
        Args:
            secret_key: Secret key for encryption. If None, uses environment variable.
        """
        self.secret_key = secret_key or os.environ.get('QR_SECRET_KEY', 'agritech_qr_default_secret_key_2026')
        self.cipher_suite = self._initialize_cipher()
    
    def _initialize_cipher(self):
        """Initialize Fernet cipher for encryption"""
        # Derive a key from the secret using PBKDF2
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'agritech_salt',  # In production, use random salt per batch
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.secret_key.encode()))
        return Fernet(key)
    
    def generate_batch_qr(self, batch_id, produce_name, harvest_date, farmer_id, 
                          origin_location, additional_data=None):
        """
        Generate encrypted QR code for a produce batch.
        
        Args:
            batch_id: Unique batch identifier
            produce_name: Name of the produce
            harvest_date: Date of harvest
            farmer_id: ID of the farmer
            origin_location: Origin location
            additional_data: Optional dict with additional metadata
            
        Returns:
            tuple: (qr_code_image_base64, encrypted_data_string)
        """
        # Prepare data payload
        payload = {
            'batch_id': batch_id,
            'produce_name': produce_name,
            'harvest_date': harvest_date.isoformat() if isinstance(harvest_date, datetime) else harvest_date,
            'farmer_id': farmer_id,
            'origin_location': origin_location,
            'generated_at': datetime.utcnow().isoformat(),
        }
        
        if additional_data:
            payload.update(additional_data)
        
        # Add HMAC signature for integrity verification
        payload['signature'] = self._generate_signature(payload)
        
        # Encrypt the payload
        encrypted_data = self._encrypt_data(payload)
        
        # Generate QR code
        qr_image_base64 = self._create_qr_image(encrypted_data)
        
        return qr_image_base64, encrypted_data
    
    def verify_and_decode_qr(self, encrypted_data):
        """
        Verify and decode encrypted QR code data.
        
        Args:
            encrypted_data: Encrypted data string from QR code
            
        Returns:
            dict: Decrypted payload if valid, None if tampered or invalid
        """
        try:
            # Decrypt data
            payload = self._decrypt_data(encrypted_data)
            
            if not payload:
                return None
            
            # Verify signature
            stored_signature = payload.pop('signature', None)
            calculated_signature = self._generate_signature(payload)
            
            if not stored_signature or not hmac.compare_digest(stored_signature, calculated_signature):
                # Data has been tampered with
                return None
            
            # Restore signature for complete record
            payload['signature'] = stored_signature
            payload['verified'] = True
            
            return payload
        
        except Exception as e:
            print(f"QR verification error: {str(e)}")
            return None
    
    def _encrypt_data(self, data):
        """Encrypt data using Fernet symmetric encryption"""
        json_data = json.dumps(data)
        encrypted = self.cipher_suite.encrypt(json_data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def _decrypt_data(self, encrypted_data):
        """Decrypt data using Fernet symmetric encryption"""
        try:
            decoded = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.cipher_suite.decrypt(decoded)
            return json.loads(decrypted.decode())
        except Exception:
            return None
    
    def _generate_signature(self, data):
        """Generate HMAC signature for data integrity"""
        # Remove signature if present
        data_copy = {k: v for k, v in data.items() if k != 'signature'}
        
        # Create deterministic string representation
        data_string = json.dumps(data_copy, sort_keys=True)
        
        # Generate HMAC
        signature = hmac.new(
            self.secret_key.encode(),
            data_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def _create_qr_image(self, data):
        """
        Create QR code image and return as base64 string.
        
        Args:
            data: Data to encode in QR code
            
        Returns:
            str: Base64 encoded PNG image
        """
        qr = qrcode.QRCode(
            version=1,  # Auto-adjust size
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction
            box_size=10,
            border=4,
        )
        
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    def generate_public_url(self, batch_id, base_url="https://agritech.example.com"):
        """
        Generate public verification URL for QR code.
        
        Args:
            batch_id: Unique batch identifier
            base_url: Base URL of the application
            
        Returns:
            str: Public verification URL
        """
        return f"{base_url}/verify/{batch_id}"
    
    def create_traceability_passport(self, batch_data, audit_logs):
        """
        Create a comprehensive traceability passport document.
        
        Args:
            batch_data: Dictionary with batch information
            audit_logs: List of audit log dictionaries
            
        Returns:
            dict: Formatted passport data
        """
        passport = {
            'batch_id': batch_data.get('batch_id'),
            'produce': {
                'name': batch_data.get('produce_name'),
                'type': batch_data.get('produce_type'),
                'quantity': batch_data.get('quantity_kg'),
                'certification': batch_data.get('certification')
            },
            'origin': {
                'location': batch_data.get('origin_location'),
                'harvest_date': batch_data.get('harvest_date')
            },
            'quality': {
                'grade': batch_data.get('quality_grade'),
                'notes': batch_data.get('quality_notes')
            },
            'journey': [],
            'current_status': batch_data.get('status'),
            'verification': {
                'verified': True,
                'verified_at': datetime.utcnow().isoformat()
            }
        }
        
        # Add audit trail to journey
        for log in audit_logs:
            journey_entry = {
                'timestamp': log.get('timestamp'),
                'event': log.get('event_type'),
                'from_status': log.get('from_status'),
                'to_status': log.get('to_status'),
                'handler_role': log.get('user_role'),
                'location': log.get('location'),
                'notes': log.get('notes')
            }
            passport['journey'].append(journey_entry)
        
        return passport


# Singleton instance
_qr_generator = None

def get_qr_generator():
    """Get or create singleton QR generator instance"""
    global _qr_generator
    if _qr_generator is None:
        _qr_generator = QRGenerator()
    return _qr_generator
