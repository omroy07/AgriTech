"""
Example script to test the PDF and Email services
Run this to verify everything is working correctly
"""

import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.pdf_service import generate_loan_report
from backend.services.email_service import EmailService, send_loan_report_email


def test_pdf_generation():
    """Test PDF generation without email"""
    print("=" * 60)
    print("TEST 1: PDF Generation")
    print("=" * 60)
    
    # Sample farmer data
    farmer_data = {
        "name": "Rajesh Kumar",
        "loan_type": "Crop Cultivation Loan",
        "land_size": "5 acres",
        "annual_income": "₹3,00,000",
        "crop_type": "Wheat & Rice",
        "state": "Punjab",
        "district": "Ludhiana",
        "age": "42",
        "farming_experience": "20 years",
        "existing_loans": "None",
        "collateral": "Land documents available"
    }
    
    # Sample AI assessment result
    assessment_result = """
## Loan Type
Crop Cultivation Loan

## Eligibility Status
**Eligible** - Based on your profile, you qualify for agricultural loans from multiple sources.

## Loan Range
- **Minimum:** ₹50,000
- **Maximum:** ₹3,00,000
- **Recommended:** ₹1,50,000 to ₹2,00,000

Your land holdings and farming experience support this loan range.

## Strengths
- **Adequate land size** (5 acres) suitable for cultivation loans
- **Good annual income** showing financial stability
- **No existing loans** - clean credit profile
- **Extensive farming experience** (20 years)
- **Proper documentation** available

## Areas for Improvement
- Consider getting a **Kisan Credit Card (KCC)** for easier future access to credit
- Maintain records of **crop yield and sales** for better loan assessment
- Get your land **surveyed and valued** officially
- Consider **soil health card** for better crop planning

## Applicable Government Schemes

### Recommended Schemes:
1. **Kisan Credit Card (KCC) Scheme**
   - Easy access to credit for crop cultivation
   - Interest subvention of 3%
   - No collateral for loans up to ₹1.6 lakhs

2. **PM-KISAN**
   - Direct income support of ₹6,000 per year
   - Three installments of ₹2,000 each

3. **PMFBY (Pradhan Mantri Fasal Bima Yojana)**
   - Comprehensive crop insurance
   - Protection against crop loss

4. **NABARD Schemes**
   - Lower interest rates for agricultural loans
   - Special schemes for wheat and rice cultivation

### Banking Options:
- **State Bank of India (SBI)** - Agricultural loan @ 7% interest
- **Punjab National Bank (PNB)** - Special schemes for Punjab farmers
- **HDFC Bank** - Agri Business loans with flexible repayment
- **Local Cooperative Banks** - Community-based lending

## Next Steps
1. Visit your nearest bank with land documents
2. Apply for Kisan Credit Card first
3. Get land valuation done officially
4. Prepare last 2 years' income proof
5. Apply for PM-KISAN if not already enrolled

**Note:** Interest rates and schemes are subject to change. Please verify current terms with the bank.
"""
    
    try:
        # Generate PDF
        pdf_path = generate_loan_report(
            farmer_data=farmer_data,
            assessment_result=assessment_result,
            farmer_email="test@example.com"
        )
        
        print(f"\n✅ SUCCESS: PDF generated successfully!")
        print(f"📄 File location: {pdf_path}")
        print(f"📁 File size: {os.path.getsize(pdf_path) / 1024:.2f} KB")
        print(f"\nYou can open this file to verify the PDF contents.")
        
        return True, pdf_path
    
    except Exception as e:
        print(f"\n❌ ERROR: Failed to generate PDF")
        print(f"Error details: {str(e)}")
        return False, None


def test_email_connection():
    """Test email SMTP connection"""
    print("\n" + "=" * 60)
    print("TEST 2: Email Connection")
    print("=" * 60)
    
    email_service = EmailService()
    
    # Check if credentials are configured
    if not email_service.smtp_username or not email_service.smtp_password:
        print("\n⚠️  WARNING: Email credentials not configured")
        print("Please set SMTP_USERNAME and SMTP_PASSWORD in your .env file")
        print("\nFor Gmail:")
        print("1. Enable 2-factor authentication")
        print("2. Generate an App Password")
        print("3. Use that password in SMTP_PASSWORD")
        return False
    
    print(f"\nTesting connection to: {email_service.smtp_host}:{email_service.smtp_port}")
    print(f"Username: {email_service.smtp_username}")
    
    success, message = email_service.test_connection()
    
    if success:
        print(f"\n✅ SUCCESS: {message}")
        return True
    else:
        print(f"\n❌ ERROR: {message}")
        print("\nTroubleshooting:")
        print("- Verify SMTP_USERNAME and SMTP_PASSWORD in .env")
        print("- For Gmail, use App Password, not regular password")
        print("- Check if firewall is blocking SMTP port")
        return False


