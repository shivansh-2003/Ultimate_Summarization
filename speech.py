import os
import openai
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain.text_splitter import RecursiveCharacterTextSplitter
import assemblyai as aai
from dotenv import load_dotenv

load_dotenv()

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize the ChatOpenAI model
chat_model = ChatOpenAI(model="gpt-4o-mini")

def transcribe_audio(file_path):
    """Transcribe audio file to text using AssemblyAI."""
    try:
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(file_path)
        return transcript.text
    except Exception as e:
        print(f"Error in transcription: {e}")
        return None

def split_text_recursive(text, chunk_size=1000, chunk_overlap=100):
    """Split text into manageable chunks using LangChain's RecursiveCharacterTextSplitter."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    documents = text_splitter.create_documents([text])
    return documents

def summarize_text(text, max_summary_length=2000):
    """
    Create a concise summary of the text, keeping the total summary within
    the specified maximum length.
    
    Args:
        text: The text to summarize
        max_summary_length: Maximum length of the entire summary
        
    Returns:
        A concise summary of the text
    """
    try:
        # Split text into chunks
        doc_chunks = split_text_recursive(text)
        chunks = [doc.page_content for doc in doc_chunks]
        
        # Calculate target summary length per chunk
        target_length_per_chunk = max_summary_length // len(chunks)
        
        # Create prompt template
        prompt_template = """
        Summarize the following text in a concise manner, focusing on the main points and key details.
        Keep your summary to approximately {length} words.
        
        TEXT TO SUMMARIZE:
        {text}
        
        CONCISE SUMMARY:
        """
        
        chunk_summaries = []
        for chunk in chunks:
            try:
                # Create a prompt with target length for this chunk
                prompt = prompt_template.format(
                    length=target_length_per_chunk // 5,  # Convert to approx word count
                    text=chunk
                )
                
                # Create message and invoke the model
                messages = [HumanMessage(content=prompt)]
                response = chat_model.invoke(messages)
                
                # Extract the summary from the response
                chunk_summary = response.content.strip()
                chunk_summaries.append(chunk_summary)
                
            except Exception as e:
                print(f"Error summarizing chunk: {e}")
                chunk_summaries.append("This section could not be summarized.")
        
        # Combine the summaries into a coherent whole
        combined_summary = " ".join(chunk_summaries)
        
        # Generate a final, cohesive summary if there are multiple chunks
        if len(chunks) > 1:
            try:
                final_prompt = f"""
                Create a coherent, unified summary from these partial summaries:
                
                {combined_summary}
                
                Maintain key details while eliminating repetition. Keep your summary concise.
                """
                
                messages = [HumanMessage(content=final_prompt)]
                response = chat_model.invoke(messages)
                return response.content.strip()
            except Exception as e:
                print(f"Error creating final summary: {e}")
                return combined_summary
        else:
            return combined_summary
            
    except Exception as e:
        print(f"Error in summarization process: {e}")
        return "The text could not be summarized due to an error."

def Process_Audio(file_path):
    """Process audio file: transcribe and summarize."""
    transcript = transcribe_audio(file_path)
    if not transcript:
        return {"success": False, "error": "Transcription failed"}
    
    summary = summarize_text(transcript)
    return {
        "success": True,
        "transcript": transcript,
        "summary": summary
    }