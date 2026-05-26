# Email Notification System Guide

## Overview

The Workforce Orchestrator now includes an intelligent email notification agent that automatically sends emails to candidates and managers at various stages of the onboarding and offboarding workflow.

## Email Configuration

### SMTP Settings

The system uses Gmail SMTP by default. Configure these environment variables or they will use the default values:

```bash
SENDER_EMAIL=idcp.administrator@gmail.com
SENDER_PASSWORD=mzdbgmctrlhtfdjj
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### Setting Environment Variables

**Windows (PowerShell):**
```powershell
$env:SENDER_EMAIL="idcp.administrator@gmail.com"
$env:SENDER_PASSWORD="mzdbgmctrlhtfdjj"
$env:SMTP_SERVER="smtp.gmail.com"
$env:SMTP_PORT="587"
```

**Linux/Mac:**
```bash
export SENDER_EMAIL="idcp.administrator@gmail.com"
export SENDER_PASSWORD="mzdbgmctrlhtfdjj"
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
```

## Email Triggers

### Onboarding Workflow

#### 1. Welcome Email
**Trigger:** When onboarding is initiated
**Recipients:** Candidate (To), Manager (CC)
**Content:**
- Welcome message
- Employee details (ID, designation, department, start date)
- Next steps checklist
- Contact information

#### 2. BGC Initiation Email
**Trigger:** When background check is initiated
**Recipients:** Candidate
**Content:**
- Action required notice
- BGV portal link with pre-filled candidate info
- List of required documents:
  - Aadhaar Front (image)
  - Aadhaar Back (image)
  - Details Form (PDF/DOCX)
  - Resume/CV (PDF/DOCX)
- Document requirements and validation criteria
- 48-hour deadline reminder

#### 3. BGC Completion Email
**Trigger:** When candidate submits documents and AI verification completes
**Recipients:** Candidate (To), Manager (CC)
**Content:**
- Verification status (Successful/Rejected/Resubmit)
- Verification date and details
- Next steps based on status

#### 4. Asset Allocation Email
**Trigger:** When assets are allocated to employee
**Recipients:** Candidate (To), Manager (CC)
**Content:**
- List of allocated assets with details:
  - Asset Type
  - Asset ID
  - Serial Number
- Asset responsibility notice
- IT team contact

### Offboarding Workflow

#### 5. Offboarding Initiation Email
**Trigger:** When offboarding process starts
**Recipients:** Employee (To), Manager (CC)
**Content:**
- Offboarding checklist:
  - Return company assets
  - Complete knowledge transfer
  - Clear pending tasks
  - Exit interview
  - Final settlement
- Last working day
- HR contact information

#### 6. Offboarding Completion Email
**Trigger:** When offboarding is completed
**Recipients:** Employee (To), Manager (CC)
**Content:**
- Completion confirmation
- Final details:
  - Assets returned
  - Access revoked
  - Settlement processing
- Thank you message

## Email Templates

All emails use professional HTML templates with:
- Gradient header with company branding
- Responsive design
- Clear call-to-action buttons
- Structured information boxes
- Professional footer

### Template Features:
- **Gradient Headers:** Purple gradient (667eea → 764ba2)
- **Responsive Layout:** Max-width 600px for email clients
- **Color Coding:**
  - Success: Green (#28a745)
  - Warning: Yellow (#ffc107)
  - Error: Red (#dc3545)
  - Info: Blue (#667eea)

## Integration Points

### 1. Onboarding Process
```python
# Welcome email sent at onboarding initiation
email_agent.send_onboarding_welcome_email(employee_data, manager_email)

# BGC email sent when background check is initiated
email_agent.send_bgc_initiation_email(employee_data, bgv_portal_url)

# Asset email sent when assets are allocated
email_agent.send_asset_allocation_email(employee_data, assets, manager_email)
```

### 2. BGV Verification
```python
# Completion email sent after AI verification
email_agent.send_bgc_completion_email(employee_data, verification_status, manager_email)
```

### 3. Offboarding Process
```python
# Initiation email sent when offboarding starts
email_agent.send_offboarding_initiation_email(employee_data, manager_email)

