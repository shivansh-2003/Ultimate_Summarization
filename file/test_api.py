import requests
import argparse
import os

def test_health():
    """Test the health check endpoint"""
    response = requests.get("http://localhost:8000/health")
    print(f"Health check status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_legal_summarization(pdf_path):
    """Test the legal document summarization endpoint"""
    if not os.path.exists(pdf_path):
        print(f"Error: File {pdf_path} does not exist")
        return False
    
    with open(pdf_path, 'rb') as f:
        files = {'file': (os.path.basename(pdf_path), f, 'application/pdf')}
        data = {'custom_question': 'What are the key points in this document?'}
        
        response = requests.post("http://localhost:8000/api/legal/summarize", 
                                files=files, data=data)
    
    print(f"Legal summarization status: {response.status_code}")
    if response.status_code == 200:
        print("Success! Legal document summarized correctly.")
        print("\nSummary excerpt:")
        print("-----------------")
        summary = response.json().get('summary', '')
        print(summary[:300] + "..." if len(summary) > 300 else summary)
        return True
    else:
        print(f"Error: {response.text}")
        return False

def test_general_summarization(document_path):
    """Test the general document summarization endpoint"""
    if not os.path.exists(document_path):
        print(f"Error: File {document_path} does not exist")
        return False
    
    with open(document_path, 'rb') as f:
        files = {'file': (os.path.basename(document_path), f, 'application/octet-stream')}
        data = {
            'conciseness': 'balanced',
            'extract_topics': 'true',
            'extract_key_points': 'true',
            'include_statistics': 'true'
        }
        
        response = requests.post("http://localhost:8000/api/general/summarize", 
                                files=files, data=data)
    
    print(f"General summarization status: {response.status_code}")
    if response.status_code == 200:
        print("Success! General document summarized correctly.")
        print("\nExecutive Summary excerpt:")
        print("---------------------------")
        summary = response.json().get('executive_summary', '')
        print(summary[:300] + "..." if len(summary) > 300 else summary)
        return True
    else:
        print(f"Error: {response.text}")
        return False

def test_resume_analysis(resume_path):
    """Test the resume analysis endpoint"""
    if not os.path.exists(resume_path):
        print(f"Error: File {resume_path} does not exist")
        return False
    
    with open(resume_path, 'rb') as f:
        files = {'file': (os.path.basename(resume_path), f, 'application/pdf')}
        data = {'job_description': 'Software Engineer with 3+ years of experience in Python development.'}
        
        response = requests.post("http://localhost:8000/api/resume/analyze", 
                                files=files, data=data)
    
    print(f"Resume analysis status: {response.status_code}")
    if response.status_code == 200:
        print("Success! Resume analyzed correctly.")
        print("\nNarrative Summary excerpt:")
        print("---------------------------")
        summary = response.json().get('narrative_summary', '')
        print(summary[:300] + "..." if len(summary) > 300 else summary)
        return True
    else:
        print(f"Error: {response.text}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test the Document Summarization API')
    parser.add_argument('--legal', type=str, help='Path to a legal PDF document for testing')
    parser.add_argument('--general', type=str, help='Path to a general document (PDF, DOCX, or TXT) for testing')
    parser.add_argument('--resume', type=str, help='Path to a resume PDF document for testing')
    
    args = parser.parse_args()
    
    print("Testing Document Summarization API...\n")
    
    # Always test health endpoint
    health_ok = test_health()
    
    if not health_ok:
        print("\nAPI health check failed. Make sure the API is running.")
        exit(1)
    
    # Test specific endpoints based on provided arguments
    if args.legal:
        print("\nTesting Legal Document Summarization...")
        test_legal_summarization(args.legal)
    
    if args.general:
        print("\nTesting General Document Summarization...")
        test_general_summarization(args.general)
    
    if args.resume:
        print("\nTesting Resume Analysis...")
        test_resume_analysis(args.resume)
    
    if not (args.legal or args.general or args.resume):
        print("\nNo specific endpoints tested. Use --legal, --general, or --resume options to test specific endpoints.")
        print("Example: python test_api.py --legal path/to/legal.pdf --resume path/to/resume.pdf") 