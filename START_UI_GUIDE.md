# How to Access and Run the UI Application

## Overview
The Workforce Orchestrator has a web-based dashboard UI (`dashboard.html`) that provides a visual interface for managing employee onboarding and offboarding workflows.

## Prerequisites
- Python 3.7+ installed
- Web browser (Chrome, Firefox, Edge, etc.)
- Project files in: `c:/Users/SarahSmruthi/Documents/Workforce_Orchestrator-main`

## Step-by-Step Instructions

### Step 1: Start the Backend API Server

The dashboard UI needs the backend API server running to trigger realtime notifications and use the chatbot.

**Open PowerShell or Command Prompt:**

```powershell
# Navigate to project directory
cd c:\Users\SarahSmruthi\Documents\Workforce_Orchestrator-main

# Start the API server on port 8050
python scripts/workforce_orchestrator.py --serve-api 8050
```

**You should see:**
```
Realtime Workflow API running on http://127.0.0.1:8050
```

**Keep this terminal window open!** The server needs to stay running while you use the UI.

### Step 2: Open the Dashboard UI

**Option A: Double-click the file**
1. Open File Explorer
2. Navigate to: `c:\Users\SarahSmruthi\Documents\Workforce_Orchestrator-main`
3. Double-click `dashboard.html`
4. It will open in your default web browser

**Option B: Use PowerShell command**

Open a **NEW** PowerShell window (keep the API server running in the first one):

```powershell
cd c:\Users\SarahSmruthi\Documents\Workforce_Orchestrator-main
start dashboard.html
```

**Option C: Open directly in browser**
1. Open your web browser
2. Press `Ctrl + O` (or File → Open)
3. Navigate to: `c:\Users\SarahSmruthi\Documents\Workforce_Orchestrator-main\dashboard.html`
4. Click Open

### Step 3: Use the Dashboard

Once the dashboard opens, you'll see:

#### **Left Sidebar Navigation:**
- 🏠 **Home** - Overview and statistics
- 👥 **Profile Screening** - View and filter candidate profiles
- 📋 **Onboarding** - Track onboarding workflows
- 📤 **Offboarding** - Manage employee exits
- 💬 **Chatbot** - Ask questions about workflows

#### **Main Features:**

1. **Profile Screening Section:**
   - View all candidates with their status
   - Filter by screening status (Nominated, Approved, Rejected, Hold)
   - Filter by experience level
   - Click on a candidate to view details

2. **Onboarding Section:**
   - View onboarding workflows
   - Track stages: Screening → Onboarding → BGC → Assets → Completed
   - Filter by onboarding status
   - Trigger realtime notifications for stages

3. **Offboarding Section:**
   - View offboarding workflows
   - Track asset returns
   - Monitor exit process

4. **Chatbot Assistant:**
   - Ask questions like:
     - "How many candidates are approved?"
     - "Show me nominated candidates"
     - "What's the status of BGC?"
     - "Help with asset tracking"

## UI Features Explained

### Realtime Notification Triggers

When viewing a candidate's workflow, you can trigger stage-specific email notifications:

**Available Triggers:**
- ✅ Onboarding Initiated
- ✅ BGC Completed
- ✅ Assets Initiated
- ✅ Offboarding Completed

**How to use:**
1. Select a candidate from the list
2. Click on the workflow stage buttons
3. The system will send notifications to all stakeholders (if Gmail is configured)

### Chatbot Queries

The chatbot understands natural language questions:

**Example Questions:**
- "How many candidates do we have?"
- "Show approved candidates"
- "List nominated candidates"
- "What's the experience filter?"
- "Help with BGC process"
- "Explain asset tracking"
- "Why are emails not sending?"

## Complete Setup (Both Backend + UI)

### Terminal 1: Start API Server
```powershell
cd c:\Users\SarahSmruthi\Documents\Workforce_Orchestrator-main
python scripts/workforce_orchestrator.py --serve-api 8050
```
**Leave this running!**

### Terminal 2: Open Dashboard
```powershell
cd c:\Users\SarahSmruthi\Documents\Workforce_Orchestrator-main
start dashboard.html
```

## Troubleshooting

### Issue: Dashboard opens but buttons don't work
**Cause:** API server is not running
**Solution:** Start the API server in Step 1

### Issue: "Failed to fetch" errors in browser console
**Cause:** API server is not accessible
**Solution:** 
1. Check if API server is running (Terminal 1)
2. Verify it's running on port 8050
3. Check browser console (F12) for error messages

### Issue: No candidates showing in dashboard
**Cause:** Data files might be empty or missing
**Solution:** Run a sample workflow first:
```powershell
python scripts/workforce_orchestrator.py samples/onboarding_event.json
```
Then refresh the dashboard

### Issue: Realtime notifications not working
**Cause:** Gmail SMTP not configured
**Solution:** This is expected. The workflow still completes, but emails won't be sent. To enable emails, configure Gmail SMTP in `config/workflow_config.json`

### Issue: Dashboard looks broken or unstyled
**Cause:** Browser compatibility or file access issue
**Solution:** 
1. Try a different browser (Chrome recommended)
2. Make sure you're opening the file directly (not through a text editor)
3. Check browser console (F12) for errors

## Testing the UI

### Quick Test Workflow:

1. **Start API Server** (Terminal 1):
   ```powershell
   python scripts/workforce_orchestrator.py --serve-api 8050
   ```

2. **Process a Sample Onboarding** (Terminal 2):
   ```powershell
   python scripts/workforce_orchestrator.py samples/onboarding_event.json
   ```

3. **Open Dashboard**:
   ```powershell
   start dashboard.html
   ```

4. **In the Dashboard:**
   - Click "Profile Screening" in sidebar
   - You should see "Anil Kumar" in the candidate list
   - Click on the candidate to view details
   - Try the chatbot: "How many candidates are approved?"

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     User's Web Browser                       │
│                      (dashboard.html)                        │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP Requests
                         │ (Port 8050)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Python API Server (Backend)                     │
│         workforce_orchestrator.py --serve-api                │
│                                                              │
│  Endpoints:                                                  │
│  • POST /api/realtime-stage-trigger                         │
│  • POST /api/chatbot                                        │
└────────────────────────┬────────────────────────────────────┘
                         │ Reads/Writes
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Files (JSON)                         │
│  • data/workflows.json                                       │
│  • data/employees.json                                       │
│  • data/assets.json                                          │
└─────────────────────────────────────────────────────────────┘
```

## What You Can Do in the UI

✅ **View Candidates** - See all candidates with their screening status
✅ **Filter & Search** - Filter by status, experience, and other criteria
✅ **Track Workflows** - Monitor onboarding/offboarding progress
✅ **View Stage History** - See complete audit trail for each workflow
✅ **Trigger Notifications** - Send realtime email notifications for stages
✅ **Asset Tracking** - Monitor asset assignments and returns
✅ **Chat Assistant** - Get help and query workflow data
✅ **Visual Dashboard** - See statistics and workflow summaries

## Next Steps

1. ✅ Start the API server (keep it running)
2. ✅ Open dashboard.html in your browser
3. ✅ Explore the Profile Screening section
4. ✅ Try the Chatbot with sample questions
5. ✅ Process more workflows using the Python script
6. ✅ Watch the dashboard update with new data

## Support

If you encounter issues:
1. Check both terminal windows are running
2. Look at browser console (F12) for JavaScript errors
3. Verify data files exist in the `data/` folder
4. Try refreshing the browser page
5. Restart the API server if needed

**The dashboard provides a complete visual interface for managing your workforce orchestration workflows!**