# Completion email sent when offboarding finishes
email_agent.send_offboarding_completion_email(employee_data, manager_email)
```

## Email Agent API

### EmailNotificationAgent Class

```python
from email_notification_agent import EmailNotificationAgent

# Initialize agent
agent = EmailNotificationAgent(
    sender_email="your-email@gmail.com",
    sender_password="your-app-password",
    smtp_server="smtp.gmail.com",
    smtp_port=587
)

# Send emails
result = agent.send_email(
    recipient_email="candidate@example.com",
    subject="Welcome!",
    body_html="<html>...</html>",
    cc_emails=["manager@example.com"]
)
```

### Available Methods:

1. **send_onboarding_welcome_email(employee_data, manager_email)**
2. **send_bgc_initiation_email(employee_data, bgv_portal_url)**
3. **send_bgc_completion_email(employee_data, verification_status, manager_email)**
4. **send_asset_allocation_email(employee_data, assets, manager_email)**
5. **send_offboarding_initiation_email(employee_data, manager_email)**
6. **send_offboarding_completion_email(employee_data, manager_email)**
7. **send_manager_notification(manager_email, employee_data, event_type, details)**

## Email History

The agent maintains a history of all sent emails:

```python
# Get email history
history = agent.get_email_history()

# Each entry contains:
{
    "timestamp": "2024-01-01T12:00:00",
    "recipient": "candidate@example.com",
    "cc": ["manager@example.com"],
    "subject": "Welcome to the Team!",
    "status": "sent"  # or "failed"
}
```

## Error Handling

The system includes comprehensive error handling:

1. **SMTP Connection Errors:** Logged with details
2. **Authentication Failures:** Captured and reported
3. **Invalid Email Addresses:** Validated before sending
4. **Network Issues:** Retry logic (future enhancement)

All errors are logged to console with `[EMAIL ERROR]` prefix.

## Testing

### Test Email Configuration

```python
# Test script
from email_notification_agent import EmailNotificationAgent

agent = EmailNotificationAgent()
print(f"Email Agent configured with: {agent.sender_email}")
print(f"SMTP Server: {agent.smtp_server}:{agent.smtp_port}")

# Send test email
employee_data = {
    "name": "Test User",
    "email": "test@example.com",
    "employee_id": "TEST001",
    "designation": "Software Engineer",
    "department": "IT",
    "start_date": "2024-01-01"
}

result = agent.send_onboarding_welcome_email(employee_data)
print(result)
```

## Gmail App Password Setup

For Gmail SMTP, you need an App Password:

1. Go to Google Account settings
2. Enable 2-Factor Authentication
3. Go to Security → App Passwords
4. Generate new app password for "Mail"
5. Use this password in `SENDER_PASSWORD`

## Troubleshooting

### Common Issues:

1. **"Authentication failed"**
   - Check email and password
   - Ensure using App Password for Gmail
   - Verify 2FA is enabled

2. **"Connection refused"**
   - Check SMTP server and port
   - Verify firewall settings
   - Ensure internet connectivity

3. **"Emails not received"**
   - Check spam folder
   - Verify recipient email address
   - Check email history for send status

4. **"Module not found"**
   - Ensure `email_notification_agent.py` is in scripts folder
   - Check Python path

## Logs

Email sending is logged to console:

```
[EMAIL] Welcome email sent to candidate@example.com
[EMAIL] BGC initiation email sent to candidate@example.com
[EMAIL] Asset allocation email sent to candidate@example.com
[EMAIL ERROR] Failed to send email: Authentication failed
```

## Future Enhancements

Planned features:
- Email templates customization via config
- Retry logic for failed emails
- Email queue for bulk sending
- Email analytics dashboard
- Attachment support
- Multi-language support
- Email scheduling

## Security Best Practices

1. **Never commit credentials** to version control
2. **Use environment variables** for sensitive data
3. **Use App Passwords** instead of account passwords
4. **Enable 2FA** on email accounts
5. **Rotate passwords** regularly
6. **Monitor email logs** for suspicious activity

## Support

For issues or questions:
- Check logs for error messages
- Verify SMTP configuration
- Test with a simple email first
- Contact: idcp.administrator@gmail.com

---

**Made with Bob - Intelligent Workforce Orchestrator**