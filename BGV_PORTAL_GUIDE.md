# BGV (Background Verification) Portal Guide

## Overview
The BGV Portal is an AI-powered document verification system that uses Google Gemini API to intelligently verify candidate documents during the onboarding process. It features agentic AI capabilities for autonomous document analysis and cross-verification.

## Features

### 🤖 Agentic AI Capabilities
- **Autonomous Document Analysis**: AI agent independently extracts and verifies information
- **Intelligent Cross-Verification**: Compares data across multiple documents
- **Reference Document Comparison**: Validates against known good samples
- **Adaptive Reasoning**: AI makes intelligent decisions based on document quality and consistency
- **Multi-Stage Verification**: Sequential checks with confidence scoring

### 📄 Document Requirements
1. **Aadhaar Card Front**: Clear image showing name, photo, DOB, Aadhaar number
2. **Aadhaar Card Back**: Clear image showing address and QR code
3. **Details Form**: Completed PDF with all required information

## Setup Instructions

### Step 1: Install Dependencies

```powershell
cd c:\Users\SarahSmruthi\Documents\Workforce_Orchestrator-main
pip install -r requirements.txt
```

This installs:
- `google-generativeai` - For Gemini API integration
- `PyPDF2` - For PDF text extraction
- `Pillow` - For image processing
- `requests` - For API calls

### Step 2: Configure Gemini API Key

The API key is already configured in `config/workflow_config.json`:

```json
{
  "gemini_api_key": "AIzaSyCv5gqdrMMg5KbkdGcUcs40ZGBgrwtuESE",
  "bgv_settings": {
    "auto_approve_threshold": 85,
    "manual_review_threshold": 70,
    "enable_reference_comparison": true,
    "require_all_documents": true
  }
}
```

**Note**: You can also set the API key as an environment variable:
```powershell
$env:GEMINI_API_KEY = "your-api-key-here"
```

### Step 3: Prepare Reference Documents

Reference documents are already in the `data/` folder:
- `data/aadhaar_front.png` - Sample Aadhaar front
- `data/aadhaar_back.png` - Sample Aadhaar back
- `data/sample_details_form.pdf` - Sample form

These are used by the AI to compare document layouts and authenticity.

### Step 4: Start the API Server

```powershell
python scripts/workforce_orchestrator.py --serve-api 8050
```

Keep this running in the background.

## Using the BGV Portal

### For Candidates

#### Step 1: Access the Portal

Open the BGV portal with candidate information:

```
bgv_portal.html?name=John%20Doe&empId=EMP001&email=john.doe@example.com
```

Or simply open `bgv_portal.html` in a browser (it will use test data).

#### Step 2: Upload Documents

1. Click on each upload box
2. Select the corresponding document:
   - **Aadhaar Front**: JPG/PNG image
   - **Aadhaar Back**: JPG/PNG image
   - **Details Form**: PDF file
3. Preview will show after upload
4. Maximum file size: 5MB per document

#### Step 3: Submit for Verification

1. Once all three documents are uploaded, the "Submit for Verification" button becomes active
2. Click the button to start AI verification
3. The system will show a processing indicator

#### Step 4: View Results

After processing (typically 10-30 seconds), you'll see:

**Verification Status:**
- ✅ **Approved**: All checks passed
- ❌ **Rejected**: Critical issues found
- ⚠️ **Review Required**: Manual review needed

**Detailed Checks:**
- Aadhaar Front Extraction
- Aadhaar Back Extraction
- Aadhaar Front Authenticity
- Aadhaar Back Authenticity
- Form Completeness
- Name Match
- Address Consistency
- Document Authenticity
- Data Completeness

**AI Analysis Summary:**
The AI provides an overall assessment with confidence score and recommendations.

## AI Verification Process

### Stage 1: Document Extraction
The AI agent extracts information from each document:

**From Aadhaar Front:**
- Full name
- Aadhaar number (12 digits)
- Date of birth
- Gender
- Photo quality assessment
- Document quality assessment

**From Aadhaar Back:**
- Complete address
- QR code presence
- Document quality assessment

**From Details Form:**
- All required fields (name, DOB, address, contact info, etc.)
- Completeness score
- Missing fields identification

### Stage 2: Reference Comparison
The AI compares uploaded documents with reference samples:
- Layout similarity analysis
- Authenticity indicators detection
- Quality comparison
- Suspicious pattern identification

### Stage 3: Cross-Verification
The AI performs intelligent cross-verification:
- **Name Matching**: Compares names across all documents
- **Address Consistency**: Validates address information
- **Data Completeness**: Ensures all required fields are present
- **Document Authenticity**: Overall authenticity assessment

### Stage 4: Final Decision
The AI makes an autonomous decision:
- **Confidence Score**: 0-100% confidence in verification
- **Status**: Approved/Rejected/Review Required
- **Recommendations**: Specific actions or concerns

## Verification Thresholds

Configured in `config/workflow_config.json`:

```json
"bgv_settings": {
  "auto_approve_threshold": 85,      // Auto-approve if confidence >= 85%
  "manual_review_threshold": 70,     // Manual review if 70% <= confidence < 85%
  "enable_reference_comparison": true,
  "require_all_documents": true
}
```

## Integration with Workflow

