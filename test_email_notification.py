"""
Test script to trigger email notifications for Anil Kumar M
This will test the email notification system by creating an onboarding event
"""

import requests
import json
from datetime import datetime
import sys
import io

# Set UTF-8 encoding for console output on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# API endpoint
API_URL = "http://localhost:8050/api/realtime-stage-trigger"

# Create onboarding event for Anil Kumar M
onboarding_data = {
    "stage_name": "onboarding_initiated",
    "workflow_type": "onboarding",
    "employee_id": "EMP1001",
    "employee_name": "Anil Kumar M",
    "employee_email": "manilkumar1909@gmail.com",
    "manager_email": "manager@example.com",
    "pmo_email": "pmo@example.com",
    "dsp_reviewer_email": "dsp@example.com",
    "department": "Data Engineering",
    "role": "Data Engineer",
    "joining_date": datetime.now().strftime("%Y-%m-%d"),
    "project_name": "Workforce Orchestrator",
    "client_name": "Internal",
    "bcg_required": True,
    "bcg_vendor": "First Advantage",
    "bcg_reference_id": f"BCG-EMP1001-{datetime.now().strftime('%Y%m%d')}",
    "requested_assets": [
        "laptop",
        "id_card",
        "mail_id",
        "welcome_kit"
    ]
}

print("=" * 60)
print("Testing Email Notification System")
print("=" * 60)
print(f"\nSending onboarding request for: {onboarding_data['employee_name']}")
print(f"Email: {onboarding_data['employee_email']}")
print(f"Position: {onboarding_data['role']}")
print(f"Department: {onboarding_data['department']}")
print("\nThis will trigger the following emails:")
print("1. Welcome email to employee")
print("2. BGC initiation email with portal link")
print("\n" + "=" * 60)

try:
    # Send POST request to trigger onboarding
    response = requests.post(API_URL, json=onboarding_data)
    
    if response.status_code == 200:
        result = response.json()
        print("\n[SUCCESS] Onboarding request successful!")
        print(f"\nResponse:")
        print(json.dumps(result, indent=2))
        
        print("\n" + "=" * 60)
        print("Email Notification Status:")
        print("=" * 60)
        print("\nPlease check the following:")
        print(f"1. Email inbox for: {onboarding_data['employee_email']}")
        print("2. Check for Welcome email")
        print("3. Check for BGC Initiation email with portal link")
        print("4. Check workforce orchestrator terminal for email logs")
        print("\n" + "=" * 60)
        
    else:
        print(f"\n[ERROR] Status code: {response.status_code}")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("\n[ERROR] Could not connect to API")
    print("Make sure workforce_orchestrator.py is running on port 8050")
    print("Run: python scripts/workforce_orchestrator.py --serve-api 8050")
    
except Exception as e:
    print(f"\n[ERROR] {str(e)}")

print("\n" + "=" * 60)

# Made with Bob
