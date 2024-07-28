import streamlit as st
import fitz  # PyMuPDF
import openai
from langchain import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains import MapReduceDocumentsChain, RefineDocumentsChain
from langchain.schema import Document
import os

# Set your OpenAI API key
#openai.api_key = 'your openai key'

# Function to read PDF file
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