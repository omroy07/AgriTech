"""
Email Service for sending PDF reports
Supports SMTP email delivery with attachments
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.utils import formataddr
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class EmailService:
    """Email service for sending reports via SMTP"""
    
    def __init__(self):
        """Initialize email service with configuration from environment variables"""
        self.smtp_host = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        self.smtp_username = os.environ.get('SMTP_USERNAME', '')
        self.smtp_password = os.environ.get('SMTP_PASSWORD', '')
        self.sender_email = os.environ.get('SENDER_EMAIL', self.smtp_username)
        self.sender_name = os.environ.get('SENDER_NAME', 'AgriTech Loan Services')
        
        # Validate configuration
        if not self.smtp_username or not self.smtp_password:
            print("⚠ Warning: Email credentials not configured. Set SMTP_USERNAME and SMTP_PASSWORD in .env")
    
    def send_loan_report(self, recipient_email, recipient_name, pdf_path, loan_type='Agricultural Loan'):
        """
        Send loan eligibility report via email
        
        Args:
            recipient_email: Email address of recipient
            recipient_name: Name of recipient
            pdf_path: Path to PDF report file
            loan_type: Type of loan applied for
        
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Validate inputs
            if not os.path.exists(pdf_path):
                return False, f"PDF file not found: {pdf_path}"
            
            if not recipient_email or '@' not in recipient_email:
                return False, "Invalid recipient email address"
            
            # Create message
            message = MIMEMultipart()
            message['From'] = formataddr((self.sender_name, self.sender_email))
            message['To'] = recipient_email
            message['Subject'] = f"Your {loan_type} Eligibility Report - AgriTech"
            
            # Email body (HTML)
            html_body = f"""
            <html>
                <head>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            line-height: 1.6;
                            color: #333;
                        }}
                        .container {{
                            max-width: 600px;
                            margin: 0 auto;
                            padding: 20px;
                        }}
                        .header {{
                            background-color: #2E7D32;
                            color: white;
                            padding: 20px;
                            text-align: center;
                            border-radius: 5px 5px 0 0;
                        }}
                        .content {{
                            background-color: #f9f9f9;
                            padding: 30px;
                            border: 1px solid #ddd;
                            border-radius: 0 0 5px 5px;
                        }}
                        .highlight {{
                            background-color: #E8F5E9;
                            padding: 15px;
                            border-left: 4px solid #2E7D32;
                            margin: 20px 0;
                        }}
                        .footer {{
                            text-align: center;
                            margin-top: 30px;
                            padding-top: 20px;
                            border-top: 1px solid #ddd;
                            font-size: 12px;
                            color: #666;
                        }}
                        .button {{
                            display: inline-block;
                            padding: 12px 30px;
                            background-color: #2E7D32;
                            color: white;
                            text-decoration: none;
                            border-radius: 5px;
                            margin-top: 20px;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>🌾 AgriTech Loan Services</h1>
                        </div>
                        <div class="content">
                            <h2>Dear {recipient_name},</h2>
                            
                            <p>Thank you for using AgriTech's loan eligibility assessment service.</p>
                            
                            <div class="highlight">
                                <strong>Your {loan_type} eligibility report is ready!</strong><br>
                                Please find the detailed PDF report attached to this email.
                            </div>
                            
                            <p>The attached report contains:</p>
                            <ul>
                                <li>Comprehensive loan eligibility assessment</li>
                                <li>Your application details</li>
                                <li>Loan amount range recommendations</li>
                                <li>Areas for improvement</li>
                                <li>Applicable government schemes and subsidies</li>
                            </ul>
                            
                            <p><strong>Next Steps:</strong></p>
                            <ol>
                                <li>Review the attached PDF report carefully</li>
                                <li>Prepare the required documents mentioned in the report</li>
                                <li>Visit your nearest bank or financial institution</li>
                                <li>Present this report along with your documents</li>
                            </ol>
                            
                            <p><em>Note: This assessment is indicative and based on the information provided. 
                            Final loan approval is subject to document verification and the lending institution's policies.</em></p>
                            
                            <div class="footer">
                                <p><strong>AgriTech - Empowering Farmers with Technology</strong></p>
                                <p>Report Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                                <p>This is an automated email. Please do not reply to this message.</p>
                            </div>
                        </div>
                    </div>
                </body>
            </html>
            """
            
            # Attach HTML body
            message.attach(MIMEText(html_body, 'html'))
            
            # Attach PDF file
            with open(pdf_path, 'rb') as pdf_file:
                pdf_attachment = MIMEApplication(pdf_file.read(), _subtype='pdf')
                pdf_attachment.add_header(
                    'Content-Disposition', 
                    'attachment', 
                    filename=os.path.basename(pdf_path)
                )
                message.attach(pdf_attachment)
            
            # Send email
            print(f"📧 Connecting to SMTP server: {self.smtp_host}:{self.smtp_port}")
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()  # Secure the connection
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(message)
            
            print(f"✓ Email sent successfully to {recipient_email}")
            return True, f"Report sent successfully to {recipient_email}"
            
        except smtplib.SMTPAuthenticationError:
            error_msg = "Email authentication failed. Please check SMTP credentials."
            print(f"✗ {error_msg}")
            return False, error_msg
        
        except smtplib.SMTPException as e:
            error_msg = f"SMTP error occurred: {str(e)}"
            print(f"✗ {error_msg}")
            return False, error_msg
        
        except Exception as e:
            error_msg = f"Failed to send email: {str(e)}"
            print(f"✗ {error_msg}")
            return False, error_msg
    
    def send_simple_email(self, recipient_email, subject, body_text, body_html=None):
        """
        Send a simple email without attachments
        
        Args:
            recipient_email: Email address of recipient
            subject: Email subject
            body_text: Plain text body
            body_html: Optional HTML body
        
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            message = MIMEMultipart('alternative')
            message['From'] = formataddr((self.sender_name, self.sender_email))
            message['To'] = recipient_email
            message['Subject'] = subject
            
            # Attach plain text
            message.attach(MIMEText(body_text, 'plain'))
            
            # Attach HTML if provided
            if body_html:
                message.attach(MIMEText(body_html, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(message)
            
            print(f"✓ Email sent successfully to {recipient_email}")
            return True, f"Email sent successfully to {recipient_email}"
            
        except Exception as e:
            error_msg = f"Failed to send email: {str(e)}"
            print(f"✗ {error_msg}")
            return False, error_msg
    
    def test_connection(self):
        """
        Test SMTP connection
        
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
            
            return True, "SMTP connection successful"
        
        except Exception as e:
            return False, f"SMTP connection failed: {str(e)}"


# Convenience function
def send_loan_report_email(recipient_email, recipient_name, pdf_path, loan_type='Agricultural Loan'):
    """
    Convenience function to send loan report email
    
    Args:
        recipient_email: Email address of recipient
        recipient_name: Name of recipient
        pdf_path: Path to PDF report file
        loan_type: Type of loan applied for
    
    Returns:
        tuple: (success: bool, message: str)
    """
    email_service = EmailService()
    return email_service.send_loan_report(recipient_email, recipient_name, pdf_path, loan_type)