def test_email_sending(pdf_path):
    """Test sending email with PDF attachment"""
    print("\n" + "=" * 60)
    print("TEST 3: Email Sending with PDF")
    print("=" * 60)
    
    if not pdf_path or not os.path.exists(pdf_path):
        print("\n⚠️  Skipping: No PDF file available to send")
        return False
    
    # Ask for test email
    print("\nThis will send a test email with the generated PDF.")
    test_email = input("Enter your email address to receive test email (or press Enter to skip): ").strip()
    
    if not test_email or '@' not in test_email:
        print("Skipping email test.")
        return False
    
    print(f"\nSending test email to: {test_email}")
    
    try:
        success, message = send_loan_report_email(
            recipient_email=test_email,
            recipient_name="Test User",
            pdf_path=pdf_path,
            loan_type="Crop Cultivation Loan"
        )
        
        if success:
            print(f"\n✅ SUCCESS: {message}")
            print(f"📧 Check your inbox at {test_email}")
            return True
        else:
            print(f"\n❌ ERROR: {message}")
            return False
    
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False


def test_celery_task():
    """Test Celery async task (requires Celery worker to be running)"""
    print("\n" + "=" * 60)
    print("TEST 4: Celery Async Task")
    print("=" * 60)
    
    print("\n⚠️  This test requires Celery worker to be running.")
    print("Start Celery worker with:")
    print("  celery -A backend.config.celery_config.celery_app worker --loglevel=info --pool=solo")
    
    proceed = input("\nIs Celery worker running? (y/n): ").strip().lower()
    
    if proceed != 'y':
        print("Skipping Celery test.")
        return False
    
    try:
        from backend.tasks.report_tasks import generate_and_send_report
        
        # Ask for test email
        test_email = input("Enter your email address for async test: ").strip()
        
        if not test_email or '@' not in test_email:
            print("Invalid email. Skipping test.")
            return False
        
        farmer_data = {
            "name": "Async Test User",
            "loan_type": "Test Loan",
            "land_size": "5 acres"
        }
        
        assessment = "## Test Assessment\n\nThis is a test report generated via Celery."
        
        # Trigger async task
        print(f"\nTriggering async task for {test_email}...")
        task = generate_and_send_report.delay(
            farmer_data=farmer_data,
            assessment_result=assessment,
            farmer_email=test_email,
            farmer_name="Async Test User"
        )
        
        print(f"\n✅ Task queued successfully!")
        print(f"Task ID: {task.id}")
        print(f"Task Status: {task.status}")
        print(f"\nCheck your email at {test_email} in a few moments.")
        print(f"Monitor task in Celery worker logs.")
        
        return True
    
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("\nMake sure:")
        print("1. Redis is running")
        print("2. Celery worker is running")
        print("3. All dependencies are installed")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("AgriTech PDF & Email Service Testing")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = {
        'pdf_generation': False,
        'email_connection': False,
        'email_sending': False,
        'celery_task': False
    }
    
    # Test 1: PDF Generation
    results['pdf_generation'], pdf_path = test_pdf_generation()
    
    # Test 2: Email Connection
    results['email_connection'] = test_email_connection()
    
    # Test 3: Email Sending (only if connection works)
    if results['email_connection'] and pdf_path:
        results['email_sending'] = test_email_sending(pdf_path)
    
    # Test 4: Celery Task
    if results['email_connection']:
        results['celery_task'] = test_celery_task()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    passed_count = sum(results.values())
    total_count = len(results)
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    if passed_count == total_count:
        print("\n🎉 All tests passed! The system is ready to use.")
    elif results['pdf_generation']:
        print("\n✅ Basic functionality working. Configure email for full features.")
    else:
        print("\n⚠️  Some tests failed. Please check the error messages above.")


if __name__ == "__main__":
    main()
