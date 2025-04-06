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

# Import module functionality from backend directory
from video_agent import process_youtube_video, process_uploaded_video, save_uploaded_video, cleanup_video_file

    # Try importing from backend first
from speech import process_audio

        # Define a placeholder function in case import fails
from document import UniversalDocumentSummarizer
from website import fetch_transcript, summarize_content
from resume_models import (
    ResumeData, ATSAnalysis, ResumeSummaryResult, 
    KeywordMatch, BasicInformation, Experience, Education,
    Certification, Project, Skill, SkillCategory
)
app = FastAPI(title="Ultimate Summarization API", 
              description="API for video, audio, document and website summarization",
              version="1.0.0")

# Pydantic models for request validation
class YouTubeRequest(BaseModel):
    url: HttpUrl
    query: Optional[str] = "Summarize this video"

class VideoUploadQuery(BaseModel):
    query: Optional[str] = "Summarize this video"

class DocumentSettings(BaseModel):
    conciseness: Optional[str] = "balanced"
    focus_areas: Optional[List[str]] = None
    job_description: Optional[str] = None
    custom_question: Optional[str] = None

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
        
        result = process_youtube_video(str(request.url), request.query)
        return {"success": True, "summary": result}
    except Exception as e:
        error_message = str(e)
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
        result = process_audio(temp_file_path)
        
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
    
# Document endpoint
@app.post("/summarize/document", summary="Summarize document")
async def summarize_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    mode: str = Form("general"),
    settings_json: Optional[str] = Form(None)
):
    try:
        # Create temp file to store the document
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)
        
        # Parse settings JSON if provided
        settings = None
        if settings_json:
            try:
                settings = json.loads(settings_json)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid settings JSON format")
        
        # Process the document
        summarizer = UniversalDocumentSummarizer()
        result = summarizer.summarize_document(temp_file_path, mode, settings)
        
        # Schedule cleanup
        background_tasks.add_task(lambda: os.unlink(temp_file_path))
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

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
        
        # Get content from website
        content = await fetch_transcript(str(request.url))
        
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
        raise HTTPException(status_code=500, detail=f"Error processing website: {str(e)}")

# Root endpoint for basic health check
@app.get("/")
async def root():
    return {"status": "online", "message": "Ultimate Summarization API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 