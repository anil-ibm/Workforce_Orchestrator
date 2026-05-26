# Workforce Orchestrator

Automated employee onboarding and offboarding pipeline with:

- employee event intake
- stage-based workflow orchestration
- profile screening to onboarding progression
- optional but model-mandatory BGC tracking
- asset initiation and return tracking
- email trigger generation through Gmail SMTP
- auditable JSON-based state management

## Pipeline Scope

This project now supports a sequential workforce lifecycle.

### 1. Onboarding lifecycle

Stages:
1. Profile Screening Approved
2. Onboarding Initiated
3. BGC In Progress or BGC Waived
4. BGC Cleared
5. Asset Initiation
6. Onboarded / Ready to Join

Mandatory onboarding fields:
- employee id
- employee name
- employee email
- manager email
- PMO email
- DSP reviewer email
- department
- role
- joining date
- project name
- client name
- requested assets
- BGC required flag

Optional BGC metadata fields:
- BGC vendor
- BGC reference id

Automated actions:
1. validate mandatory onboarding data
2. register profile-screening-approved candidate
3. create onboarding workflow record
4. trigger onboarding notifications
5. initiate BGC if required
6. initiate assets like laptop, ID card, mail ID, welcome kit
7. track assigned and pending assets
8. generate auditable stage history
9. send notifications to candidate, manager, PMO, and DSP reviewer

### 2. Offboarding lifecycle

Stages:
1. Offboarding Initiated
2. Asset Return
3. Access Revocation
4. Offboarded

Mandatory offboarding fields:
- employee id
- employee name
- employee email
- manager email
- PMO email
- DSP reviewer email
- last working date
- assigned assets

Automated actions:
1. validate offboarding request
2. create exit workflow record
3. process asset return
4. identify missing assets
5. revoke logical access where applicable
6. notify candidate, manager, PMO, and DSP reviewer
7. update final offboarding status

## Project Structure

- `config/workflow_config.json` : pipeline rules, Gmail SMTP mail settings, and stage mail templates
- `data/assets.json` : sample asset inventory
- `data/employees.json` : sample employee records
- `data/workflows.json` : generated workflow execution data
- `scripts/workforce_orchestrator.py` : stage-based automation engine
- `samples/` : onboarding and offboarding sample events
- `requirements.txt` : Python dependencies for MSAL and Microsoft Graph calls
- `dashboard.html` : UI prototype for screening/onboarding visibility

## Setup

1. Enable 2-Step Verification on the Gmail account used as sender.
2. Generate a Gmail App Password for the sender account.
3. Update `config/workflow_config.json` with:
   - `sender_email`
   - `sender_password`
   - `smtp_host`
   - `smtp_port`
4. Install dependencies:

```powershell
pip install -r requirements.txt
```

## Run

From the `Workforce_Orchestrator` directory:

```powershell
python scripts/workforce_orchestrator.py samples/onboarding_event.json
python scripts/workforce_orchestrator.py samples/offboarding_event.json
```

## Event Contract

### Onboarding event example

```json
{
  "workflow_type": "onboarding",
  "employee_id": "EMP003",
  "employee_name": "Anil Kumar",
  "employee_email": "anil.kumar@example.com",
  "manager_email": "manager.ops@example.com",
  "pmo_email": "pmo.macquarie@example.com",
  "dsp_reviewer_email": "dsp.reviewer@example.com",
  "department": "Operations",
  "role": "Workforce Analyst",
  "joining_date": "2026-06-10",
  "project_name": "Workforce Orchestrator",
  "client_name": "Macquarie",
  "bcg_required": true,
  "bcg_vendor": "First Advantage",
  "bcg_reference_id": "BGC-EMP003-20260610",
  "requested_assets": ["laptop", "id_card", "mail_id", "welcome_kit"]
}
```

### Offboarding event example

```json
{
  "workflow_type": "offboarding",
  "employee_id": "EMP002",
  "employee_name": "Ananya Sharma",
  "employee_email": "ananya.sharma@example.com",
  "manager_email": "manager.eng@example.com",
  "pmo_email": "pmo.macquarie@example.com",
  "dsp_reviewer_email": "dsp.reviewer@example.com",
  "last_working_date": "2026-07-31",
  "assigned_assets": ["LAP-1001", "MON-2001", "ID-3001"]
}
```

## Output

The pipeline updates:
- `data/workflows.json`
- `data/employees.json`
- `data/assets.json`
- console summary of workflow execution
- generated stage-level email notifications in workflow records
- actual mail delivery through Gmail SMTP

## Notes

- Mail delivery is implemented using Python `smtplib` with a Gmail app password.
- The configured `sender_email` must be a valid Gmail account allowed to send mail.
- For production, use a dedicated workflow mailbox instead of a personal account.
- The current backend is enhanced for sequential workflow handling without requiring a destructive UI rewrite.
- `dashboard.html` can consume the new stage, BGC, asset, and notification fields incrementally.
- Current storage is file-based JSON for easy review and prototyping.