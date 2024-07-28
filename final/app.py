import streamlit as st
from transformers import pipeline
import assemblyai as aai
import os
import fitz  # PyMuPDF
import openai
from langchain import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains import MapReduceDocumentsChain, RefineDocumentsChain
from langchain.schema import Document
import validators
from langchain_groq import ChatGroq
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import YoutubeLoader, UnstructuredURLLoader

# Set your Groq API key here
GROQ_API_KEY = "your grog api key"

# Set your OpenAI API key
openai.api_key = 'your open ai key'
# Set AssemblyAI API key
aai.settings.api_key = "your assembly ai key"

# Set Streamlit page configuration
st.set_page_config(page_title="LangChain: Summarize Text From YT or Website", page_icon="🦜")

# Initialize the summarizer pipeline
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

# Sidebar navigation
page = st.sidebar.selectbox("Navigation", ["Website", "Speech", "Document"])

if page == "Website":
    st.title("🦜 LangChain: Summarize Text From YT or Website")
    st.subheader('Summarize URL')

    # Get the Groq API Key and URL (YT or website) to be summarized
    with st.sidebar:
        groq_api_key = st.text_input("Groq API Key", value="", type="password")

    generic_url = st.text_input("URL", label_visibility="collapsed")

    # Gemma Model Using Groq API
    llm = ChatGroq(model="Gemma-7b-It", groq_api_key=groq_api_key)

    prompt_template = """
    Provide a summary of the following content in 300 words:
    Content: {text}
    """
    prompt = PromptTemplate(template=prompt_template, input_variables=["text"])

    if st.button("Summarize the Content from YT or Website"):
        # Validate all the inputs
        if not groq_api_key.strip() or not generic_url.strip():
            st.error("Please provide the information to get started")
        elif not validators.url(generic_url):
            st.error("Please enter a valid URL. It can be a YT video URL or website URL")
        else:
            try:
                with st.spinner("Waiting..."):
                    # Loading the website or YT video data
                    if "youtube.com" in generic_url:
                        loader = YoutubeLoader.from_youtube_url(generic_url, add_video_info=True)
                    else:
                        loader = UnstructuredURLLoader(
                            urls=[generic_url],
                            ssl_verify=False,
                            headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"}
                        )
                    docs = loader.load()

                    # Chain for Summarization
                    chain = load_summarize_chain(llm, chain_type="stuff", prompt=prompt)
                    output_summary = chain.run(docs)

                    st.success(output_summary)
            except Exception as e:
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

else:
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
    st.title("Document Summarization App")

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