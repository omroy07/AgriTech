"""
Optimized Supply Chain Traceability Workflow
Refactored for: Security, DRY principles, and Connection Pooling.
"""

import os
import requests
import json
import time
from datetime import datetime
from requests.exceptions import RequestException

# --- CONFIGURATION ---
# It is recommended to set these in your terminal/environment:
# export FARMER_TOKEN="your_token"
# export SHOPKEEPER_TOKEN="your_token"
BASE_URL = os.getenv("TRACE_API_URL", "http://localhost:5000/api/v1/traceability")
FARMER_TOKEN = os.getenv("FARMER_TOKEN", "your_farmer_jwt_token_here")
SHOPKEEPER_TOKEN = os.getenv("SHOPKEEPER_TOKEN", "your_shopkeeper_jwt_token_here")

class TraceabilityClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def _get_auth_header(self, role="farmer"):
        token = FARMER_TOKEN if role == "farmer" else SHOPKEEPER_TOKEN
        return {"Authorization": f"Bearer {token}"}

    def _handle_request(self, method, endpoint, data=None, role="farmer", auth_required=True):
        """Unified request handler with error management"""
        url = f"{BASE_URL}/{endpoint}"
        headers = self._get_auth_header(role) if auth_required else {}
        
        try:
            response = self.session.request(method, url, json=data, headers=headers)
            # This will trigger an exception for 4xx or 5xx errors
            response.raise_for_status() 
            return response.json()
        except RequestException as e:
            print(f"\n[!] API Error during {method} {endpoint}")
            if e.response is not None:
                print(f"    Status: {e.response.status_code}")
                print(f"    Message: {e.response.text}")
            else:
                print(f"    Error: {str(e)}")
            return None

    def print_divider(self, title):
        print("\n" + "="*60)
        print(f" {title.upper()}")
        print("="*60)

    # --- WORKFLOW STEPS ---

    def create_batch(self):
        self.print_divider("Step 1: Farmer Creates Batch")
        payload = {
            "produce_name": "Organic Tomatoes",
            "produce_type": "vegetable",
            "quantity_kg": 150.5,
            "origin_location": "Green Valley Farm, Punjab",
            "harvest_date": datetime.now().isoformat(),
            "certification": "organic",
            "quality_grade": "A",
            "quality_notes": "Fresh harvest, no defects observed"
        }
        
        result = self._handle_request("POST", "batches", data=payload)
        if result:
            batch_id = result['data']['batch']['batch_id']
            print(f"✓ Batch Created: {batch_id}")
            return batch_id
        return None

    def update_batch_status(self, batch_id, status, location, notes, role="farmer"):
        """Generic status updater to replace repetitive step functions"""
        self.print_divider(f"Transitioning to: {status}")
        payload = {
            "status": status,
            "location": location,
            "notes": notes
        }
        
        # Merge quality notes if moving to Quality Check
        if status == "Quality_Check":
            payload.update({"quality_grade": "A", "quality_notes": "Passed all standards"})

        result = self._handle_request("PUT", f"batches/{batch_id}/status", data=payload, role=role)
        if result:
            print(f"✓ Status successfully updated to {status}")
            return True
        return False

    def public_verify(self, batch_id):
        self.print_divider("Step 5: Public QR Verification")
        result = self._handle_request("GET", f"verify/{batch_id}", auth_required=False)
        
        if result:
            p = result['data']['passport']
            print(f"TRACEABILITY PASSPORT FOR: {p['produce']['name']}")
            print(f"Current Status: {p['current_status']}")
            print(f"Origin: {p['origin']['location']}")
            print("\nJourney History:")
            for step in p['journey']:
                print(f" - [{step['timestamp']}] {step['to_status']} @ {step.get('location', 'N/A')}")
            return True
        return False

    def get_stats(self):
        self.print_divider("Step 6: Farmer Statistics")
        result = self._handle_request("GET", "stats")
        if result:
            print(json.dumps(result, indent=2))

# --- MAIN EXECUTION ---

def main():
    client = TraceabilityClient()
    
    print("\nAGRITECH SUPPLY CHAIN SYSTEM")
    print("Initializing automated workflow...")
    
    # 1. Create
    batch_id = client.create_batch()
    if not batch_id:
        print("Workflow aborted: Failed to create initial batch.")
        return

    # 2. Quality Check
    time.sleep(1)
    if not client.update_batch_status(batch_id, "Quality_Check", "Inspection Facility, Delhi", "Grade A confirmed"):
        return

    # 3. Logistics
    time.sleep(1)
    if not client.update_batch_status(batch_id, "Logistics", "Distribution Center, Delhi", "In Transit"):
        return

    # 4. Receive (Shopkeeper Role)
    time.sleep(1)
    if not client.update_batch_status(batch_id, "In_Shop", "City Market Store #5, Mumbai", "Goods Received", role="shopkeeper"):
        return

    # 5. Public Verification
    client.public_verify(batch_id)

    # 6. Stats
    client.get_stats()

    print("\n" + "="*60)
    print(" WORKFLOW COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()