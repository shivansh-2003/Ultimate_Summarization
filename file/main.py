import os
import tempfile
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from legal import LegalDocumentSummarizer
from normal import GeneralDocumentSummarizer, SummarySettings
from resume import ResumeSummarizer

app = FastAPI(
    title="Document Summarization API",
    description="API for summarizing legal documents, general documents, and resumes",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the summarizers (lazy loading)
legal_summarizer = None
general_summarizer = None
resume_summarizer = None

def get_legal_summarizer():
    global legal_summarizer
    if legal_summarizer is None:
        legal_summarizer = LegalDocumentSummarizer()
    return legal_summarizer

def get_general_summarizer():
    global general_summarizer
    if general_summarizer is None:
        general_summarizer = GeneralDocumentSummarizer()
    return general_summarizer

def get_resume_summarizer():
    global resume_summarizer
    if resume_summarizer is None:
        resume_summarizer = ResumeSummarizer()
    return resume_summarizer

# Request/Response models
class LegalSummaryResponse(BaseModel):
    document_type: str
    summary: str
    processing_time: float

class LegalSummaryRequest(BaseModel):
    custom_question: Optional[str] = None

class GeneralSummaryRequest(BaseModel):
    conciseness: str = "balanced"
    focus_areas: List[str] = []
    extract_topics: bool = True
    extract_key_points: bool = True
    include_statistics: bool = False
    summary_length_percentage: Optional[float] = None

class ResumeAnalysisRequest(BaseModel):
    job_description: Optional[str] = None

# Routes for Legal Document Summarization
@app.post("/api/legal/summarize", response_model=LegalSummaryResponse)
async def summarize_legal_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    custom_question: Optional[str] = Form(None)
):
    """Summarize a legal document (PDF format)"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Save uploaded file to temp directory
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_file_path = temp_file.name
        
        contents = await file.read()
        with open(temp_file_path, 'wb') as f:
            f.write(contents)
            
        # Process the document
        summarizer = get_legal_summarizer()
        result = summarizer.generate_summary(temp_file_path, custom_question)
        
        # Clean up temp file in the background
        background_tasks.add_task(os.unlink, temp_file_path)
        
        return result
    except Exception as e:
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        raise HTTPException(status_code=500, detail=f"Error processing legal document: {str(e)}")

# Routes for General Document Summarization
@app.post("/api/general/summarize")
async def summarize_general_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    conciseness: str = Form("balanced"),
    extract_topics: bool = Form(True),
    extract_key_points: bool = Form(True),
    include_statistics: bool = Form(False),
    summary_length_percentage: Optional[float] = Form(None)
):
    """Summarize a general document (PDF, DOCX, or TXT format)"""
    valid_extensions = ['.pdf', '.docx', '.txt']
    if not any(file.filename.lower().endswith(ext) for ext in valid_extensions):
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file format. Supported formats: {', '.join(valid_extensions)}"
        )
    
    try:
        # Save uploaded file to temp directory
        file_extension = os.path.splitext(file.filename)[1].lower()
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
        temp_file_path = temp_file.name
        
        contents = await file.read()
        with open(temp_file_path, 'wb') as f:
            f.write(contents)
            
        # Configure settings
        settings = SummarySettings(
            conciseness=conciseness,
            extract_topics=extract_topics,
            extract_key_points=extract_key_points,
            include_statistics=include_statistics,
            summary_length_percentage=summary_length_percentage
        )
            
        # Process the document
        summarizer = get_general_summarizer()
        result = summarizer.summarize_document(temp_file_path, settings.model_dump())
        
        # Clean up temp file in the background
        background_tasks.add_task(os.unlink, temp_file_path)
        
        # Convert result to dictionary (JSON serializable)
        return result.model_dump()
    except Exception as e:
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

# Routes for Resume Summarization and Analysis
@app.post("/api/resume/analyze")
async def analyze_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    job_description: Optional[str] = Form(None)
):
    """Analyze a resume (PDF format) with optional job description for ATS comparison"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported for resumes")
    
    try:
        # Save uploaded file to temp directory
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_file_path = temp_file.name
        
        contents = await file.read()
        with open(temp_file_path, 'wb') as f:
            f.write(contents)
            
        # Process the resume
        summarizer = get_resume_summarizer()
        result = summarizer.process_resume_file(temp_file_path, job_description)
        
        # Clean up temp file in the background
        background_tasks.add_task(os.unlink, temp_file_path)
        
        # Convert result to dictionary (JSON serializable)
        return result.model_dump()
    except Exception as e:
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 