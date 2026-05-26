# How Candidates Access BGV Portal from IDCP Dashboard

## Overview
The BGV (Background Verification) Portal is seamlessly integrated into the IDCP (Integrated Dashboard Control Panel) workflow. Candidates can access it directly from the main dashboard when their BGC (Background Check) stage is initiated.

## Access Flow

### For HR/Admin (Dashboard User):

#### Step 1: Open IDCP Dashboard
```
http://localhost/dashboard.html
```
Or simply open `dashboard.html` in your browser.

#### Step 2: Navigate to Onboarding Section
1. Click on **"📋 Onboarding"** in the left sidebar
2. You'll see the list of candidates in various onboarding stages

#### Step 3: Select a Candidate
1. Click on any candidate card to view their workflow details
2. The workflow stages will be displayed:
   - ✅ Profile Screening Approved
   - ✅ Onboarded
   - ⏳ **BGC** (Background Check)
   - ⏳ Asset Initiated
   - ⏳ Offboarded

#### Step 4: Initiate BGV Portal
1. In the **BGC** stage section, you'll see a button: **"🔐 Start BGV Portal"**
2. Click this button
3. A new window will open with the BGV Portal pre-filled with candidate information
4. You'll see a confirmation message

### For Candidates:

#### Option A: Direct Link from HR
HR can share the direct BGV portal link with candidate information:
```
bgv_portal.html?name=John%20Doe&empId=EMP001&email=john.doe@example.com
```

#### Option B: Email Notification (Recommended)
When BGC is initiated, the system can send an automated email to the candidate with:
- BGV portal link
- Instructions
- Required documents list
- Deadline

#### Option C: Self-Service Portal
Candidates can access through a dedicated self-service portal (future enhancement).

## Complete Workflow

### 1. **HR Initiates BGC**
```
IDCP Dashboard → Onboarding → Select Candidate → Click "Start BGV Portal"
```

### 2. **BGV Portal Opens**
- New browser window/tab opens
- Candidate information is pre-filled:
  - Name
  - Employee ID
  - Email
- Instructions are displayed

### 3. **Candidate Uploads Documents**
Required documents:
- ✅ Aadhaar Card (Front) - Image (JPG/PNG)
- ✅ Aadhaar Card (Back) - Image (JPG/PNG)
- ✅ Details Form - PDF

### 4. **AI Verification Process**
The system automatically:
1. Extracts information from Aadhaar
2. Compares with reference documents
3. Verifies form completeness
4. Cross-verifies all data
5. Generates verification report

### 5. **Results Display**
Candidate sees:
- ✅ Approved / ❌ Rejected / ⚠️ Review Required
- Detailed check results
- AI analysis summary
- Confidence score

### 6. **Workflow Update**
If approved:
- BGC status updated to "Verified"
- Workflow moves to next stage
- Notifications sent to stakeholders

## Integration Points

### In IDCP Dashboard:

#### 1. **BGC Stage Card**
```javascript
{
  key: "bgc",
  title: "BGC",
  description: "BGC is pending for this candidate. Click button to start BGV portal.",
  status: "pending",
  action: {
    label: "🔐 Start BGV Portal",
    handler: () => openBGVPortal(candidateName, employeeId, email)
  }
}
```

#### 2. **JavaScript Function**
```javascript
function openBGVPortal(candidateName, employeeId, employeeEmail) {
  const bgvUrl = `bgv_portal.html?name=${encodeURIComponent(candidateName)}&empId=${encodeURIComponent(employeeId)}&email=${encodeURIComponent(employeeEmail)}`;
  window.open(bgvUrl, '_blank', 'width=1200,height=900');
}
```

#### 3. **API Endpoint**
```
POST http://127.0.0.1:8050/api/bgv-verify
```

## URL Parameters

The BGV portal accepts these URL parameters:

| Parameter | Description | Example |
|-----------|-------------|---------|
| `name` | Candidate full name | `John%20Doe` |
| `empId` | Employee ID | `EMP001` |
| `email` | Candidate email | `john.doe@example.com` |

### Example URLs:

**Basic:**
```
bgv_portal.html
```

**With Candidate Info:**
```
bgv_portal.html?name=Sarah%20Smith&empId=EMP003&email=sarah.smith@example.com
```

**Full Example:**
```
http://localhost/bgv_portal.html?name=Anil%20Kumar&empId=EMP003&email=anil.kumar@example.com
```

## User Experience Flow

### HR/Admin View (IDCP Dashboard):

```
┌─────────────────────────────────────────┐
│     IDCP Dashboard - Onboarding         │
├─────────────────────────────────────────┤
│                                         │
│  Candidate: Anil Kumar (EMP003)         │
│  Status: Onboarding in Progress         │
│                                         │
│  Workflow Stages:                       │
│  ✅ Profile Screening Approved          │
│  ✅ Onboarded                           │
│  ⏳ BGC [🔐 Start BGV Portal] ← Click  │
│  ⏳ Asset Initiated                     │
│  ⏳ Offboarded                          │
│                                         │
└─────────────────────────────────────────┘
```

### Candidate View (BGV Portal):

