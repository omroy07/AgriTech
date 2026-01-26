"""
Celery Tasks for Report Generation and Email Delivery
Handles async PDF generation and email sending
"""

from backend.config.celery_config import celery_app
from backend.services.pdf_service import generate_loan_report
from backend.services.email_service import send_loan_report_email
import os
import traceback


@celery_app.task(name='generate_and_send_report', bind=True, max_retries=3)
def generate_and_send_report(self, farmer_data, assessment_result, farmer_email, farmer_name=None):
    """
    Complete workflow: Generate PDF report and send via email
    
    Args:
        self: Task instance (for retries)
        farmer_data: Dictionary containing farmer application data
        assessment_result: AI-generated assessment text
        farmer_email: Email address of the farmer
        farmer_name: Name of the farmer (optional)
    
    Returns:
        dict: Status and message
    """
    try:
        print(f"🚀 Starting report generation task for {farmer_email}")
        
        # Step 1: Generate PDF
        print("📄 Generating PDF report...")
        pdf_path = generate_loan_report(farmer_data, assessment_result, farmer_email)
        
        if not os.path.exists(pdf_path):
            raise Exception("PDF generation failed - file not found")
        
        print(f"✓ PDF generated successfully: {pdf_path}")
        
        # Step 2: Send Email
        print("📧 Sending email...")
        recipient_name = farmer_name or farmer_data.get('name', 'Valued Farmer')
        loan_type = farmer_data.get('loan_type', 'Agricultural Loan')
        
        success, message = send_loan_report_email(
            recipient_email=farmer_email,
            recipient_name=recipient_name,
            pdf_path=pdf_path,
            loan_type=loan_type
        )
        
        if not success:
            raise Exception(f"Email sending failed: {message}")
        
        print(f"✓ Email sent successfully to {farmer_email}")
        
        # Step 3: Cleanup (optional - keep for records or delete)
        # os.remove(pdf_path)  # Uncomment to delete after sending
        
        return {
            'status': 'success',
            'message': f'Report generated and sent to {farmer_email}',
            'pdf_path': pdf_path,
            'email_sent': True
        }
    
    except Exception as e:
        error_msg = f"Error in generate_and_send_report: {str(e)}"
        print(f"✗ {error_msg}")
        traceback.print_exc()
        
        # Retry logic
        try:
            # Retry with exponential backoff
            raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
        except self.MaxRetriesExceededError:
            return {
                'status': 'failed',
                'message': error_msg,
                'retries_exceeded': True
            }


@celery_app.task(name='generate_pdf_report')
def generate_pdf_report(farmer_data, assessment_result, farmer_email):
    """
    Generate PDF report only (without sending email)
    
    Args:
        farmer_data: Dictionary containing farmer application data
        assessment_result: AI-generated assessment text
        farmer_email: Email address of the farmer
    
    Returns:
        dict: Status and PDF path
    """
    try:
        print(f"📄 Generating PDF report for {farmer_email}")
        
        pdf_path = generate_loan_report(farmer_data, assessment_result, farmer_email)
        
        if not os.path.exists(pdf_path):
            raise Exception("PDF generation failed - file not found")
        
        print(f"✓ PDF generated successfully: {pdf_path}")
        
        return {
            'status': 'success',
            'message': 'PDF report generated successfully',
            'pdf_path': pdf_path
        }
    
    except Exception as e:
        error_msg = f"Error generating PDF: {str(e)}"
        print(f"✗ {error_msg}")
        traceback.print_exc()
        
        return {
            'status': 'failed',
            'message': error_msg
        }


@celery_app.task(name='send_email_report', bind=True, max_retries=3)
def send_email_report(self, recipient_email, recipient_name, pdf_path, loan_type='Agricultural Loan'):
    """
    Send email with PDF attachment
    
    Args:
        self: Task instance (for retries)
        recipient_email: Email address of recipient
        recipient_name: Name of recipient
        pdf_path: Path to PDF file
        loan_type: Type of loan
    
    Returns:
        dict: Status and message
    """
    try:
        print(f"📧 Sending email to {recipient_email}")
        
        if not os.path.exists(pdf_path):
            raise Exception(f"PDF file not found: {pdf_path}")
        
        success, message = send_loan_report_email(
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            pdf_path=pdf_path,
            loan_type=loan_type
        )
        
        if not success:
            raise Exception(message)
        
        print(f"✓ Email sent successfully to {recipient_email}")
        
        return {
            'status': 'success',
            'message': message,
            'email_sent': True
        }
    
    except Exception as e:
        error_msg = f"Error sending email: {str(e)}"
        print(f"✗ {error_msg}")
        
        # Retry logic
        try:
            raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
        except self.MaxRetriesExceededError:
            return {
                'status': 'failed',
                'message': error_msg,
                'retries_exceeded': True
            }


@celery_app.task(name='batch_generate_reports')
def batch_generate_reports(applications_list):
    """
    Generate and send reports for multiple applications
    
    Args:
        applications_list: List of application dictionaries, each containing:
            - farmer_data
            - assessment_result
            - farmer_email
            - farmer_name (optional)
    
    Returns:
        dict: Batch processing results
    """
    results = {
        'total': len(applications_list),
        'successful': 0,
        'failed': 0,
        'details': []
    }
    
    for application in applications_list:
        try:
            result = generate_and_send_report.delay(
                farmer_data=application['farmer_data'],
                assessment_result=application['assessment_result'],
                farmer_email=application['farmer_email'],
                farmer_name=application.get('farmer_name')
            )
            
            results['successful'] += 1
            results['details'].append({
                'email': application['farmer_email'],
                'status': 'queued',
                'task_id': result.id
            })
            
        except Exception as e:
            results['failed'] += 1
            results['details'].append({
                'email': application.get('farmer_email', 'unknown'),
                'status': 'failed',
                'error': str(e)
            })
    
    return results