### Automatic Workflow Update

When BGV is approved:
1. Verification result is saved to `data/bgv_verifications.json`
2. Employee's onboarding workflow is updated with:
   - `bgv_verification_id`: Unique verification ID
   - `bgv_status`: "verified"
   - `bgv_verified_at`: Timestamp

### Triggering BGV from Dashboard

You can integrate BGV into the main dashboard by adding a "Start BGV" button in the onboarding workflow section.

## API Endpoint

### POST /api/bgv-verify

**Request**: Multipart form data
```
aadhaar_front: [image file]
aadhaar_back: [image file]
details_form: [PDF file]
employee_id: "EMP001"
employee_name: "John Doe"
employee_email: "john.doe@example.com"
```

**Response**: JSON
```json
{
  "verification_id": "BGV-20260526040000",
  "employee_id": "EMP001",
  "employee_name": "John Doe",
  "timestamp": "2026-05-26T04:00:00Z",
  "verification_status": "approved",
  "checks": [
    {
      "check_name": "Aadhaar Front Extraction",
      "status": "pass",
      "message": "Successfully extracted information"
    }
  ],
  "extracted_data": {
    "aadhaar_front": {...},
    "aadhaar_back": {...},
    "form": {...},
    "cross_verification": {...}
  },
  "ai_analysis": "All documents verified successfully...",
  "confidence_score": 92
}
```

## Troubleshooting

### Issue: "BGV verification module not available"
**Solution**: Install dependencies
```powershell
pip install google-generativeai PyPDF2 Pillow
```

### Issue: "Gemini API key not configured"
**Solution**: 
1. Check `config/workflow_config.json` has the API key
2. Or set environment variable: `$env:GEMINI_API_KEY = "your-key"`

### Issue: "Failed to extract information"
**Causes**:
- Poor image quality (blurred, dark, cropped)
- Unsupported file format
- File size too large

**Solutions**:
- Use clear, well-lit photos
- Ensure entire document is visible
- Use JPG/PNG for images, PDF for forms
- Keep files under 5MB

### Issue: "Verification taking too long"
**Causes**:
- Large file sizes
- Network latency to Gemini API
- Complex document analysis

**Solutions**:
- Compress images before upload
- Ensure stable internet connection
- Wait up to 60 seconds for complex verifications

### Issue: "Cross-verification failed"
**Causes**:
- Name mismatch between documents
- Address inconsistencies
- Incomplete form data

**Solutions**:
- Ensure all documents belong to the same person
- Verify all form fields are filled correctly
- Check for typos or spelling differences

## Security Considerations

1. **Temporary Storage**: Uploaded files are stored temporarily and deleted after verification
2. **API Key Security**: Keep your Gemini API key confidential
3. **Data Privacy**: Verification results contain sensitive personal information
4. **HTTPS**: In production, use HTTPS for the portal
5. **Access Control**: Implement authentication for the BGV portal

## Advanced Features

### Custom Verification Rules

You can customize verification logic in `scripts/bgv_verification.py`:

```python
# Adjust AI prompts for specific requirements
# Modify confidence thresholds
# Add custom validation checks
```

### Batch Verification

Process multiple candidates:

```python
from bgv_verification import BGVVerificationEngine

engine = BGVVerificationEngine(api_key, reference_path)

for candidate in candidates:
    result = engine.verify_documents(
        candidate['aadhaar_front'],
        candidate['aadhaar_back'],
        candidate['form'],
        candidate['info']
    )
    print(f"Verified {candidate['name']}: {result['verification_status']}")
```

### Verification History

View all verifications:

```python
history = engine.get_verification_history()
# Or for specific employee
employee_history = engine.get_verification_history(employee_id="EMP001")
```

## Testing the System

### Quick Test

1. Start API server:
```powershell
python scripts/workforce_orchestrator.py --serve-api 8050
```

2. Open BGV portal:
```powershell
start bgv_portal.html
```

3. Upload the sample documents from `data/` folder

4. Submit and verify the AI analysis works

### Expected Results

With good quality documents:
- Extraction: ✅ Pass
- Authenticity: ✅ Pass
- Cross-verification: ✅ Pass
- Overall: ✅ Approved (85-95% confidence)

## Production Deployment

### Checklist

- [ ] Install all dependencies
- [ ] Configure Gemini API key
- [ ] Set up HTTPS
- [ ] Implement authentication
- [ ] Configure backup storage for verification results
- [ ] Set up monitoring and logging
- [ ] Test with various document qualities
- [ ] Train staff on manual review process
- [ ] Document escalation procedures

## Support

For issues or questions:
1. Check this guide
2. Review `scripts/bgv_verification.py` for implementation details
3. Check browser console (F12) for errors
4. Verify API server is running
5. Test Gemini API key with a simple request

## Future Enhancements

- [ ] Support for additional ID types (Passport, Driver's License)
- [ ] Multi-language support
- [ ] Real-time video verification
- [ ] Blockchain-based verification records
- [ ] Integration with government databases
- [ ] Mobile app for document capture
- [ ] Advanced fraud detection algorithms
- [ ] Automated quality improvement suggestions

---

**The BGV Portal provides enterprise-grade document verification with the power of AI, ensuring secure and accurate background checks for your workforce!**