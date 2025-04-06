import streamlit as st
from speech_file import process_audio 
from dotenv import load_dotenv
import os
import traceback
from langchain_openai import ChatOpenAI
import openai
load_dotenv()

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize the ChatOpenAI model
chat_model = ChatOpenAI(model="gpt-4o-mini")  

def main():
    st.title("Audio Summarization App")

    # File upload
    uploaded_file = st.file_uploader("Choose an audio file...", type=["mp3", "mp4", "wav", "m4a"])

    if uploaded_file is not None:
        file_path = f"/tmp/{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        if st.button("Transcribe and Summarize"):
            with st.spinner('Transcribing and summarizing audio...'):
                try:
                    result = process_audio(file_path)
                    if result["success"]:
                        st.success("Processing successful!")
                        
                        # Display transcript in an expandable section
                        with st.expander("View Full Transcript"):
                            st.write(result["transcript"])
                        
                        # Display the summary prominently
                        st.subheader("Summary")
                        st.markdown(result["summary"])
                    else:
                        st.error(result["error"])
                except Exception as e:
                    st.error(f"Error processing audio: {str(e)}")
                    st.error(traceback.format_exc())

if __name__ == "__main__":
    main()