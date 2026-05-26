# Quick Test Guide - BGV Portal on UI

## Your Dashboard is Already Open! 

Follow these steps to test the BGV portal integration:

## Step-by-Step Test:

### 1. In Your Open Dashboard Window:

Look at the **left sidebar** and click on:
```
📋 Onboarding
```

### 2. You'll See Candidate Cards:

Click on any candidate card, for example:
```
┌─────────────────────────────┐
│  Anil Kumar                 │
│  EMP003                     │
│  Status: Onboarding         │
│  [Click Here]               │
└─────────────────────────────┘
```

### 3. Scroll Down to Workflow Stages:

You'll see stages like:
```
✅ Profile Screening Approved
✅ Onboarded
⏳ BGC  [🔐 Start BGV Portal] ← CLICK THIS BUTTON!
⏳ Asset Initiated
⏳ Offboarded
```

### 4. Click the "🔐 Start BGV Portal" Button

A new window will open showing the BGV Portal with:
- Candidate name pre-filled
- Employee ID pre-filled
- Email pre-filled
- Three upload boxes for documents

### 5. Test Document Upload:

In the BGV Portal window, upload these test files from your `data/` folder:
- **Aadhaar Front**: `data/aadhaar_front.png`
- **Aadhaar Back**: `data/aadhaar_back.png`
- **Details Form**: `data/sample_details_form.pdf`

### 6. Click "Submit for Verification"

The AI will process the documents and show results!

## If You Don't See the Dashboard:

The dashboard should already be open. If not, run:
```powershell
start dashboard.html
```

## Visual Guide:

```
┌─────────────────────────────────────────────────────────────┐
│  IDCP Dashboard                                    [X]       │
├──────────┬──────────────────────────────────────────────────┤
│          │                                                   │
│  🏠 Home │  Onboarding Workflow                             │
│          │                                                   │
│  👥 Profile  Candidate: Anil Kumar (EMP003)                │
│  Screening│                                                  │
│          │  Workflow Stages:                                │
│  📋 Onboarding  ✅ Profile Screening Approved              │
│    ← CLICK    ✅ Onboarded                                 │
│          │  ⏳ BGC [🔐 Start BGV Portal] ← THEN CLICK THIS│
│  📤 Offboarding  ⏳ Asset Initiated                        │
│          │  ⏳ Offboarded                                   │
│  💬 Chatbot│                                                │
│          │                                                   │
└──────────┴───────────────────────────────────────────────────┘
```

## What Happens When You Click:

1. **New window opens** with BGV Portal
2. **Candidate info is pre-filled** automatically
3. **Upload interface is ready** for documents
4. **Submit button activates** after all files uploaded
5. **AI verification runs** automatically
6. **Results display** with detailed checks

## Current System Status:

✅ API Server: Running on port 8050 (Terminal 1)
✅ Dashboard: Open in your browser
✅ BGV Portal: Ready to launch
✅ AI Verification: Configured and ready
✅ All Code: Error-free and functional

## Test Now!

1. Switch to your browser window with the dashboard
2. Click "📋 Onboarding" in the sidebar
3. Select a candidate
4. Click "🔐 Start BGV Portal"
5. Upload documents
6. See the AI verification in action!

---

**Everything is ready and running. Just follow the steps above in your open dashboard!** 🚀