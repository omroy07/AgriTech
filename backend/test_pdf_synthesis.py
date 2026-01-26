import requests
import time
import json

BASE_URL = "http://localhost:5000"

def test_async_loan_pdf_synthesis():
    print("🚀 Testing Async PDF Synthesis...")
    
    # 1. Submit loan processing task
    loan_data = {
        "user_id": 1,
        "loan_type": "Crop Cultivation",
        "amount": 100000,
        "duration": 24,
        "purpose": "Purchase of high-yield seeds and irrigation equipment",
        "farm_size": "5 acres",
        "annual_income": "300000"
    }
    
    print("Step 1: Submitting async loan processing task...")
    response = requests.post(f"{BASE_URL}/api/loan/process-async", json=loan_data)
    
    if response.status_code != 202:
        print(f"❌ Failed to submit task: {response.text}")
        return
        
    task_id = response.json()['task_id']
    print(f"✅ Task submitted! ID: {task_id}")
    
    # 2. Poll for task completion
    print("Step 2: Polling for task results...")
    max_retries = 30
    for i in range(max_retries):
        res = requests.get(f"{BASE_URL}/api/task/{task_id}")
        data = res.json()
        
        if data['status'] == 'success':
            print("✅ Loan Analysis Complete!")
            print("📝 Analysis Preview:", data['result'][:100], "...")
            break
        elif data['status'] == 'failed':
            print(f"❌ Task failed: {data['message']}")
            return
            
        print(f"  ... Still processing ({i+1}/{max_retries})")
        time.sleep(2)
    else:
        print("❌ Polling timed out")
        return

    # 3. Check for generated files
    print("\nStep 3: Checking for generated PDF in FileService...")
    # Wait a bit for the sub-task (PDF synthesis) to finish
    time.sleep(5) 
    
    # We'll use our newly created list_user_files endpoint if it exists
    # If not, we'll try to check by fetching user 1 notifications
    print("Checking notifications for user 1...")
    notif_res = requests.get(f"{BASE_URL}/api/v1/notifications/?user_id=1")
    if notif_res.status_code == 200:
        notifs = notif_res.json()['notifications']
        pdf_notif = next((n for n in notifs if "PDF Report Ready" in n['title']), None)
        if pdf_notif:
            print(f"✅ Found notification: {pdf_notif['message']}")
        else:
            print("❌ No PDF notification found")
    else:
        print("❌ Could not fetch notifications")

    # Final check: see if we can find the file record
    print("\nListing files for user 1...")
    file_res = requests.get(f"{BASE_URL}/api/v1/files/user/1")
    if file_res.status_code == 200:
        files = file_res.json()['files']
        pdf_file = next((f for f in files if f['file_type'] == 'application/pdf'), None)
        if pdf_file:
            print(f"✅ Found PDF file record: {pdf_file['original_name']} ({pdf_file['file_size']} bytes)")
            print(f"🔗 Download Link: {BASE_URL}/api/v1/files/download/{pdf_file['id']}")
        else:
            print("❌ No PDF file record found")
    else:
        print("❌ Could not list files")

if __name__ == "__main__":
    test_async_loan_pdf_synthesis()
