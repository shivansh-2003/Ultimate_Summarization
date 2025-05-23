import streamlit as st
from transformers import pipeline
import assemblyai as aai
import os
import fitz  # PyMuPDF
import openai
from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.duckduckgo import DuckDuckGo
from google.generativeai import upload_file,get_file
import google.generativeai as genai
from langchain import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains import MapReduceDocumentsChain, RefineDocumentsChain
from langchain.schema import Document
import validators
from langchain_groq import ChatGroq
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import YoutubeLoader, UnstructuredURLLoader
import time
from pathlib import Path
import tempfile
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Access the API keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")

# Configure the services with the API keys
genai.configure(api_key=GOOGLE_API_KEY)
openai.api_key = OPENAI_API_KEY
aai.settings.api_key = ASSEMBLYAI_API_KEY

# Set Streamlit page configuration
st.set_page_config(page_title="LangChain: Summarize Text From YT or Website", page_icon="🦜")

# Initialize the summarizer pipeline
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

# Sidebar navigation
page = st.sidebar.selectbox("Navigation", ["Website", "Speech", "Document", "Video"])




if page == "Website":
    st.title("Website URL Summarization")
    st.image("/Users/shivanshmahajan/Desktop/Ultimate_Summarization/Images/web3.jpg")
    st.subheader('Summarize URL')

    # Input field for URL
    generic_url = st.text_input("Enter URL (YouTube or Website)", help="Paste the URL of the YouTube video or website to summarize")

    # Summary length option on the main page
    summary_length = st.selectbox("Summary Length", options=["Short", "Medium", "Long"], index=1, help="Select the length of the summary")

    # Set summary length based on user selection
    summary_word_count = {
        "Short": 100,
        "Medium": 300,
        "Long": 500
    }[summary_length]

    # Gemma Model using Groq API
    llm = ChatGroq(model="gemma2-9b-it", groq_api_key=GROQ_API_KEY)

    # Prompt template for summarization
    prompt_template = f"""
    Provide a summary of the following content in {summary_word_count} words:
    Content: {{text}}
    """
    prompt = PromptTemplate(template=prompt_template, input_variables=["text"])

    # Button to trigger summarization
    if st.button("Summarize the Content from YT or Website"):
        # Validate the inputs
        if not generic_url.strip():
            st.error("Please provide a URL to get started")
        elif not validators.url(generic_url):
            st.error("Please enter a valid URL. It can be a YouTube video URL or a website URL")
        else:
            try:
                with st.spinner("Fetching and summarizing content..."):
                    # Load the content from the URL
                    if "youtube.com" in generic_url or "youtu.be" in generic_url:
                        loader = YoutubeLoader.from_youtube_url(generic_url, add_video_info=True)
                        docs = loader.load()
                        # Display YouTube video info
                        video_info = docs[0].metadata
                        st.info(f"Title: {video_info['title']}\nChannel: {video_info['channel']}\nPublished At: {video_info['publish_date']}")
                    else:
                        loader = UnstructuredURLLoader(
                            urls=[generic_url],
                            ssl_verify=False,
                            headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"}
                        )
                        docs = loader.load()

                    # Chain for summarization
                    chain = load_summarize_chain(llm, chain_type="stuff", prompt=prompt)
                    output_summary = chain.run(docs)

                    st.success("Summary:")
                    st.write(output_summary)
            except Exception as e:
                st.error("An error occurred during summarization")
                st.exception(f"Exception: {e}")
elif page == "Speech":
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

    st.title("Audio Summarization")
    st.image("//Users/shivanshmahajan/Desktop/Ultimate_Summarization/Images/audio.jpg")

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

elif page =="Document":
    def read_pdf(file):
       text = ""
       pdf_document = fitz.open(stream=file.read(), filetype="pdf")
       for page_num in range(pdf_document.page_count):
          page = pdf_document.load_page(page_num)
          text += page.get_text()
       return text

# Function to read TXT file
    def read_txt(file):
       return file.read().decode('utf-8')

# Define the chat model completion function
    def chat_completion(messages):
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # or "gpt-4"
        messages=messages
        )
        return response.choices[0].message['content'].strip()

# Define the Stuff prompt template
    stuff_prompt_template = """Write a concise summary of the following:
    "{text}"
    CONCISE SUMMARY:"""
    stuff_prompt = PromptTemplate.from_template(stuff_prompt_template)

