import os
import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
# Set OpenAI API Key
os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"

# Title of the Streamlit app
st.title("Chat with Your Custom Document 📄🤖")

# Greet user in the chat-like message
with st.chat_message("user"):
    st.write("Hello 👋! Upload a document, and I’ll provide answers based on its content.")

# Function to process and split the document
@st.cache_data
def load_and_process_document(file_path):
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(documents)
    return chunks

# Updated create_vector_store function with persistence
@st.cache_data(hash_funcs={list: lambda _: None})
def create_vector_store(chunks):
    embeddings = OpenAIEmbeddings()
    # Set persistent storage location for ChromaDB
    db_directory = "./chroma_db"
    if not os.path.exists(db_directory):
        os.makedirs(db_directory)
    
    # Initialize ChromaDB with persistent storage
    vector_store = Chroma.from_documents(
        documents=chunks, 
        embedding=embeddings, 
        persist_directory=db_directory
    )
    return vector_store

# Upload document
uploaded_file = st.file_uploader("Upload your document (PDF)", type=["pdf"])

if uploaded_file:
    # Save uploaded file temporarily
    with open("uploaded_document.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success("Document uploaded successfully!")

    # Load and process the document
    with st.spinner("Processing your document..."):
        chunks = load_and_process_document("uploaded_document.pdf")
        vector_store = create_vector_store(chunks)
    st.success("Document is ready for questions!")

    # Build the RetrievalQA chain
    llm = OpenAI(model="gpt-4", temperature=0)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vector_store.as_retriever(),
        chain_type="stuff"
    )

    # User Query
    st.subheader("Ask a question based on the document:")
    query = st.text_input("Enter your question here:")
    
    # Display answer when the user clicks the button
    if st.button("Get Answer"):
        if query:
            with st.spinner("Finding the answer..."):
                response = qa_chain.run(query)
            with st.chat_message("assistant"):
                st.write(response)
        else:
            st.warning("Please enter a question to get an answer.")
