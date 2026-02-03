"""
Example Script: Supply Chain Traceability Workflow
Demonstrates the complete flow from farm to shop
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000/api/v1/traceability"
FARMER_TOKEN = "your_farmer_jwt_token_here"
SHOPKEEPER_TOKEN = "your_shopkeeper_jwt_token_here"

# Headers
farmer_headers = {
    "Authorization": f"Bearer {FARMER_TOKEN}",
    "Content-Type": "application/json"
}

shopkeeper_headers = {
    "Authorization": f"Bearer {SHOPKEEPER_TOKEN}",
    "Content-Type": "application/json"
}


def print_section(title):
    """Print section header"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)


def print_response(response):
    """Pretty print API response"""
    try:
        data = response.json()
        print(f"Status Code: {response.status_code}")
        print(json.dumps(data, indent=2))
    except:
        print(f"Status Code: {response.status_code}")
        print(response.text)


def step_1_create_batch():
    """Step 1: Farmer creates a batch"""
    print_section("STEP 1: Farmer Creates Batch")
    
    batch_data = {
        "produce_name": "Organic Tomatoes",
        "produce_type": "vegetable",
        "quantity_kg": 150.5,
        "origin_location": "Green Valley Farm, Punjab",
        "harvest_date": datetime.now().isoformat(),
        "certification": "organic",
        "quality_grade": "A",
        "quality_notes": "Fresh harvest, no defects observed"
    }
    
    print("Creating batch with data:")
    print(json.dumps(batch_data, indent=2))
    print()
    
    response = requests.post(
        f"{BASE_URL}/batches",
        headers=farmer_headers,
        json=batch_data
    )
    
    print_response(response)
    
    if response.status_code == 201:
        data = response.json()
        batch_id = data['data']['batch']['batch_id']
        print(f"\n✓ Batch created successfully!")
        print(f"  Batch ID: {batch_id}")
        print(f"  QR Verification URL: {data['data']['qr_verification_url']}")
        return batch_id
    else:
        print("\n✗ Failed to create batch")
        return None


def step_2_move_to_quality_check(batch_id):
    """Step 2: Farmer moves batch to quality check"""
    print_section("STEP 2: Move to Quality Check")
    
    update_data = {
        "status": "Quality_Check",
        "notes": "Quality inspection completed - Grade A produce",
        "location": "Inspection Facility, Delhi",
        "quality_grade": "A",
        "quality_notes": "Passed all quality standards"
    }
    
    print(f"Updating batch {batch_id}:")
    print(json.dumps(update_data, indent=2))
    print()
    
    response = requests.put(
        f"{BASE_URL}/batches/{batch_id}/status",
        headers=farmer_headers,
        json=update_data
    )
    
    print_response(response)
    
    if response.status_code == 200:
        print(f"\n✓ Batch moved to Quality_Check")
    else:
        print(f"\n✗ Failed to update status")
    
    time.sleep(1)


def step_3_move_to_logistics(batch_id):
    """Step 3: Farmer approves for logistics"""
    print_section("STEP 3: Move to Logistics")
    
    update_data = {
        "status": "Logistics",
        "notes": "Approved for transport to markets",
        "location": "Distribution Center, Delhi"
    }
    
    print(f"Updating batch {batch_id}:")
    print(json.dumps(update_data, indent=2))
    print()
    
    response = requests.put(
        f"{BASE_URL}/batches/{batch_id}/status",
        headers=farmer_headers,
        json=update_data
    )
    
    print_response(response)
    
    if response.status_code == 200:
        print(f"\n✓ Batch moved to Logistics")
    else:
        print(f"\n✗ Failed to update status")
    
    time.sleep(1)


def step_4_receive_at_shop(batch_id):
    """Step 4: Shopkeeper marks batch as received"""
    print_section("STEP 4: Shopkeeper Receives Batch")
    
    update_data = {
        "status": "In_Shop",
        "notes": "Received in excellent condition",
        "location": "City Market Store #5, Mumbai"
    }
    
    print(f"Updating batch {batch_id}:")
    print(json.dumps(update_data, indent=2))
    print()
    
    response = requests.put(
        f"{BASE_URL}/batches/{batch_id}/status",
        headers=shopkeeper_headers,
        json=update_data
    )
    
    print_response(response)
    
    if response.status_code == 200:
        print(f"\n✓ Batch marked as received in shop")
    else:
        print(f"\n✗ Failed to update status")
    
    time.sleep(1)


def step_5_verify_public(batch_id):
    """Step 5: Public verification (no auth required)"""
    print_section("STEP 5: Public QR Verification")
    
    print(f"Verifying batch {batch_id} publicly...")
    print("(This endpoint doesn't require authentication)")
    print()
    
    response = requests.get(f"{BASE_URL}/verify/{batch_id}")
    
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        passport = data['data']['passport']
        
        print("\n" + "-"*60)
        print("TRACEABILITY PASSPORT")
        print("-"*60)
        print(f"Batch ID: {passport['batch_id']}")
        print(f"Produce: {passport['produce']['name']} ({passport['produce']['quantity']}kg)")
        print(f"Type: {passport['produce']['type']}")
        print(f"Origin: {passport['origin']['location']}")
        print(f"Harvest Date: {passport['origin']['harvest_date']}")
        print(f"Quality Grade: {passport['quality']['grade']}")
        print(f"Current Status: {passport['current_status']}")
        
        print("\nSupply Chain Journey:")
        for i, step in enumerate(passport['journey'], 1):
            print(f"\n  {i}. {step['event']} ({step['to_status']})")
            print(f"     Time: {step['timestamp']}")
            print(f"     Handler: {step['handler_role']}")
            if step.get('location'):
                print(f"     Location: {step['location']}")
            if step.get('notes'):
                print(f"     Notes: {step['notes']}")
        
        print("-"*60)
        print("\n✓ Batch verified successfully!")
    else:
        print("\n✗ Verification failed")


def step_6_get_statistics():
    """Step 6: Get statistics"""
    print_section("STEP 6: Farmer Statistics")
    
    response = requests.get(
        f"{BASE_URL}/stats",
        headers=farmer_headers
    )
    
    print_response(response)


def main():
    """Run complete workflow"""
    print("\n" + "="*60)
    print(" AGRITECH SUPPLY CHAIN TRACEABILITY - COMPLETE WORKFLOW")
    print("="*60)
    print("\nThis script demonstrates the complete farm-to-shop journey")
    print("of produce through the traceability system.")
    print("\nPrerequisites:")
    print("  1. Server running at", BASE_URL)
    print("  2. Valid JWT tokens for farmer and shopkeeper")
    print("  3. Database initialized")
    
    input("\nPress Enter to start the workflow...")
    
    # Execute workflow
    batch_id = step_1_create_batch()
    
    if not batch_id:
        print("\n✗ Workflow failed: Could not create batch")
        return
    
    input("\nPress Enter to continue to quality check...")
    step_2_move_to_quality_check(batch_id)
    
    input("\nPress Enter to continue to logistics...")
    step_3_move_to_logistics(batch_id)
    
    input("\nPress Enter to receive at shop...")
    step_4_receive_at_shop(batch_id)
    
    input("\nPress Enter to verify publicly...")
    step_5_verify_public(batch_id)
    
    input("\nPress Enter to view statistics...")
    step_6_get_statistics()
    
    print("\n" + "="*60)
    print(" WORKFLOW COMPLETED!")
    print("="*60)
    print(f"\nBatch ID: {batch_id}")
    print(f"Public verification URL: http://localhost:5000/verify-produce.html?batch={batch_id}")
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
