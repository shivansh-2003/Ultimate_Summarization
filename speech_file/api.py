# speech/app.py - FastAPI endpoint for speech.py
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import tempfile
import os
from pathlib import Path
import traceback
from speech_file import process_audio
import uvicorn
# Create FastAPI app
app = FastAPI(
    title="Speech Processing API",
    description="API for transcribing and summarizing audio files",
    version="1.0.0"
)

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

@app.get("/", summary="API Health Check")
async def root():
    """Check if the API is running."""
    return {"status": "online", "message": "Speech Processing API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)