```
┌─────────────────────────────────────────┐
│   🔐 Background Verification Portal     │
├─────────────────────────────────────────┤
│                                         │
│  Candidate Information:                 │
│  Name: Anil Kumar                       │
│  Employee ID: EMP003                    │
│  Email: anil.kumar@example.com          │
│                                         │
│  📋 Instructions                        │
│  Upload clear, readable documents...    │
│                                         │
│  Upload Documents:                      │
│  [🪪 Aadhaar Front] [Choose File]      │
│  [🪪 Aadhaar Back]  [Choose File]      │
│  [📄 Details Form]  [Choose File]      │
│                                         │
│  [Submit for Verification]              │
│                                         │
└─────────────────────────────────────────┘
```

## Email Template (Optional)

When BGC is initiated, send this email to the candidate:

```
Subject: Action Required: Complete Background Verification

Dear [Candidate Name],

Your onboarding process has reached the Background Verification stage. 
Please complete the following steps:

1. Click the link below to access the BGV Portal:
   [BGV Portal Link]

2. Upload the following documents:
   - Aadhaar Card (Front) - Clear image
   - Aadhaar Card (Back) - Clear image
   - Completed Details Form - PDF

3. Submit for AI-powered verification

Your documents will be verified automatically using our intelligent 
verification system. You'll receive results immediately.

Important Notes:
- Ensure all documents are clear and readable
- File size limit: 5MB per document
- Supported formats: JPG, PNG for images; PDF for forms

Need help? Contact HR at hr@company.com

Best regards,
HR Team
```

## Security Considerations

### 1. **Access Control**
- BGV portal link contains candidate-specific information
- Links should be unique and time-limited (future enhancement)
- Implement session management

### 2. **Data Privacy**
- Documents are processed and deleted after verification
- Results stored securely in `data/bgv_verifications.json`
- Sensitive data encrypted at rest

### 3. **Authentication** (Future Enhancement)
- Add OTP verification
- Email verification link
- Two-factor authentication

## Troubleshooting

### Issue: "Start BGV Portal" button not visible
**Cause:** BGC stage already completed or not yet reached
**Solution:** Check candidate's current workflow stage

### Issue: BGV portal opens but shows "Loading..."
**Cause:** URL parameters missing or incorrect
**Solution:** Ensure name, empId, and email are passed correctly

### Issue: Documents not uploading
**Cause:** File size too large or wrong format
**Solution:** 
- Check file size (max 5MB)
- Use JPG/PNG for images, PDF for forms
- Ensure files are not corrupted

### Issue: Verification fails
**Cause:** API server not running or Gemini API issues
**Solution:**
- Verify API server is running on port 8050
- Check Gemini API key is configured
- Review browser console for errors

## Testing the Integration

### Test Scenario 1: Complete Flow

1. **Start API Server:**
```powershell
python scripts/workforce_orchestrator.py --serve-api 8050
```

2. **Open IDCP Dashboard:**
```powershell
start dashboard.html
```

3. **Navigate to Onboarding:**
- Click "📋 Onboarding" in sidebar
- Select a candidate (e.g., "Anil Kumar")

4. **Start BGV Portal:**
- Click "🔐 Start BGV Portal" button
- New window opens with BGV portal

5. **Upload Documents:**
- Use sample documents from `data/` folder
- Submit for verification

6. **View Results:**
- Check verification status
- Review detailed checks
- See AI analysis

### Test Scenario 2: Direct Link

1. **Open BGV Portal Directly:**
```
bgv_portal.html?name=Test%20User&empId=TEST001&email=test@example.com
```

2. **Upload and Verify:**
- Upload test documents
- Submit for verification
- Check results

## Production Deployment

### Checklist:

- [ ] Deploy IDCP dashboard to web server
- [ ] Deploy BGV portal to same domain
- [ ] Configure HTTPS for secure communication
- [ ] Set up email notifications for BGC initiation
- [ ] Implement authentication and authorization
- [ ] Configure backup and disaster recovery
- [ ] Set up monitoring and logging
- [ ] Train HR staff on the process
- [ ] Create candidate user guide
- [ ] Test end-to-end workflow

### Recommended Architecture:

```
┌─────────────────────────────────────────────────┐
│              Load Balancer (HTTPS)              │
└────────────────┬────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
┌───────▼──────┐  ┌──────▼────────┐
│ IDCP Dashboard│  │  BGV Portal   │
│ (dashboard.html)│  │(bgv_portal.html)│
└───────┬──────┘  └──────┬────────┘
        │                 │
        └────────┬────────┘
                 │
        ┌────────▼────────┐
        │   API Server    │
        │   (Port 8050)   │
        └────────┬────────┘
                 │
        ┌────────▼────────┐
        │  Gemini API     │
        │  (AI Verification)│
        └─────────────────┘
```

## Summary

The BGV portal is fully integrated into the IDCP dashboard workflow:

1. **HR initiates** BGC from dashboard
2. **System opens** BGV portal with candidate info
3. **Candidate uploads** required documents
4. **AI verifies** documents automatically
5. **Results update** workflow in real-time
6. **Process continues** to next stage

This seamless integration ensures a smooth, secure, and efficient background verification process for all stakeholders.

---

**For more details, see:**
- `BGV_PORTAL_GUIDE.md` - Complete BGV portal documentation
- `HOW_TO_RUN.md` - System setup and running instructions
- `START_UI_GUIDE.md` - Dashboard usage guide