# Define the Stuff chain
    def summarize_stuff(text):
        messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": stuff_prompt.format(text=text)}
        ]
        return chat_completion(messages)

# Define the Map-Reduce prompt templates
    map_template = """The following is a set of documents:
    {docs}
    Please provide a summary for each document."""
    map_prompt = PromptTemplate.from_template(map_template)

    reduce_template = """Here are the summaries of multiple documents:
    {summaries}
    Please provide a concise summary of all these summaries."""
    reduce_prompt = PromptTemplate.from_template(reduce_template)

# Define the Map-Reduce chain
    def summarize_map_reduce(docs):
       summaries = [summarize_stuff(doc) for doc in docs]
       final_summary = summarize_stuff(" ".join(summaries))
       return final_summary

# Define the Refine prompt template
    refine_template = """We are summarizing a collection of documents. Here is the current summary:
    {summary}
    Here is the next document:
    {document}
    Update the summary with information from the new document."""
    refine_prompt = PromptTemplate.from_template(refine_template)

# Define the Refine chain
    def summarize_refine(docs):
       summary = ""
       for doc in docs:
            messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": refine_prompt.format(summary=summary, document=doc)}
            ]
       summary = chat_completion(messages)
       return summary

# Streamlit app layout
    st.title("Document Summarization")
    st.image("/Users/shivanshmahajan/Desktop/Ultimate_Summarization/Images/doc.jpg")

# File upload
    uploaded_file = st.file_uploader("Upload a TXT or PDF file", type=["txt", "pdf"])

    if uploaded_file is not None:
       if uploaded_file.type == "application/pdf":
        # Read the content of the PDF file
         text = read_pdf(uploaded_file)
       elif uploaded_file.type == "text/plain":
        # Read the content of the TXT file
         text = read_txt(uploaded_file)
    
       st.subheader("Original Text")
       st.text_area("Original Text", text, height=300)
    
    # Choose summarization method
       method = st.selectbox("Choose Summarization Method", ["Stuff", "Map-Reduce", "Refine"])
    
       if st.button("Summarize"):
        # Create a list of Document objects
          documents = [text]  # Assuming text is already a list of documents for Map-Reduce and Refine
        
          if method == "Stuff":
            # Summarize documents using Stuff method
             result = summarize_stuff(text)
          elif method == "Map-Reduce":
            # Summarize documents using Map-Reduce method
             result = summarize_map_reduce(documents)
          elif method == "Refine":
            # Summarize documents using Refine method
            result = summarize_refine(documents)
        
          st.subheader("Summary")
          st.text_area("Summary", result, height=200)

else:
    @st.cache_resource
    def initialize_agent():
       return Agent(
        name="Video AI Summarizer",
        model=Gemini(id="gemini-2.0-flash-exp"),
        tools=[DuckDuckGo()],
        markdown=True,
    )

## Initialize the agent
    multimodal_Agent=initialize_agent()   # This is the "Video" page
    st.title("Video Analysis")

    # File uploader for video
    video_file = st.file_uploader(
        "Upload a video file", type=['mp4', 'mov', 'avi'], help="Upload a video for AI analysis"
    )

    if video_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
            temp_video.write(video_file.read())
            video_path = temp_video.name

        st.video(video_path, format="video/mp4", start_time=0)

        user_query = st.text_area(
            "What insights are you seeking from the video?",
            placeholder="Ask anything about the video content. The AI agent will analyze and gather additional context if needed.",
            help="Provide specific questions or insights you want from the video."
        )

        if st.button("🔍 Analyze Video", key="analyze_video_button"):
            if not user_query:
                st.warning("Please enter a question or insight to analyze the video.")
            else:
                try:
                    with st.spinner("Processing video and gathering insights..."):
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
                            {user_query}

                            Provide a detailed, user-friendly, and actionable response.
                            """
                        )

                        # AI agent processing
                        response = multimodal_Agent.run(analysis_prompt, videos=[processed_video])

                    # Display the result
                    st.subheader("Analysis Result")
                    st.markdown(response.content)

                except Exception as error:
                    st.error(f"An error occurred during analysis: {error}")
                finally:
                    # Clean up temporary video file
                    Path(video_path).unlink(missing_ok=True)
    else:
        st.info("Upload a video file to begin analysis.")

    # Customize text area height
    st.markdown(
        """
        <style>
        .stTextArea textarea {
            height: 100px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    