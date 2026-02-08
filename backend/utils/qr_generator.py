import qrcode
import io
import base64
from PIL import Image

class QRGenerator:
    @staticmethod
    def generate_batch_qr(batch_id, base_url="https://agritech.com/trace/"):
        """
        Generate a QR code for a supply batch.
        Contains the URL to the public traceability page.
        Returns a base64 encoded PNG string.
        """
        trace_url = f"{base_url}{batch_id}"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(trace_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to buffer
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        qr_bytes = buf.getvalue()
        
        # Convert to base64
        qr_base64 = base64.b64encode(qr_bytes).decode('utf-8')
        return f"data:image/png;base64,{qr_base64}"

    @staticmethod
    def generate_qr_image(data):
        """Generic QR generator returning PIL Image"""
        qr = qrcode.QRCode(box_size=10, border=2)
        qr.add_data(data)
        qr.make(fit=True)
        return qr.make_image(fill_color="#16a34a", back_color="white")
