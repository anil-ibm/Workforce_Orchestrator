"""
Test script for BGV verification system
"""

import sys
import os
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8')

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

try:
    from bgv_verification import BGVVerificationEngine, GeminiAgent
    print("[OK] BGV verification module imported successfully")
except ImportError as e:
    print(f"[ERROR] Failed to import BGV module: {e}")
    sys.exit(1)

# Test configuration
BASE_DIR = Path(__file__).parent
REFERENCE_DOCS_PATH = BASE_DIR / "data"

def test_gemini_connection(api_key):
    """Test connection to Gemini API"""
    print("\n[TEST] Testing Gemini API connection...")
    
    try:
        agent = GeminiAgent(api_key)
        
        # Simple test using the agent's model
        test_prompt = "Respond with 'OK' if you can read this message."
        response = agent.model.generate_content(test_prompt)
        
        if response and response.text:
            print("[OK] Gemini API connection successful")
            print(f"[INFO] Response: {response.text[:50]}...")
            return True
        else:
            print("[ERROR] No response from Gemini API")
            return False
            
    except Exception as e:
        print(f"[ERROR] Connection test failed: {e}")
        return False

def test_reference_documents():
    """Check if reference documents exist"""
    print("\n[TEST] Checking reference documents...")
    
    required_files = [
        "aadhaar_front.png",
        "aadhaar_back.png",
        "sample_details_form.pdf"
    ]
    
    all_exist = True
    for filename in required_files:
        filepath = REFERENCE_DOCS_PATH / filename
        if filepath.exists():
            print(f"[OK] Found: {filename}")
        else:
            print(f"[ERROR] Missing: {filename}")
            all_exist = False
    
    return all_exist

def test_bgv_engine(api_key):
    """Test BGV engine initialization"""
    print("\n[TEST] Testing BGV engine initialization...")
    
    try:
        engine = BGVVerificationEngine(api_key, REFERENCE_DOCS_PATH)
        print("[OK] BGV engine initialized successfully")
        return True
    except Exception as e:
        print(f"[ERROR] BGV engine initialization failed: {e}")
        return False

def main():
    print("=" * 60)
    print("BGV VERIFICATION SYSTEM TEST")
    print("=" * 60)
    
    # Load config
    import json
    config_file = BASE_DIR / "config" / "workflow_config.json"
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        api_key = config.get('gemini_api_key')
        
        if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
            print("[ERROR] Gemini API key not configured in config/workflow_config.json")
            print("Please add your API key to the config file")
            return False
        
        print(f"[OK] API key loaded from config (length: {len(api_key)})")
        
    except Exception as e:
        print(f"[ERROR] Failed to load config: {e}")
        return False
    
    # Run tests
    results = []
    
    results.append(("Gemini API Connection", test_gemini_connection(api_key)))
    results.append(("Reference Documents", test_reference_documents()))
    results.append(("BGV Engine", test_bgv_engine(api_key)))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed! BGV system is ready to use.")
        print("\nNext steps:")
        print("1. Ensure API server is running: python scripts/workforce_orchestrator.py --serve-api 8050")
        print("2. Open bgv_portal.html in your browser")
        print("3. Upload test documents and verify the system works")
        return True
    else:
        print("\n[WARNING] Some tests failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

# Made with Bob
