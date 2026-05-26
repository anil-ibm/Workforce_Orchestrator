"""
Generate candidate screening records from resumes in the Resumes folder
This script scans all PDF/DOCX files and creates candidate entries
Extracts email addresses from resume content
"""

import os
import json
from pathlib import Path
import re
import sys
import io

# Set UTF-8 encoding for console output on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Import resume parser
try:
    from resume_parser import parse_resume
    PARSER_AVAILABLE = True
except ImportError:
    PARSER_AVAILABLE = False
    print("[WARNING] Resume parser not available. Install PyPDF2 and python-docx for email extraction.")

def extract_candidate_info_from_filename(filename):
    """Extract candidate information from resume filename"""
    # Remove extension
    name_part = Path(filename).stem
    
    # Common patterns in filenames
    # Example: "Anil_Kumar_Data_Engineer_Resume.pdf" or "Sarah_Ultra_Detailed.docx"
    
    # Remove common suffixes
    name_part = re.sub(r'_(Resume|Ultra_Detailed|Detailed|CV)$', '', name_part, flags=re.IGNORECASE)
    
    # Split by underscore and extract name
    parts = name_part.split('_')
    
    # First part is usually first name, second is last name or role
    if len(parts) >= 2:
        first_name = parts[0]
        # Check if second part looks like a last name (capitalized) or role
        if parts[1][0].isupper() and len(parts[1]) < 15:
            last_name = parts[1]
            candidate_name = f"{first_name} {last_name}"
        else:
            candidate_name = first_name
    else:
        candidate_name = parts[0]
    
    return candidate_name

def generate_employee_id():
    """Generate a random employee ID"""
    import random
    return f"{random.randint(100, 999)}EBC{random.randint(100, 999)}"

def detect_role_from_filename(filename):
    """Try to detect role from filename"""
    filename_lower = filename.lower()
    
    role_keywords = {
        'genai': 'GenAI Developer',
        'data_engineer': 'Data Engineer',
        'developer': 'Software Developer',
        'analyst': 'Business Analyst',
        'manager': 'Project Manager',
        'architect': 'Solution Architect',
        'consultant': 'Technical Consultant'
    }
    
    for keyword, role in role_keywords.items():
        if keyword in filename_lower:
            return role
    
    return 'Software Engineer'  # Default role

def scan_resumes_folder(resumes_path='Resumes'):
    """Scan Resumes folder and generate candidate records with email extraction"""
    resumes_dir = Path(resumes_path)
    
    if not resumes_dir.exists():
        print(f"Error: {resumes_path} directory not found")
        return []
    
    candidates = []
    supported_extensions = ['.pdf', '.docx', '.doc']
    
    for resume_file in resumes_dir.iterdir():
        if resume_file.suffix.lower() in supported_extensions:
            candidate_name = extract_candidate_info_from_filename(resume_file.name)
            role = detect_role_from_filename(resume_file.name)
            
            # Extract email from resume if parser is available
            email = None
            phone = None
            if PARSER_AVAILABLE:
                try:
                    parsed_data = parse_resume(resume_file)
                    email = parsed_data.get('email')
                    phone = parsed_data.get('phone')
                except Exception as e:
                    print(f"[WARNING] Could not parse {resume_file.name}: {str(e)}")
            
            # Generate default email if not found
            if not email:
                email = f"{candidate_name.lower().replace(' ', '.')}@example.com"
            
            candidate = {
                'candidateName': candidate_name,
                'employeeId': generate_employee_id(),
                'role': role,
                'experience': f"{5 + len(candidate_name) % 10} years",  # Varied experience
                'skills': 'Python, Java, Cloud, AI/ML',  # Default skills
                'location': 'Bangalore',
                'cvUploaded': 'Yes',
                'status': 'Nominated',
                'resumeFile': resume_file.name,
                'email': email,
                'phone': phone or 'N/A'
            }
            
            candidates.append(candidate)
            print(f"[OK] Added: {candidate_name} ({role}) - Email: {email}")
    
    return candidates

def save_candidates_json(candidates, output_file='data/screening_candidates.json'):
    """Save candidates to JSON file"""
    output_path = Path(output_file)
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(candidates, f, indent=2, ensure_ascii=False)
    
    print(f"\n[OK] Saved {len(candidates)} candidates to {output_file}")

def generate_javascript_array(candidates):
    """Generate JavaScript array code for dashboard.html"""
    js_code = "      const screeningRecords = [\n"
    
    for candidate in candidates:
        js_code += "        {\n"
        js_code += f"          candidateName: \"{candidate['candidateName']}\",\n"
        js_code += f"          employeeId: \"{candidate['employeeId']}\",\n"
        js_code += f"          role: \"{candidate['role']}\",\n"
        js_code += f"          experience: \"{candidate['experience']}\",\n"
        js_code += f"          skills: \"{candidate['skills']}\",\n"
        js_code += f"          location: \"{candidate['location']}\",\n"
        js_code += f"          cvUploaded: \"{candidate['cvUploaded']}\",\n"
        js_code += f"          status: \"{candidate['status']}\",\n"
        js_code += f"          email: \"{candidate['email']}\",\n"
        js_code += f"          phone: \"{candidate['phone']}\"\n"
        js_code += "        },\n"
    
    js_code += "      ];\n"
    
    return js_code

if __name__ == "__main__":
    print("=" * 60)
    print("Generating Candidate Records from Resumes")
    print("=" * 60)
    print()
    
    # Scan resumes folder
    candidates = scan_resumes_folder()
    
    if not candidates:
        print("\nNo resume files found in Resumes folder")
        exit(1)
    
    # Save to JSON
    save_candidates_json(candidates)
    
    # Generate JavaScript code
    js_code = generate_javascript_array(candidates)
    
    # Save JavaScript code to file
    with open('screening_records.js', 'w', encoding='utf-8') as f:
        f.write(js_code)
    
    print(f"[OK] Generated JavaScript code in screening_records.js")
    print()
    print("=" * 60)
    print("Next Steps:")
    print("=" * 60)
    print("1. Copy the content from screening_records.js")
    print("2. Replace the screeningRecords array in dashboard.html (around line 3089)")
    print("3. Refresh the dashboard to see all candidates")
    print("=" * 60)

# Made with Bob
