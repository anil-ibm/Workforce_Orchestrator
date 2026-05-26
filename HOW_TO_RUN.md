# How to Run Workforce Orchestrator

## Prerequisites

1. **Python 3.7+** installed on your system
2. **Required Python packages** (install using pip)

## Installation Steps

### Step 1: Install Dependencies

Open PowerShell or Command Prompt in the project directory and run:

```powershell
pip install -r requirements.txt
```

This installs:
- `msal>=1.30.0` (for Microsoft authentication)
- `requests>=2.32.0` (for HTTP requests)

### Step 2: Configure Gmail SMTP (Optional)

If you want to send actual emails, edit `config/workflow_config.json`:

```json
{
  "gmail_smtp": {
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your-email@gmail.com",
    "sender_password": "your-app-password",
    "use_tls": true
  }
}
```

**To get Gmail App Password:**
1. Enable 2-Step Verification on your Gmail account
2. Go to Google Account → Security → 2-Step Verification → App passwords
3. Generate a new app password for "Mail"
4. Use that 16-character password in the config

**Note:** If you don't configure Gmail, the workflow will still run but skip email delivery.

## Running the Code

### Method 1: Process Onboarding Event

```powershell
python scripts/workforce_orchestrator.py samples/onboarding_event.json
```

**What it does:**
- Processes a new employee onboarding
- Creates workflow record
- Assigns assets (laptop, mail ID, welcome kit, etc.)
- Tracks BGC (Background Check) if required
- Generates email notifications
- Updates employee and asset records

**Output:**
```json
{
  "workflow_id": "unique-id",
  "workflow_type": "onboarding",
  "status": "completed",
  "current_stage": "Onboarded",
  "employee_id": "EMP003",
  "notifications_generated": 22
}
```

### Method 2: Process Offboarding Event

```powershell
python scripts/workforce_orchestrator.py samples/offboarding_event.json
```

**What it does:**
- Processes employee exit
- Returns assigned assets
- Tracks missing assets
- Revokes access
- Generates exit notifications
- Updates employee status to inactive

### Method 3: Start Realtime API Server

```powershell
python scripts/workforce_orchestrator.py --serve-api 8050
```

**What it does:**
- Starts HTTP server on port 8050
- Provides REST API endpoints:
  - `POST /api/realtime-stage-trigger` - Trigger stage-specific notifications
  - `POST /api/chatbot` - Query dashboard assistant

**Example API Usage:**

```powershell
# Trigger BGC completion notification
curl -X POST http://127.0.0.1:8050/api/realtime-stage-trigger -H "Content-Type: application/json" -d '{
  "stage_name": "bgc_completed",
  "employee_id": "EMP003",
  "employee_name": "Anil Kumar",
  "employee_email": "anil.kumar@example.com",
  "manager_email": "manager.ops@example.com",
  "pmo_email": "pmo.macquarie@example.com",
  "dsp_reviewer_email": "dsp.reviewer@example.com"
}'
```

### Method 4: Open Dashboard UI

Simply open `dashboard.html` in a web browser:

```powershell
start dashboard.html
```

**Features:**
- View candidate screening status
- Track onboarding/offboarding workflows
- Monitor asset assignments
- Trigger realtime notifications
- Chat with workflow assistant

## Custom Event Files

### Create Onboarding Event

Create a JSON file (e.g., `my_onboarding.json`):

```json
{
  "workflow_type": "onboarding",
  "employee_id": "EMP004",
  "employee_name": "John Doe",
  "employee_email": "john.doe@example.com",
  "manager_email": "manager@example.com",
  "pmo_email": "pmo@example.com",
  "dsp_reviewer_email": "dsp@example.com",
  "department": "Engineering",
  "role": "Software Engineer",
  "joining_date": "2026-06-15",
  "project_name": "Project Alpha",
  "client_name": "Client XYZ",
  "bcg_required": true,
  "bcg_vendor": "Vendor Name",
  "bcg_reference_id": "BGC-REF-123",
  "requested_assets": ["laptop", "id_card", "mail_id", "welcome_kit"]
}
```

Run it:
```powershell
python scripts/workforce_orchestrator.py my_onboarding.json
```

### Create Offboarding Event

Create a JSON file (e.g., `my_offboarding.json`):

```json
{
  "workflow_type": "offboarding",
  "employee_id": "EMP004",
  "employee_name": "John Doe",
  "employee_email": "john.doe@example.com",
  "manager_email": "manager@example.com",
  "pmo_email": "pmo@example.com",
  "dsp_reviewer_email": "dsp@example.com",
  "last_working_date": "2026-12-31",
  "assigned_assets": ["LAP-1002", "ID-3001"]
}
```

Run it:
```powershell
python scripts/workforce_orchestrator.py my_offboarding.json
```

## Output Files

After running workflows, check these files:

1. **`data/workflows.json`** - Complete workflow execution history
2. **`data/employees.json`** - Updated employee records
3. **`data/assets.json`** - Updated asset inventory

## Troubleshooting

### Issue: "Module not found"
**Solution:** Install dependencies
```powershell
pip install -r requirements.txt
```

### Issue: "Email delivery failed"
**Solution:** Either configure Gmail SMTP credentials or ignore the warning (workflow will still complete)

### Issue: "File not found"
**Solution:** Make sure you're running commands from the project root directory:
```powershell
cd c:/Users/SarahSmruthi/Documents/Workforce_Orchestrator-main
```

### Issue: Port 8050 already in use
**Solution:** Use a different port
```powershell
python scripts/workforce_orchestrator.py --serve-api 8051
```

## Quick Start Commands

```powershell
# Navigate to project directory
cd c:/Users/SarahSmruthi/Documents/Workforce_Orchestrator-main

# Install dependencies
pip install -r requirements.txt

# Run onboarding example
python scripts/workforce_orchestrator.py samples/onboarding_event.json

# Run offboarding example
python scripts/workforce_orchestrator.py samples/offboarding_event.json

# Start API server
python scripts/workforce_orchestrator.py --serve-api 8050

# Open dashboard
start dashboard.html
```

## Workflow Stages

### Onboarding Lifecycle:
1. Profile Screening Approved
2. Onboarding Initiated
3. BGC In Progress (if required)
4. BGC Cleared
5. Asset Initiation
6. Onboarded / Ready to Join

### Offboarding Lifecycle:
1. Offboarding Initiated
2. Asset Return
3. Access Revocation
4. Offboarded

## Support

For issues or questions, check:
- `README.md` for project overview
- `config/workflow_config.json` for configuration options
- `samples/` directory for example events