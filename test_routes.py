#!/usr/bin/env python3
"""
Test script to verify all routes are working correctly
"""

import requests
import time

def test_routes():
    base_url = "http://127.0.0.1:5000"
    
    print("🌾 Testing AgriTech Routes...")
    print("=" * 50)
    
    # Test main landing page
    print("\n1. Testing Main Landing Page...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Main page: {response.status_code}")
        if "AgriTech" in response.text:
            print("   ✅ Landing page content found")
        else:
            print("   ❌ Landing page content not found")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test debug routes
    print("\n2. Testing Debug Routes...")
    debug_routes = [
        "/test-crop-recommendation",
        "/test-crop-yield", 
        "/test-disease"
    ]
    
    for route in debug_routes:
        try:
            response = requests.get(f"{base_url}{route}")
            print(f"✅ {route}: {response.status_code} - {response.text[:50]}...")
        except Exception as e:
            print(f"   ❌ {route}: Error - {e}")
    
    # Test blueprint routes
    print("\n3. Testing Blueprint Routes...")
    blueprint_routes = [
        "/crop-recommendation/",
        "/crop-yield/",
        "/disease/"
    ]
    
    for route in blueprint_routes:
        try:
            response = requests.get(f"{base_url}{route}")
            print(f"✅ {route}: {response.status_code}")
            if response.status_code == 200:
                if "Crop Recommendation" in response.text:
                    print("   ✅ Crop Recommendation page detected")
                elif "Crop Yield" in response.text:
                    print("   ✅ Crop Yield page detected")
                elif "Disease Prediction" in response.text:
                    print("   ✅ Disease Prediction page detected")
                else:
                    print("   ❓ Unknown page content")
        except Exception as e:
            print(f"   ❌ {route}: Error - {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Route Testing Complete!")

if __name__ == "__main__":
    print("Make sure the Flask app is running on http://127.0.0.1:5000")
    print("Press Enter to start testing...")
    input()
    test_routes() 