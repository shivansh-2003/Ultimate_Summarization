# video/api.py
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl
import os
import tempfile
from typing import Optional
from pathlib import Path
import uvicorn

# Import functionality from video_agent.py
from video_agent import (
    process_youtube_video, 
    process_uploaded_video, 
    save_uploaded_video, 
    cleanup_video_file
)

# Create FastAPI app
app = FastAPI(
    title="Video Processing API",
    description="API for YouTube and video file summarization",
    version="1.0.0"
)

# Pydantic models for request validation
class YouTubeRequest(BaseModel):
    url: HttpUrl
    query: Optional[str] = "Summarize this video"

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

@app.post("/api/summarize/video", summary="Summarize uploaded video")
async def summarize_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    query: Optional[str] = Form("Summarize this video")
):
    """
    Upload a video file to be processed and summarized.
    
    Returns a JSON with the summary and analysis of the video content.
    """
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

# Root endpoint for basic health check
@app.get("/", summary="API Health Check")
async def root():
    """Check if the API is running."""
    return {"status": "online", "message": "Video Processing API is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)