import requests
import json

BASE_URL = "http://localhost:5000"

def test_multilingual_loan_processing():
    print("🚀 Testing Multilingual Support for Loan Processing...")
    
    # Test Data
    payload = {
        "loan_type": "Crop Cultivation",
        "amount": 50000,
        "duration": 12,
        "purpose": "Buying seeds and fertilizer",
        "farm_size": 2.5,
        "crop_type": "Wheat",
        "annual_income": 150000
    }
    
    languages = {
        'en': 'English',
        'hi': 'Hindi',
        'bn': 'Bengali',
        'te': 'Telugu'
    }
    
    for lang_code, lang_name in languages.items():
        print(f"\n--- Testing Language: {lang_name} ({lang_code}) ---")
        headers = {
            'Accept-Language': lang_code,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(f"{BASE_URL}/process-loan", json=payload, headers=headers)
            data = response.json()
            
            if response.status_code == 200:
                print(f"✅ Success Message: {data['message']}")
                print(f"📝 Gemini Response (First 200 chars):")
                print(data['result'][:200] + "...")
            else:
                print(f"❌ Failed: {data}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Make sure the backend is running at http://localhost:5000")

if __name__ == "__main__":
    test_multilingual_loan_processing()
