import os
import time
import tempfile
from pathlib import Path
from dotenv import load_dotenv

from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.youtube import YouTubeTools
from agno.tools.duckduckgo import DuckDuckGoTools

import google.generativeai as genai
from google.generativeai import upload_file, get_file

# Load environment variables
load_dotenv()

# Configure Google API
API_KEY = os.getenv("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    raise ValueError("Google API key not found. Please set the GOOGLE_API_KEY environment variable.")

def initialize_youtube_agent():
    """Initialize an agent for YouTube video processing."""
    return Agent(
        name="YouTube Video Summarizer",
        tools=[YouTubeTools()],
        show_tool_calls=True,
        description="You are a YouTube agent. Obtain the captions of a YouTube video and answer questions.",
        markdown=True
    )

def initialize_multimodal_agent():
    """Initialize an agent for processing uploaded video files."""
    return Agent(
        name="Video AI Summarizer",
        model=Gemini(id="gemini-2.0-flash-exp"),
        tools=[DuckDuckGoTools()],
        markdown=True,
    )

def process_youtube_video(youtube_url, query="Summarize this video"):
    """
    Process a YouTube video and return insights based on the query.
    
    Args:
        youtube_url (str): URL of the YouTube video
        query (str, optional): Query for the video analysis. Defaults to "Summarize this video".
        
    Returns:
        str: The response content from the agent
    """
    agent = initialize_youtube_agent()
    full_query = f"{query} {youtube_url}"
    response = agent.run(full_query)
    return response.content

def process_uploaded_video(video_path, query):
    """
    Process an uploaded video file and return insights based on the query.
    
    Args:
        video_path (str): Path to the video file
        query (str): Query for the video analysis
        
    Returns:
        str: The response content from the agent
    """
    agent = initialize_multimodal_agent()
    
    try:
        # Upload and process video file
        processed_video = upload_file(video_path)
        while processed_video.state.name == "PROCESSING":
            time.sleep(1)
            processed_video = get_file(processed_video.name)

        # Prompt generation for analysis
        analysis_prompt = (
            f"""
            Analyze the uploaded video for content and context.
            Respond to the following query using video insights and supplementary web research:
            {query}

            Provide a detailed, user-friendly, and actionable response.
            """
        )

        # AI agent processing
        response = agent.run(analysis_prompt, videos=[processed_video])
        return response.content
    
    except Exception as error:
        return f"An error occurred during analysis: {error}"

def save_uploaded_video(video_data):
    """
    Save uploaded video data to a temporary file.
    
    Args:
        video_data (bytes): Binary video data
        
    Returns:
        str: Path to the saved video file
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
        temp_video.write(video_data)
        return temp_video.name

def cleanup_video_file(video_path):
    """
    Clean up the temporary video file.
    
    Args:
        video_path (str): Path to the video file
    """
    Path(video_path).unlink(missing_ok=True)

# Example usage
if __name__ == "__main__":
    # Example 1: Process a YouTube video
    youtube_result = process_youtube_video("https://www.youtube.com/watch?v=QTGcccAXFjA")
    print("YouTube Video Analysis:")
    print(youtube_result)
    print("\n" + "-"*50 + "\n")
    
    # Example 2: Process a local video file
    # Uncomment and modify this section if you want to test with a local file
    """
    local_video_path = "path/to/your/video.mp4"
    query = "What is the main topic of this video?"
    
    local_result = process_uploaded_video(local_video_path, query)
    print("Local Video Analysis:")
    print(local_result)
    """ 