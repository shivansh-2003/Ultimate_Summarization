import os
from dotenv import load_dotenv
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

load_dotenv()  # load all the environment variables
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

prompt = """You are Youtube video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in points
within 250 words. Please provide the summary of the text given here:  """


## getting the transcript data from yt videos
def extract_transcript_details(youtube_video_url):
    try:
        # Extract video ID from various YouTube URL formats
        if "youtube.com/watch?v=" in youtube_video_url:
            video_id = youtube_video_url.split("watch?v=")[1].split("&")[0]
        elif "youtu.be/" in youtube_video_url:
            video_id = youtube_video_url.split("youtu.be/")[1].split("?")[0]
        else:
            raise ValueError("Invalid YouTube URL format")
        
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)

        transcript = ""
        for i in transcript_text:
            transcript += " " + i["text"]

        return transcript

    except ValueError as e:
        raise e
    except Exception as e:
        raise Exception(f"Failed to retrieve transcript: {str(e)}")
    
## getting the summary based on Prompt from Google Gemini Pro
def generate_gemini_content(transcript_text, prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt+transcript_text)
        return response.text
    except Exception as e:
        raise Exception(f"Failed to generate summary with Gemini: {str(e)}")

def summarize_youtube_video(youtube_link, custom_prompt=None):
    """
    Main function to summarize a YouTube video
    
    Args:
        youtube_link (str): URL of the YouTube video
        custom_prompt (str, optional): Custom prompt to use for summarization
    
    Returns:
        str: Summary of the video or None if failed
    """
    try:
        transcript_text = extract_transcript_details(youtube_link)
        if transcript_text:
            # Use custom prompt if provided, otherwise use default
            summary_prompt = custom_prompt if custom_prompt else prompt
            summary = generate_gemini_content(transcript_text, summary_prompt)
            return summary
        return None
    except Exception as e:
        # Log the error but don't print to stdout in API context
        error_message = f"Error summarizing video: {str(e)}"
        # We'll allow the API to handle and format this error
        raise Exception(error_message)

# Example usage
if __name__ == "__main__":
    youtube_link = "https://www.youtube.com/watch?v=e3MX7HoGXug&t=164s"
    summary = summarize_youtube_video(youtube_link)
    if summary:
        print("Summary:")
        print(summary)
        
    # Example with custom prompt
    custom_prompt = """You are Youtube video summarizer. You will be taking the transcript text
    and extracting the main technical concepts mentioned in the video.
    Provide the summary in bullet points. Please analyze the text given here: """
    
    custom_summary = summarize_youtube_video(youtube_link, custom_prompt)
    if custom_summary:
        print("\nCustom Summary:")
        print(custom_summary)




