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
        video_id = youtube_video_url.split("=")[1]
        
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)

        transcript = ""
        for i in transcript_text:
            transcript += " " + i["text"]

        return transcript

    except Exception as e:
        raise e
    
## getting the summary based on Prompt from Google Gemini Pro
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt+transcript_text)
    return response.text

def summarize_youtube_video(youtube_link):
    """
    Main function to summarize a YouTube video
    """
    try:
        transcript_text = extract_transcript_details(youtube_link)
        if transcript_text:
            summary = generate_gemini_content(transcript_text, prompt)
            return summary
        return None
    except Exception as e:
        print(f"Error summarizing video: {e}")
        return None

# Example usage
if __name__ == "__main__":
    youtube_link = "https://www.youtube.com/watch?v=e3MX7HoGXug&t=164s"
    summary = summarize_youtube_video(youtube_link)
    if summary:
        print("Summary:")
        print(summary)




