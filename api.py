from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl
import os
import tempfile
import shutil
from typing import Optional, List, Dict, Any
import asyncio
from pathlib import Path
import json
import sys
import traceback
import uvicorn
# Add speech module path if needed

from fastapi.middleware.cors import CORSMiddleware
import subprocess
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup CORS


# Import module functionality from backend directory
from video_agent import process_youtube_video, process_uploaded_video, save_uploaded_video, cleanup_video_file
from speech import Process_Audio
from legal import LegalDocumentSummarizer
from normal import GeneralDocumentSummarizer, SummarySettings
from resume import ResumeSummarizer
from website import fetch_transcript, summarize_content

app = FastAPI(title="Ultimate Summarization API", 
              description="API for video, audio, document and website summarization",
              version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Playwright on startup
@app.on_event("startup")
async def install_playwright_browser():
    try:
        logger.info("Checking Playwright browser installation...")
        # Check if browser is installed by trying to import playwright
        try:
            from playwright.async_api import async_playwright
            logger.info("Playwright is installed, checking browser...")
            
            # Check if browser binary exists
            browser_path = Path("/opt/render/.cache/ms-playwright/chromium-1161/chrome-linux/chrome")
            if not browser_path.exists():
                logger.info("Playwright browser not found, installing...")
                # Install Playwright browser
                result = subprocess.run(["playwright", "install", "chromium"], 
                                       capture_output=True, text=True, check=False)
                if result.returncode != 0:
                    logger.error(f"Failed to install Playwright browser: {result.stderr}")
                else:
                    logger.info("Playwright browser installed successfully")
            else:
                logger.info("Playwright browser already installed")
        except ImportError:
            logger.error("Playwright not installed, installing package and browser...")
            # Install playwright package first
            subprocess.run(["pip", "install", "playwright"], check=False)
            # Install browser
            subprocess.run(["playwright", "install", "chromium"], check=False)
    except Exception as e:
        logger.error(f"Error during Playwright setup: {str(e)}")

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

# Pydantic models for request validation
class YouTubeRequest(BaseModel):
    url: HttpUrl
    query: Optional[str] = "Summarize this video"

class VideoUploadQuery(BaseModel):
    query: Optional[str] = "Summarize this video"



class WebsiteRequest(BaseModel):
    url: HttpUrl
    summary_length: Optional[str] = "Medium"

# Video endpoints
@app.post("/api/summarize/youtube", summary="Summarize YouTube video")
async def summarize_youtube(request: YouTubeRequest):
    """
    Process and summarize a YouTube video based on the provided URL and query.
    
    Returns a JSON with the summary and analysis of the video content.
    """
    try:
        # Check for required environment variables
        if not os.getenv("OPENAI_API_KEY"):
            return JSONResponse(
                status_code=400,
                content={
                    "success": False, 
                    "error": "OpenAI API key is required for YouTube video processing. Set the OPENAI_API_KEY environment variable."
                }
            )
        
        # Try to get video summary
        result = process_youtube_video(str(request.url), request.query)
        
        # Check if there's an issue with captions
        if "can't retrieve the captions" in result or "can't access the captions" in result:
            logger.warning(f"Caption issue detected for URL: {request.url}")
            
            # Try a direct more aggressive approach using video_agent
            from video_agent import initialize_youtube_agent
            agent = initialize_youtube_agent()
            
            # First try direct caption fetching
            try:
                full_query = f"get_transcript {str(request.url)}"
                captions_response = agent.run(full_query)
                if captions_response and "transcript" in captions_response.content.lower():
                    # Now ask the question based on these captions
                    summary_query = f"{request.query}\n\nAnalyze this transcript: {captions_response.content}"
                    summary_response = agent.run(summary_query)
                    return {"success": True, "summary": summary_response.content}
            except Exception as caption_error:
                logger.error(f"Error in direct caption approach: {str(caption_error)}")
                
            # Fallback to analyze video using available metadata
            try:
                metadata_query = f"Analyze the YouTube video at {str(request.url)} using its title, description, and any available metadata. {request.query}"
                metadata_response = agent.run(metadata_query)
                return {
                    "success": True, 
                    "summary": metadata_response.content,
                    "warning": "This summary is based on video metadata, not transcript, due to caption retrieval issues."
                }
            except Exception as metadata_error:
                logger.error(f"Error in metadata approach: {str(metadata_error)}")
        
        # Return original result if no issues detected
        return {"success": True, "summary": result}
    except Exception as e:
        error_message = str(e)
        logger.error(f"YouTube summarizer error: {error_message}")
        if "API key" in error_message:
            # Handle API key errors more gracefully
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": f"API key error: {error_message}",
                    "hint": "Check that both GOOGLE_API_KEY and OPENAI_API_KEY environment variables are set correctly."
                }
            )
        raise HTTPException(status_code=500, detail=f"Error processing YouTube video: {error_message}")

