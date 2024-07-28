import streamlit as st
from transformers import pipeline
import assemblyai as aai
import os

# Set AssemblyAI API key
#aai.settings.api_key = "your assembly ai api key"

# Initialize the summarizer pipeline
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")


def transcribe_audio(file_path):
    try:
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(file_path)
        return transcript.text
    except Exception as e:
        st.error(f"Error in transcription: {e}")
        return None


def split_text(text, max_length=1000):
    """Splits text into chunks of a specified maximum length."""
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    for word in words:
        if current_length + len(word) + 1 <= max_length:
            current_chunk.append(word)
            current_length += len(word) + 1
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_length = len(word) + 1
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks


def summarize_text(text):
    try:
        chunks = split_text(text)
        summaries = [summarizer(chunk, max_length=130, min_length=30, do_sample=False)[0]['summary_text'] for chunk in chunks]
        bullet_points = "\n".join([f"- {summary}" for summary in summaries])
        return bullet_points
    except Exception as e:
        st.error(f"Error in summarization: {e}")
        return "Summary could not be generated."


def main():
    st.title("Audio Summarization")

    # File upload
    uploaded_file = st.file_uploader("Choose an audio file...", type=["mp3", "mp4", "wav", "m4a"])

    if uploaded_file is not None:
        file_path = os.path.join("/tmp", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        if st.button("Transcribe and Summarize"):
            with st.spinner('Transcribing audio...'):
                transcript_text = transcribe_audio(file_path)
                if transcript_text:
                    with st.spinner('Summarizing text...'):
                        summary_text = summarize_text(transcript_text)
                        st.write("Summary:")
                        st.markdown(summary_text)
                else:
                    st.error("Transcription failed. Please try again.")


if __name__ == "__main__":
    main()
