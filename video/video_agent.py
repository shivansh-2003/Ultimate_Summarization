import os
import time
import tempfile
from pathlib import Path
from dotenv import load_dotenv

from agno.agent import Agent as AgnoAgent
from agno.tools.youtube import YouTubeTools
from phi.agent import Agent as PhiAgent
from phi.model.google import Gemini
from phi.tools.duckduckgo import DuckDuckGo
from agno.models.openai import OpenAIChat  # Import OpenAI from agno

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

# For agno library, check for OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY environment variable not set. YouTube analysis may not work.")

def initialize_youtube_agent():
    """Initialize an agent for YouTube video processing."""
    if OPENAI_API_KEY:
        # Use OpenAI model since AgnoAgent works best with it
        model = OpenAIChat(api_key=OPENAI_API_KEY)
        return AgnoAgent(
            name="YouTube Video Summarizer",
            model=model,
            tools=[YouTubeTools()],
            show_tool_calls=True,
            description="You are a YouTube agent. Obtain the captions of a YouTube video and answer questions.",
            markdown=True
        )
    else:
        # Fallback to default - may not work without OpenAI API key
        return AgnoAgent(
            name="YouTube Video Summarizer",
            tools=[YouTubeTools()],
            show_tool_calls=True,
            description="You are a YouTube agent. Obtain the captions of a YouTube video and answer questions.",
            markdown=True
        )

def initialize_multimodal_agent():
    """Initialize an agent for processing uploaded video files."""
    return PhiAgent(
        name="Video AI Summarizer",
        model=Gemini(id="gemini-2.0-flash-exp"),
        tools=[DuckDuckGo()],
        show_tool_calls=True,
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
        # Upload and process video file - using the approach from 1.py
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
        # Fallback approach if video processing fails
        try:
            fallback_prompt = (
                f"This is a video analysis request. The user asked: {query}. "
                f"Please provide a helpful response even though we cannot process the actual video content. "
                f"Suggest what might be analyzed in a video of this type and how the user might extract insights manually."
            )
            
            response = agent.run(fallback_prompt)
            return response.content + "\n\n(Note: Direct video processing failed. This is a general response.)"
        except:
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
    '''
    youtube_result = process_youtube_video("https://www.youtube.com/watch?v=QTGcccAXFjA")
    print("YouTube Video Analysis:")
    print(youtube_result)
    print("\n" + "-"*50 + "\n")
    '''
    # Example 2: Process a local video file
    # Uncomment and modify this section if you want to test with a local file
    
    local_video_path = "/Users/shivanshmahajan/Downloads/video.mp4"
    query = "Summarize the video min 400"
    
    local_result = process_uploaded_video(local_video_path, query)
    print("Local Video Analysis:")
    print(local_result)
    