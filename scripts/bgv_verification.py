"""
BGV Document Verification Module with Agentic AI
Uses Google Gemini API for intelligent document verification
"""

import base64
import json
import os
from pathlib import Path
from datetime import datetime, UTC
from PIL import Image
import io

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("WARNING: google-generativeai not installed. Install with: pip install google-generativeai")


class GeminiAgent:
    """Agentic AI agent using Gemini API for document verification"""
    
    def __init__(self, api_key):
        if not GENAI_AVAILABLE:
            raise ImportError("google-generativeai library is required")
        
        self.api_key = api_key
        genai.configure(api_key=api_key)
        # Use gemini-pro (stable model for text)
        self.model = genai.GenerativeModel('gemini-pro')
        # For vision tasks, we'll use gemini-pro-vision
        self.vision_model = genai.GenerativeModel('gemini-pro-vision')
    
    def load_image(self, image_path):
        """Load image from path"""
        try:
            img = Image.open(image_path)
            return img
        except Exception as e:
            print(f"Error loading image: {e}")
            return None
    
    def analyze_document(self, image_path, prompt):
        """
        Analyze document using Gemini Vision API
        
        Args:
            image_path: Path to image file
            prompt: Analysis prompt for the AI
            
        Returns:
            dict: Analysis results from Gemini
        """
        try:
            img = self.load_image(image_path)
            if img is None:
                return {
                    "success": False,
                    "error": "Failed to load image"
                }
            
            # Use vision model for image analysis
            response = self.vision_model.generate_content([prompt, img])
            
            return {
                "success": True,
                "analysis": response.text,
                "raw_response": response
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def extract_aadhaar_info(self, image_path, side='front'):
        """Extract information from Aadhaar card with structure validation"""
        prompt = f"""
You are an expert Aadhaar document verification agent trained on authentic Aadhaar card structure.

AADHAAR STRUCTURE KNOWLEDGE:
- Aadhaar cards have a specific government logo (UIDAI logo)
- Aadhaar number is EXACTLY 12 digits in format: XXXX XXXX XXXX (with spaces)
- Front side has: Logo, Name, Photo, DOB, Gender, Aadhaar Number
- Back side has: Address and QR code (mandatory)
- Specific color scheme and layout

Analyze this Aadhaar card ({side} side) image and extract the following information in JSON format:

For FRONT side, extract:
- name: Full name as printed (CRITICAL - must be exact)
- aadhaar_number: 12-digit Aadhaar number (format: XXXX XXXX XXXX)
- aadhaar_number_valid: true if exactly 12 digits, false otherwise
- date_of_birth: Date of birth (DD/MM/YYYY format)
- gender: Gender (Male/Female/Other)
- photo_quality: Quality of photo (clear/blurred/missing)
- logo_present: Whether UIDAI logo is visible (true/false)
- document_structure: Whether layout matches standard Aadhaar (valid/suspicious/invalid)
- document_quality: Overall document quality (good/fair/poor)
- is_valid: Whether the document appears authentic (true/false)

For BACK side, extract:
- address: Complete address as printed
- qr_code_present: Whether QR code is visible (true/false) - MANDATORY
- document_structure: Whether layout matches standard Aadhaar (valid/suspicious/invalid)
- document_quality: Overall document quality (good/fair/poor)
- is_valid: Whether the document appears authentic (true/false)

Also provide:
- confidence_score: Your confidence in the extraction (0-100)
- issues: List any issues found (tampering, poor quality, missing info, etc.)

Return ONLY valid JSON, no additional text.
"""
        
        result = self.analyze_document(image_path, prompt)
        
        if result['success']:
            try:
                # Extract JSON from the response
                analysis_text = result['analysis']
                # Remove markdown code blocks if present
                if '```json' in analysis_text:
                    analysis_text = analysis_text.split('```json')[1].split('```')[0]
                elif '```' in analysis_text:
                    analysis_text = analysis_text.split('```')[1].split('```')[0]
                
                extracted_data = json.loads(analysis_text.strip())
                return {
                    "success": True,
                    "data": extracted_data
                }
            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "error": f"Failed to parse JSON: {str(e)}",
                    "raw_text": result['analysis']
                }
        else:
            return result
    
    def verify_form_completeness(self, pdf_text):
        """Verify if the details form is complete"""
        prompt = f"""
You are a document verification agent. Analyze this form text and verify completeness.

Form text:
{pdf_text}

Check for the following required fields and return JSON:
{{
    "fields_present": {{
        "full_name": true/false,
        "father_name": true/false,
        "date_of_birth": true/false,
        "current_address": true/false,
        "permanent_address": true/false,
        "phone_number": true/false,
        "email": true/false,
        "emergency_contact": true/false,
        "education_details": true/false,
        "previous_employment": true/false
    }},
    "completeness_score": 0-100,
    "missing_fields": ["list of missing fields"],
    "issues": ["list of any issues found"],
    "is_complete": true/false
}}

Return ONLY valid JSON, no additional text.
"""
        
        try:
            response = self.model.generate_content(prompt)
            analysis_text = response.text
            
            # Extract JSON
            if '```json' in analysis_text:
                analysis_text = analysis_text.split('```json')[1].split('```')[0]
            elif '```' in analysis_text:
                analysis_text = analysis_text.split('```')[1].split('```')[0]
            
            form_data = json.loads(analysis_text.strip())
            return {
                "success": True,
                "data": form_data
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def cross_verify_documents(self, aadhaar_front_data, aadhaar_back_data, form_data, resume_data=None):
        """Cross-verify information across all documents using AI reasoning"""
        
        # Build the prompt with all available data
        documents_info = f"""
Aadhaar Front Data:
{json.dumps(aadhaar_front_data, indent=2)}

Aadhaar Back Data:
{json.dumps(aadhaar_back_data, indent=2)}

Form Data:
{json.dumps(form_data, indent=2)}
"""
        
        if resume_data:
            documents_info += f"""
Resume Data:
{json.dumps(resume_data, indent=2)}
"""
        
        prompt = f"""
You are an intelligent BGV verification agent trained on Aadhaar document structure. You know that:
- Aadhaar cards have a specific logo and layout
- Aadhaar number is exactly 12 digits in format XXXX XXXX XXXX
- Aadhaar front has: name, photo, DOB, gender, Aadhaar number
- Aadhaar back has: address and QR code
- All documents must have consistent name spelling

Cross-verify the following information extracted from different documents:

{documents_info}

CRITICAL: Perform strict name matching across ALL documents (Aadhaar, Form, {"Resume" if resume_data else ""}). Names must match exactly or be very similar (accounting for minor spelling variations).

Perform the following verification checks and return JSON:
{{
    "aadhaar_structure_validation": {{
        "status": "pass/fail/warning",
        "confidence": 0-100,
        "details": "Check if Aadhaar has 12-digit number, QR code present, proper structure"
    }},
    "name_cross_verification": {{
        "status": "pass/fail/warning",
        "confidence": 0-100,
        "details": "Compare names from Aadhaar, Form, {"and Resume" if resume_data else ""} - must match",
        "aadhaar_name": "name from aadhaar",
        "form_name": "name from form",
        {"resume_name": "name from resume"," if resume_data else ""}
        "match_result": "exact/similar/mismatch"
    }},
    "address_consistency": {{
        "status": "pass/fail/warning",
        "confidence": 0-100,
        "details": "explanation"
    }},
    "document_authenticity": {{
        "status": "pass/fail/warning",
        "confidence": 0-100,
        "details": "Check Aadhaar structure, logo presence, field completeness"
    }},
    "data_completeness": {{
        "status": "pass/fail/warning",
        "confidence": 0-100,
        "details": "explanation"
    }},
    "overall_verification": {{
        "status": "successful/rejected/resubmit",
        "confidence": 0-100,
        "summary": "overall assessment",
        "decision_reason": "why successful/rejected/resubmit"
    }},
    "red_flags": ["list any suspicious findings"],
    "recommendations": ["list any recommendations for resubmission if needed"]
}}

IMPORTANT:
- Use "successful" for approved cases (name matches, all checks pass)
- Use "rejected" for clear fraud/fake documents
- Use "resubmit" for missing info, unclear documents, or minor issues that can be fixed

Return ONLY valid JSON, no additional text.
"""
        
        try:
            response = self.model.generate_content(prompt)
            analysis_text = response.text
            
            # Extract JSON
            if '```json' in analysis_text:
                analysis_text = analysis_text.split('```json')[1].split('```')[0]
            elif '```' in analysis_text:
                analysis_text = analysis_text.split('```')[1].split('```')[0]
            
            verification_result = json.loads(analysis_text.strip())
            return {
                "success": True,
                "data": verification_result
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def compare_with_reference(self, uploaded_image_path, reference_image_path, doc_type):
        """Compare uploaded document with reference using AI"""
        prompt = f"""
You are a document verification expert. Compare these two {doc_type} documents.

The first image is a REFERENCE sample (known good document).
The second image is the UPLOADED document to verify.

Analyze and return JSON:
{{
    "similarity_score": 0-100,
    "layout_match": "matches/differs/suspicious",
    "quality_comparison": "better/similar/worse",
    "authenticity_indicators": ["list of authenticity indicators found"],
    "concerns": ["list any concerns"],
    "recommendation": "approve/reject/review"
}}

Return ONLY valid JSON, no additional text.
"""
        
        try:
            ref_img = self.load_image(reference_image_path)
            upload_img = self.load_image(uploaded_image_path)
            
            if ref_img is None or upload_img is None:
                return {
                    "success": False,
                    "error": "Failed to load images"
                }
            
            # Use vision model for image comparison
            response = self.vision_model.generate_content([prompt, ref_img, upload_img])
            analysis_text = response.text
            
            # Extract JSON
            if '```json' in analysis_text:
                analysis_text = analysis_text.split('```json')[1].split('```')[0]
            elif '```' in analysis_text:
                analysis_text = analysis_text.split('```')[1].split('```')[0]
            
            comparison_result = json.loads(analysis_text.strip())
            return {
                "success": True,
                "data": comparison_result
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def extract_resume_info(self, resume_text):
        """Extract key information from resume"""
        prompt = f"""
You are an expert resume analyzer. Extract the following information from this resume text in JSON format:

{{
    "name": "Full name of the candidate",
    "email": "Email address",
    "phone": "Phone number",
    "current_designation": "Current job title/designation",
    "total_experience": "Total years of experience",
    "education": ["List of educational qualifications"],
    "skills": ["List of key skills"],
    "certifications": ["List of certifications if any"],
    "previous_companies": ["List of previous companies worked at"],
    "confidence_score": 0-100
}}

Resume Text:
{resume_text[:3000]}

Return ONLY valid JSON, no additional text.
"""
        
        try:
            response = self.model.generate_content(prompt)
            analysis_text = response.text
            
            # Extract JSON
            if '```json' in analysis_text:
                analysis_text = analysis_text.split('```json')[1].split('```')[0]
            elif '```' in analysis_text:
                analysis_text = analysis_text.split('```')[1].split('```')[0]
            
            resume_data = json.loads(analysis_text.strip())
            return {
                "success": True,
                "data": resume_data
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class BGVVerificationEngine:
    """Main BGV verification engine with agentic AI capabilities"""
    
    def __init__(self, gemini_api_key, reference_docs_path):
        self.agent = GeminiAgent(gemini_api_key)
        self.reference_docs_path = Path(reference_docs_path)
        self.verification_history = []
    
    def extract_pdf_text(self, pdf_path):
        """Extract text from PDF or DOCX"""
        try:
            file_ext = str(pdf_path).lower()
            
            # Handle DOCX files
            if file_ext.endswith('.docx'):
                try:
                    from docx import Document
                    doc = Document(pdf_path)
                    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
                    return text if text.strip() else "[DOCX file appears empty]"
                except ImportError:
                    return "[python-docx not installed. Install with: pip install python-docx]"
                except Exception as e:
                    return f"[Error extracting DOCX: {str(e)}]"
            
            # Handle PDF files
            elif file_ext.endswith('.pdf'):
                try:
                    from PyPDF2 import PdfReader
                    reader = PdfReader(pdf_path)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text()
                    return text if text.strip() else "[PDF file appears empty]"
                except Exception as e:
                    return f"[Error extracting PDF: {str(e)}]"
            
            # Unknown file type
            else:
                return f"[Unsupported file type: {file_ext}. Please upload PDF or DOCX]"
                
        except Exception as e:
            return f"[Error processing document: {str(e)}]"
    
    def verify_documents(self, aadhaar_front_path, aadhaar_back_path, details_form_path, employee_info, resume_path=None):
        """
        Main verification method - orchestrates the entire verification process
        
        Args:
            aadhaar_front_path: Path to uploaded Aadhaar front image
            aadhaar_back_path: Path to uploaded Aadhaar back image
            details_form_path: Path to uploaded details form PDF
            employee_info: Dict with employee_id, employee_name, employee_email
            resume_path: Path to uploaded resume (PDF/DOCX) - optional
            
        Returns:
            dict: Complete verification results
        """
        verification_id = f"BGV-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
        
        results = {
            "verification_id": verification_id,
            "employee_id": employee_info.get("employee_id"),
            "employee_name": employee_info.get("employee_name"),
            "timestamp": datetime.now(UTC).isoformat(),
            "verification_status": "pending",
            "checks": [],
            "extracted_data": {},
            "ai_analysis": "",
            "confidence_score": 0
        }
        
        try:
            # Step 1: Extract information from Aadhaar front
            print("[INFO] Extracting Aadhaar front information...")
            front_result = self.agent.extract_aadhaar_info(aadhaar_front_path, 'front')
            
            if front_result['success']:
                results['extracted_data']['aadhaar_front'] = front_result['data']
                results['checks'].append({
                    "check_name": "Aadhaar Front Extraction",
                    "status": "pass",
                    "message": "Successfully extracted information from Aadhaar front"
                })
            else:
                results['checks'].append({
                    "check_name": "Aadhaar Front Extraction",
                    "status": "fail",
                    "message": f"Failed to extract: {front_result.get('error', 'Unknown error')}"
                })
            
            # Step 2: Extract information from Aadhaar back
            print("[INFO] Extracting Aadhaar back information...")
            back_result = self.agent.extract_aadhaar_info(aadhaar_back_path, 'back')
            
            if back_result['success']:
                results['extracted_data']['aadhaar_back'] = back_result['data']
                results['checks'].append({
                    "check_name": "Aadhaar Back Extraction",
                    "status": "pass",
                    "message": "Successfully extracted information from Aadhaar back"
                })
            else:
                results['checks'].append({
                    "check_name": "Aadhaar Back Extraction",
                    "status": "fail",
                    "message": f"Failed to extract: {back_result.get('error', 'Unknown error')}"
                })
            
            # Step 3: Compare with reference documents
            print("[INFO] Comparing with reference documents...")
            ref_front = self.reference_docs_path / "aadhaar_front.png"
            ref_back = self.reference_docs_path / "aadhaar_back.png"
            
            if ref_front.exists():
                front_comparison = self.agent.compare_with_reference(
                    aadhaar_front_path, ref_front, "Aadhaar front"
                )
                if front_comparison['success']:
                    comp_data = front_comparison['data']
                    status = "pass" if comp_data.get('recommendation') == 'approve' else \
                            "fail" if comp_data.get('recommendation') == 'reject' else "warning"
                    results['checks'].append({
                        "check_name": "Aadhaar Front Authenticity",
                        "status": status,
                        "message": f"Similarity: {comp_data.get('similarity_score', 0)}%, Layout: {comp_data.get('layout_match', 'unknown')}"
                    })
            
            if ref_back.exists():
                back_comparison = self.agent.compare_with_reference(
                    aadhaar_back_path, ref_back, "Aadhaar back"
                )
                if back_comparison['success']:
                    comp_data = back_comparison['data']
                    status = "pass" if comp_data.get('recommendation') == 'approve' else \
                            "fail" if comp_data.get('recommendation') == 'reject' else "warning"
                    results['checks'].append({
                        "check_name": "Aadhaar Back Authenticity",
                        "status": status,
                        "message": f"Similarity: {comp_data.get('similarity_score', 0)}%, Layout: {comp_data.get('layout_match', 'unknown')}"
                    })
            
            # Step 4: Extract resume information if provided
            resume_data = None
            if resume_path:
                print("[INFO] Extracting resume information...")
                resume_text = self.extract_pdf_text(resume_path)
                resume_result = self.agent.extract_resume_info(resume_text)
                
                if resume_result['success']:
                    resume_data = resume_result['data']
                    results['extracted_data']['resume'] = resume_data
                    results['checks'].append({
                        "check_name": "Resume Extraction",
                        "status": "pass",
                        "message": "Successfully extracted information from resume"
                    })
                else:
                    results['checks'].append({
                        "check_name": "Resume Extraction",
                        "status": "warning",
                        "message": f"Could not extract resume data: {resume_result.get('error', 'Unknown error')}"
                    })
            
            # Step 5: Verify form completeness
            print("[INFO] Verifying form completeness...")
            pdf_text = self.extract_pdf_text(details_form_path)
            form_result = self.agent.verify_form_completeness(pdf_text)
            
            if form_result['success']:
                form_data = form_result['data']
                results['extracted_data']['form'] = form_data
                
                if form_data.get('is_complete', False):
                    results['checks'].append({
                        "check_name": "Form Completeness",
                        "status": "pass",
                        "message": f"Form is {form_data.get('completeness_score', 0)}% complete"
                    })
                else:
                    results['checks'].append({
                        "check_name": "Form Completeness",
                        "status": "fail",
                        "message": f"Missing fields: {', '.join(form_data.get('missing_fields', []))}"
                    })
            
            # Step 6: Cross-verify all documents including resume
            print("[INFO] Cross-verifying all documents...")
            if front_result['success'] and back_result['success'] and form_result['success']:
                cross_verify_result = self.agent.cross_verify_documents(
                    front_result['data'],
                    back_result['data'],
                    form_result['data'],
                    resume_data
                )
                
                if cross_verify_result['success']:
                    verify_data = cross_verify_result['data']
                    results['extracted_data']['cross_verification'] = verify_data
                    
                    # Add individual verification checks
                    for check_name, check_data in verify_data.items():
                        if isinstance(check_data, dict) and 'status' in check_data:
                            results['checks'].append({
                                "check_name": check_name.replace('_', ' ').title(),
                                "status": check_data['status'],
                                "message": check_data.get('details', '')
                            })
                    
                    # Set overall status
                    overall = verify_data.get('overall_verification', {})
                    results['verification_status'] = overall.get('status', 'review_required')
                    results['confidence_score'] = overall.get('confidence', 0)
                    results['ai_analysis'] = overall.get('summary', '')
            
            # Calculate final status if not set
            if results['verification_status'] == 'pending':
                failed_checks = sum(1 for check in results['checks'] if check['status'] == 'fail')
                warning_checks = sum(1 for check in results['checks'] if check['status'] == 'warning')
                
                if failed_checks > 0:
                    results['verification_status'] = 'rejected'
                elif warning_checks > 0:
                    results['verification_status'] = 'review_required'
                else:
                    results['verification_status'] = 'approved'
            
            # Store in history
            self.verification_history.append(results)
            
            return results
            
        except Exception as e:
            results['verification_status'] = 'error'
            results['checks'].append({
                "check_name": "System Error",
                "status": "fail",
                "message": str(e)
            })
            return results
    
    def get_verification_history(self, employee_id=None):
        """Get verification history for an employee or all"""
        if employee_id:
            return [v for v in self.verification_history if v['employee_id'] == employee_id]
        return self.verification_history


# Example usage
if __name__ == "__main__":
    print("BGV Verification Module - Ready for integration")

# Made with Bob
