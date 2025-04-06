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

# Import module functionality from backend directory
from video_agent import process_youtube_video, process_uploaded_video, save_uploaded_video, cleanup_video_file
from speech import process_audio
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
@app.post("/summarize/youtube", summary="Summarize YouTube video")
async def summarize_youtube(request: YouTubeRequest):
    try:
        result = process_youtube_video(str(request.url), request.query)
        return {"success": True, "summary": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing YouTube video: {str(e)}")

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
@app.post("/summarize/audio", summary="Transcribe and summarize audio")
async def summarize_audio(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    try:
        # Create temp file to store the audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)
        
        # Process the audio file
        result = process_audio(temp_file_path)
        
        # Schedule cleanup
        background_tasks.add_task(lambda: os.unlink(temp_file_path))
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")

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