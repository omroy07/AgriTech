import requests
import json

BASE_URL = "http://localhost:5000/api/v1/auth"

def test_auth_flow():
    print("🚀 Testing Auth Verification & Reset Flow...")
    
    # 1. Register a test user
    print("Step 1: Registering user...")
    payload = {
        "username": "testfarmer",
        "email": "farmer@example.com",
        "password": "securepassword123"
    }
    response = requests.post(f"{BASE_URL}/register", json=payload)
    print(f"Response: {response.json()['message']}")

    # Note: In a real test we'd need to mock the DB to get the token 
    # since we can't actually "read" the email sent to MailHog easily in this script without more setup.
    print("\n✅ Registration complete. In a full system, you would check MailHog at http://localhost:8025 to see the verification link.")
    
    # 2. Test forgot password
    print("\nStep 2: Requesting password reset...")
    response = requests.post(f"{BASE_URL}/forgot-password", json={"email": "farmer@example.com"})
    print(f"Response: {response.json()['message']}")
    
    print("\n✅ Forgot password requested. Check MailHog for the reset link.")

if __name__ == "__main__":
    test_auth_flow()