@app.post("/summarize/video", summary="Summarize uploaded video")
async def summarize_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    query: Optional[str] = Form("Summarize this video")
):
    try:
        # Save the uploaded video
        temp_file_path = save_uploaded_video(await file.read())
        
        # Process the video
        result = process_uploaded_video(temp_file_path, query)
        
        # Schedule cleanup of the temporary file
        background_tasks.add_task(cleanup_video_file, temp_file_path)
        
        return {"success": True, "summary": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")

# Speech/Audio endpoint
@app.post("/api/process-audio", summary="Transcribe and summarize audio file")
async def process_audio_endpoint(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Upload an audio file to be transcribed and summarized.
    
    Returns a JSON with transcript and summary of the audio content.
    """
    temp_file_path = None
    try:
        # Get file extension or default to .mp3
        suffix = Path(file.filename).suffix if file.filename else ".mp3"
        
        # Create temp file to store the audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file_path = temp_file.name
            
            # Read file content
            file_content = await file.read()
            
            # Write to temp file
            temp_file.write(file_content)
            print(f"Audio saved to temporary file: {temp_file_path}, size: {len(file_content)} bytes")
        
        # Process the audio file
        result = Process_Audio(temp_file_path)
        
        # Schedule cleanup of temp file
        if temp_file_path:
            background_tasks.add_task(lambda: os.unlink(temp_file_path) if os.path.exists(temp_file_path) else None)
        
        # Check processing result
        if not result["success"]:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": result.get("error", "Audio processing failed")}
            )
        
        # Return successful response
        return {
            "success": True,
            "transcript": result["transcript"],
            "summary": result["summary"]
        }
    
    except Exception as e:
        # Print error for debugging
        print(f"Error processing audio: {str(e)}")
        traceback.print_exc()
        
        # Clean up temp file if it exists
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except:
                pass
        
        # Return error response
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Error processing audio: {str(e)}"}
        )
    


# Website endpoint
@app.post("/summarize/website", summary="Summarize website content")
async def summarize_website(request: WebsiteRequest):
    try:
        # Define word count mapping
        summary_word_count = {
            "Short": 100,
            "Medium": 300,
            "Long": 500
        }
        
        try:
            # Get content from website with improved timeout and retry settings
            logger.info(f"Attempting to fetch content from {request.url}")
            content = await fetch_transcript(str(request.url), max_retries=3, timeout=90)
        except Exception as fetch_error:
            logger.error(f"Error fetching website content: {str(fetch_error)}")
            error_msg = str(fetch_error)
            
            # Check if it's a Playwright browser error
            if any(error_text in error_msg.lower() for error_text in [
                "executable doesn't exist", 
                "playwright", 
                "browser", 
                "has been closed", 
                "target page"
            ]):
                logger.warning("Browser-related error detected, attempting recovery...")
                
                # Try to restart/reinstall Playwright
                try:
                    # Force browser cleanup and reinstallation
                    logger.info("Running browser reinstallation...")
                    subprocess.run(["playwright", "install", "--force", "chromium"], 
                                  check=False, capture_output=True)
                    
                    # Try with specific browser path if needed
                    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "/opt/render/.cache/ms-playwright"
                    
                    # Try with a much longer timeout and different config
                    logger.info("Retrying with more conservative settings...")
                    browser_config_override = {
                        "timeout": 120000,  # 2 minute timeout
                        "headless": True,
                        "args": [
                            "--no-sandbox", 
                            "--disable-dev-shm-usage",
                            "--disable-gpu",
                            "--disable-extensions"
                        ]
                    }
                    
                    # Import directly to access more configuration options
                    from crawl4ai import AsyncWebCrawler
                    from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
                    
                    # Try with more conservative settings
                    browser_config = BrowserConfig(**browser_config_override)
                    run_config = CrawlerRunConfig(timeout=120, wait_for=5000)
                    
                    async with AsyncWebCrawler(config=browser_config) as crawler:
                        logger.info(f"Attempting direct crawler fetch for {request.url}")
                        result = await crawler.arun(url=str(request.url), config=run_config)
                        content = result.markdown
                        
                        if not content or len(content.strip()) < 50:
                            raise ValueError("Retrieved content too short")
                        
                        logger.info(f"Successful recovery - got {len(content)} chars")
                    
                except Exception as recovery_error:
                    logger.error(f"Recovery attempt failed: {str(recovery_error)}")
                    
                    # If all browser attempts fail, try a fallback approach with a simple HTTP request
                    try:
                        logger.info("Attempting fallback with simple HTTP request...")
                        import httpx
                        import re
                        from bs4 import BeautifulSoup
                        
                        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                            response = await client.get(str(request.url))
                            response.raise_for_status()
                            
                            # Parse with BeautifulSoup
                            soup = BeautifulSoup(response.text, 'html.parser')
                            
                            # Remove script and style elements
                            for script in soup(["script", "style"]):
                                script.extract()
                                
                            # Get text and clean it
                            text = soup.get_text(separator=' ', strip=True)
                            text = re.sub(r'\s+', ' ', text)
                            
                            if len(text) > 500:  # Ensure we have enough content
                                content = text
                                logger.info(f"Fallback successful - got {len(content)} chars")
                            else:
                                raise ValueError("Insufficient content from fallback method")
                                
                    except Exception as fallback_error:
                        logger.error(f"All content retrieval methods failed: {str(fallback_error)}")
                        return JSONResponse(
                            status_code=500,
                            content={
                                "success": False,
                                "error": "Unable to retrieve website content after multiple attempts",
                                "url": str(request.url),
                                "details": "Server encountered browser issues that could not be resolved. This may be a temporary issue or related to the target website."
                            }
                        )
            else:
                # Return error for non-browser issues
                return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "error": f"Failed to fetch website content: {str(fetch_error)}",
                        "url": str(request.url)
                    }
                )
        
        # Get word count based on summary length
        word_count = summary_word_count.get(request.summary_length, 300)
        
        # Summarize content
        summary = await summarize_content(content, word_count)
        
        return {
            "success": True,
            "url": str(request.url),
            "summary_length": request.summary_length,
            "summary": summary
        }
    except Exception as e:
        logger.error(f"Website summarizer error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing website: {str(e)}")

# Root endpoint for basic health check
@app.get("/")
async def root():
    return {"status": "online", "message": "Ultimate Summarization API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 