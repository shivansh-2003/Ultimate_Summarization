import streamlit as st
from transformers import pipeline
import assemblyai as aai
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Set AssemblyAI API key
#aai.settings.api_key = "your assembly ai api key"

# Initialize the summarizer pipeline
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")


def transcribe_audio(file_path):
    """
    Transcribe audio file to text.
    
    Args:
        file_path (str): Path to the audio file
        
    Returns:
        str or None: Transcribed text or None if failed
    """
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


def split_text_recursive(text, chunk_size=1000, chunk_overlap=200):
    """
    Split text into manageable chunks using LangChain's RecursiveCharacterTextSplitter.
    
    Args:
        text (str): Text to split
        chunk_size (int): Maximum size of each chunk
        chunk_overlap (int): Overlap between chunks to maintain context
        
    Returns:
        list: List of Document objects with text chunks
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    # Split text into Document objects
    documents = text_splitter.create_documents([text])
    
    # Return the list of Document objects
    return documents


def summarize_text(text, use_recursive_splitter=True):
    """
    Summarize text using transformer model.
    
    Args:
        text (str): Text to summarize
        use_recursive_splitter (bool): Whether to use the recursive text splitter
        
    Returns:
        str: Bullet-point summary
    """
    try:
        if use_recursive_splitter:
            # Use the advanced recursive splitter
            doc_chunks = split_text_recursive(text)
            chunks = [doc.page_content for doc in doc_chunks]
        else:
            # Use the basic word-based splitter
            chunks = split_text(text)
            
        summaries = [summarizer(chunk, max_length=130, min_length=30, do_sample=False)[0]['summary_text'] for chunk in chunks]
        bullet_points = "\n".join([f"- {summary}" for summary in summaries])
        return bullet_points
    except Exception as e:
        st.error(f"Error in summarization: {e}")
        return "Summary could not be generated."


def process_audio(file_path):
    """
    Process audio file: transcribe and summarize.
    
    Args:
        file_path (str): Path to the audio file
        
    Returns:
        dict: Result with transcript and summary
    """
    transcript = transcribe_audio(file_path)
    if not transcript:
        return {"success": False, "error": "Transcription failed"}
    
    summary = summarize_text(transcript)
    return {
        "success": True,
        "transcript": transcript,
        "summary": summary
    }


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
                result = process_audio(file_path)
                if result["success"]:
                    with st.spinner('Summarizing text...'):
                        st.write("Summary:")
                        st.markdown(result["summary"])
                else:
                    st.error(result["error"])


if __name__ == "__main__":
    main()
