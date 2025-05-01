import streamlit as st
import os
import tempfile
import time
from pathlib import Path
import google.generativeai as genai
from google.generativeai import upload_file
from yt import summarize_youtube_video

# Import functions from your video_agent module
from video_agent import (
    process_youtube_video,
    initialize_multimodal_agent
)

def main():
    # Set page configuration
    st.set_page_config(
        page_title="Video Analysis Tool",
        page_icon="🎬",
        layout="wide"
    )
    
    # Application header
    st.title("🎬 AI Video Analysis Tool")
    st.markdown("""
    This application allows you to analyze videos using AI. You can either:
    - Analyze a YouTube video by providing a URL
    - Upload your own video file for analysis
    """)
    
    # Sidebar for API key input
    with st.sidebar:
        st.header("Configuration")
        api_key = st.text_input("Google API Key", type="password", help="Enter your Google API key here")
        
        if api_key:
            os.environ["GOOGLE_API_KEY"] = api_key
            genai.configure(api_key=api_key)
            st.success("API Key set successfully!")
        else:
            st.warning("Please enter your Google API key to use the application")
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This application uses the Google Gemini API to analyze video content.
        It can process YouTube videos or your own uploaded video files.
        """)
    
    # Create tabs for different functionalities
    tab1, tab2 = st.tabs(["YouTube Video Analysis", "Upload Video Analysis"])
    
    # YouTube video analysis tab
    with tab1:
        st.header("YouTube Video Analysis")
        youtube_url = st.text_input("Enter YouTube URL", placeholder="https://www.youtube.com/watch?v=...")
        query_type = st.radio(
            "Select analysis type",
            options=["Summary", "Key Points", "Custom Query"],
            horizontal=True
        )
        
        if query_type == "Custom Query":
            custom_query = st.text_area("Enter your custom query", placeholder="What is the main topic of this video?")
        
        yt_analyze_button = st.button("Analyze YouTube Video", type="primary", use_container_width=True)
        
        if yt_analyze_button and youtube_url:
            if not api_key:
                st.error("Please enter your Google API key in the sidebar first")
            else:
                with st.spinner("Analyzing YouTube video..."):
                    try:
                        # Determine query based on selection
                        if query_type == "Summary":
                            query = "Provide a comprehensive summary of this video"
                        elif query_type == "Key Points":
                            query = "Extract and list the key points from this video"
                        else:
                            query = custom_query
                        
                        # Process the YouTube video
                        result = process_youtube_video(youtube_url, query)
                        
                        # Display results
                        st.subheader("Analysis Results")
                        st.markdown(result)
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
                        st.exception(e)
    
    # Upload video analysis tab
    with tab2:
        st.header("Upload Your Own Video")
        uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "mov", "avi", "mkv"])
        
        query = st.text_area(
            "What would you like to know about this video?", 
            placeholder="Example: Summarize the main topics in this video",
            help="Be specific with your query to get the most relevant results"
        )
        
        upload_analyze_button = st.button("Analyze Uploaded Video", type="primary", use_container_width=True)
        
        if upload_analyze_button and uploaded_file is not None:
            if not api_key:
                st.error("Please enter your Google API key in the sidebar first")
            elif not query:
                st.warning("Please enter a query for the video analysis")
            else:
                with st.spinner("Processing uploaded video..."):
                    try:
                        # Create a temporary file
                        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}")
                        temp_file.write(uploaded_file.getvalue())
                        temp_file.close()
                        
                        st.info("Video uploaded! Now processing with Gemini. This may take a few minutes...")
                        
                        # Using direct Gemini API approach for upload
                        try:
                            processed_video = upload_file(temp_file.name)
                            
                            # Wait for processing to complete
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            for i in range(10):
                                # Check if the file is still processing
                                status_text.text(f"Processing video... ({i+1}/10)")
                                progress_bar.progress((i+1) * 10)
                                time.sleep(3)  # Wait between checks
                            
                            # Initialize the agent
                            agent = initialize_multimodal_agent()
                            
                            # Prompt generation for analysis
                            analysis_prompt = (
                                f"""
                                Analyze the uploaded video for content and context.
                                Respond to the following query using video insights and supplementary web research:
                                {query}

                                Provide a detailed, user-friendly, and actionable response.
                                """
                            )
                            
                            # Run the agent
                            response = agent.run(analysis_prompt, videos=[processed_video])
                            result = response.content
                            
                            # Display results
                            st.subheader("Analysis Results")
                            st.markdown(result)
                            
                        except Exception as gemini_error:
                            st.error(f"Gemini API error: {str(gemini_error)}")
                            st.error("This could be due to API limits, file format issues, or an unsupported video format.")
                            st.info("Alternative processing approach:")
                            
                            # Alternative implementation using simpler approach
                            try:
                                agent = initialize_multimodal_agent()
                                sample_analysis = agent.run(
                                    f"This is a video analysis request. The user asked: {query}. Please provide a helpful response "
                                    f"even though we cannot process the actual video content. Suggest what might be analyzed "
                                    f"in a video of this type and how the user might extract insights manually."
                                )
                                st.markdown(sample_analysis.content)
                            except Exception as fallback_error:
                                st.error(f"Fallback approach also failed: {str(fallback_error)}")
                        
                        # Clean up the temporary file
                        try:
                            Path(temp_file.name).unlink(missing_ok=True)
                        except Exception as cleanup_error:
                            st.warning(f"Could not clean up temporary file: {str(cleanup_error)}")
                            
                    except Exception as e:
                        st.error(f"An error occurred during processing: {str(e)}")
                        st.exception(e)

    st.title("YouTube Transcript to Detailed Notes Converter")

    youtube_link = st.text_input("Enter YouTube Video Link:")

    if youtube_link:
        try:
            video_id = youtube_link.split("=")[1]
            st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)
        except:
            st.error("Please enter a valid YouTube URL")

    if st.button("Get Detailed Notes") and youtube_link:
        with st.spinner("Generating summary..."):
            summary = summarize_youtube_video(youtube_link)
            
        if summary:
            st.markdown("## Detailed Notes:")
            st.write(summary)
        else:
            st.error("Failed to generate summary. Please check the YouTube link and try again.")

if __name__ == "__main__":
    main()