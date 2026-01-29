import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_notification_system():
    print("🚀 Testing Notification System...")
    
    # 1. Create a test notification via API
    payload = {
        "user_id": 1,
        "title": "Alert: Crop Disease Detected",
        "message": "Symptoms of Blight found in your neighboring area. Please check your fields.",
        "type": "disease_alert"
    }
    
    try:
        print("Step 1: Creating test notification...")
        response = requests.post(f"{BASE_URL}/api/v1/notifications/test", json=payload)
        data = response.json()
        
        if response.status_code == 200 and data['status'] == 'success':
            notification_id = data['notification']['id']
            print(f"✅ Notification created (ID: {notification_id})")
        else:
            print(f"❌ Failed to create notification: {data}")
            return

        # 2. Fetch notifications for user
        print("Step 2: Fetching user notifications...")
        response = requests.get(f"{BASE_URL}/api/v1/notifications/?user_id=1")
        data = response.json()
        
        if response.status_code == 200 and len(data['notifications']) > 0:
            print(f"✅ Found {len(data['notifications'])} notifications")
        else:
            print(f"❌ No notifications found for user 1")

        # 3. Mark as read
        print(f"Step 3: Marking notification {notification_id} as read...")
        response = requests.post(f"{BASE_URL}/api/v1/notifications/{notification_id}/read")
        data = response.json()
        
        if response.status_code == 200 and data['status'] == 'success':
            print("✅ Marked as read successfully")
        else:
            print("❌ Failed to mark as read")

    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        print("Make sure the backend is running at http://localhost:5000")

if __name__ == "__main__":
    test_notification_system()
