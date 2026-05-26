"""
Resume Parser - Extract email and other details from resume files
"""

import re
from pathlib import Path
import PyPDF2
import docx

def extract_email_from_text(text):
    """Extract email address from text using regex"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else None

def extract_phone_from_text(text):
    """Extract phone number from text"""
    phone_pattern = r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]'
    phones = re.findall(phone_pattern, text)
    return phones[0] if phones else None

def parse_pdf_resume(file_path):
    """Parse PDF resume and extract information"""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            
            return {
                'email': extract_email_from_text(text),
                'phone': extract_phone_from_text(text),
                'text': text[:500]  # First 500 chars for preview
            }
    except Exception as e:
        print(f"Error parsing PDF {file_path}: {str(e)}")
        return {'email': None, 'phone': None, 'text': ''}

def parse_docx_resume(file_path):
    """Parse DOCX resume and extract information"""
    try:
        doc = docx.Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        
        return {
            'email': extract_email_from_text(text),
            'phone': extract_phone_from_text(text),
            'text': text[:500]  # First 500 chars for preview
        }
    except Exception as e:
        print(f"Error parsing DOCX {file_path}: {str(e)}")
        return {'email': None, 'phone': None, 'text': ''}

def parse_resume(file_path):
    """Parse resume file and extract information"""
    file_path = Path(file_path)
    
    if not file_path.exists():
        return {'email': None, 'phone': None, 'text': '', 'error': 'File not found'}
    
    if file_path.suffix.lower() == '.pdf':
        return parse_pdf_resume(file_path)
    elif file_path.suffix.lower() in ['.docx', '.doc']:
        return parse_docx_resume(file_path)
    else:
        return {'email': None, 'phone': None, 'text': '', 'error': 'Unsupported format'}

if __name__ == "__main__":
    # Test with Anil Kumar's resume
    result = parse_resume("Resumes/Anil_Kumar_Data_Engineer_Resume.pdf")
    print(f"Email found: {result.get('email')}")
    print(f"Phone found: {result.get('phone')}")

# Made with Bob
