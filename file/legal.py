import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
import requests
import json
from datetime import datetime

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

class LegalDocumentSummarizer:
    """
    A simplified legal document summarizer that uses LangChain and OpenAI
    without vector databases for easier deployment.
    """
    
    def __init__(self, model_name="gpt-4", temperature=0.0):
        """Initialize the legal document summarizer with necessary components."""
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            openai_api_key=OPENAI_API_KEY
        )
        
        # Text splitter tuned for legal documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=4000,
            chunk_overlap=400,
            separators=["\n\n", "\n", ".", " ", ""],
            length_function=len
        )
        
        # Legal-specific prompt templates
        self.summary_prompt = PromptTemplate(
            input_variables=["text_chunks", "document_type", "question"],
            template="""
            You are a highly skilled legal expert tasked with summarizing legal documents.
            
            DOCUMENT TYPE: {document_type}
            
            DOCUMENT SECTIONS:
            {text_chunks}
            
            {question}
            
            Provide a comprehensive yet concise summary that:
            1. Identifies the key parties involved
            2. Extracts main legal provisions, obligations, and rights
            3. Highlights important dates, deadlines, and durations
            4. Notes any conditional clauses or exceptions
            5. Flags potential risks or areas of concern
            
            Use precise legal terminology where appropriate, but explain complex legal concepts
            in plain language. Structure your response logically, following the organization of
            the original document where beneficial.
            """
        )
    
    def load_pdf(self, pdf_path: str) -> str:
        """Extract text from a PDF document."""
        print(f"Loading PDF from {pdf_path}...")
        
        text = ""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text() + "\n\n"
        
        print(f"Extracted {len(text)} characters from PDF.")
        return text
    
    def detect_document_type(self, text: str) -> str:
        """Determine the type of legal document based on content analysis."""
        # We'll use the LLM to identify document type
        prompt = """
        Analyze the following legal text and identify the document type (e.g., Contract, NDA, 
        Employment Agreement, Terms of Service, Privacy Policy, Patent Application, Court Filing, etc.).
        Return ONLY the document type, no other text.
        
        TEXT:
        {}
        """.format(text[:5000])  # Use the first 5000 chars to identify doc type
        
        response = self.llm.predict(prompt)
        print(f"Detected document type: {response}")
        return response.strip()
    
    def chunk_document(self, text: str) -> List[str]:
        """Split document into manageable chunks."""
        print("Splitting text into manageable chunks...")
        chunks = self.text_splitter.split_text(text)
        print(f"Created {len(chunks)} text chunks.")
        return chunks
    
    def search_legal_context(self, query: str, num_results: int = 3) -> List[Dict]:
        """Use Tavily API to search for relevant legal context."""
        if not TAVILY_API_KEY:
            print("Tavily API key not provided. Skipping external context search.")
            return []
            
        print(f"Searching for external legal context about: {query}")
        url = "https://api.tavily.com/search"
        payload = {
            "api_key": TAVILY_API_KEY,
            "query": f"legal information about {query}",
            "search_depth": "advanced",
            "include_domains": ["law.cornell.edu", "justia.com", "findlaw.com", "legal-dictionary.thefreedictionary.com"],
            "max_results": num_results
        }
        
        try:
            response = requests.post(url, json=payload)
            result = response.json()
            if "results" in result:
                print(f"Found {len(result['results'])} external legal resources.")
                return result["results"]
        except Exception as e:
            print(f"Error fetching external legal context: {e}")
        
        return []
    
    def summarize_chunks(self, chunks: List[str], document_type: str, question: str) -> str:
        """Summarize document chunks without using vector storage."""
        # For longer documents, we'll use a map-reduce approach
        if len(chunks) > 5:
            print("Document is long, using map-reduce approach...")
            # First, get summaries of each chunk
            chunk_summaries = []
            for i, chunk in enumerate(chunks):
                print(f"Processing chunk {i+1}/{len(chunks)}...")
                chunk_prompt = f"""
                You are a legal expert. Summarize the key legal points from this section of a {document_type}:
                
                {chunk}
                
                Provide a concise summary of the main legal elements in this section.
                """
                summary = self.llm.predict(chunk_prompt)
                chunk_summaries.append(summary)
            
            # Then combine the summaries
            combined_summaries = "\n\n".join(chunk_summaries)
            final_prompt = f"""
            You are a senior legal expert. Based on these summaries of different sections of a {document_type},
            create a comprehensive summary of the entire document.
            
            SECTION SUMMARIES:
            {combined_summaries}
            
            {question}
            
            Provide a well-structured summary that integrates all the key legal aspects from these sections.
            Include information about parties, obligations, rights, deadlines, conditions, and potential risks.
            Use clear, precise language, with legal terminology where appropriate.
            """
            return self.llm.predict(final_prompt)
        else:
            # For shorter documents, process all chunks together
            print("Document is shorter, processing all chunks together...")
            full_text = "\n\n".join(chunks)
            prompt = self.summary_prompt.format(
                text_chunks=full_text,
                document_type=document_type,
                question=question
            )
            return self.llm.predict(prompt)
    
    def enhance_with_legal_context(self, summary: str, document_type: str) -> str:
        """Enhance the summary with relevant legal context and explanations."""
        # Extract key legal terms/concepts to research
        prompt = """
        Identify the 3 most important legal concepts or terms from this legal document summary
        that would benefit from additional explanation or context. Return ONLY the terms/concepts
        separated by commas, no other text.
        
        SUMMARY:
        {}
        """.format(summary)
        
        key_concepts = self.llm.predict(prompt).strip()
        print(f"Key legal concepts identified: {key_concepts}")
        
        # Search for additional context
        external_context = []
        for concept in key_concepts.split(","):
            search_results = self.search_legal_context(concept.strip())
            if search_results:
                external_context.append({
                    "concept": concept.strip(),
                    "sources": search_results
                })
        
        # Enhance summary with additional context
        if external_context:
            context_str = json.dumps(external_context, indent=2)
            enhancement_prompt = """
            Enhance this legal document summary with additional context and explanations 
            for key legal concepts. Incorporate the external information where relevant, but
            keep the focus on the original document. Make the additional context helpful for
            non-legal professionals.
            
            DOCUMENT TYPE: {}
            
            CURRENT SUMMARY:
            {}
            
            ADDITIONAL LEGAL CONTEXT:
            {}
            
            Provide an enhanced summary that incorporates this additional context to make
            the legal document more understandable. Don't explicitly mention that you're adding
            external context - just seamlessly integrate the information.
            """.format(document_type, summary, context_str)
            
            enhanced_summary = self.llm.predict(enhancement_prompt)
            print("Summary enhanced with external legal context.")
            return enhanced_summary
        
        return summary
    
    def generate_summary(self, pdf_path: str, custom_question: Optional[str] = None) -> Dict[str, Any]:
        """Generate a comprehensive legal document summary."""
        start_time = datetime.now()
        
        # Load document
        text = self.load_pdf(pdf_path)
        document_type = self.detect_document_type(text)
        
        # Process document in chunks
        chunks = self.chunk_document(text)
        
        # Generate summary
        question = custom_question if custom_question else "Provide a comprehensive summary of this legal document."
        summary = self.summarize_chunks(chunks, document_type, question)
        
        # Enhance with legal context
        enhanced_summary = self.enhance_with_legal_context(summary, document_type)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "document_type": document_type,
            "summary": enhanced_summary,
            "processing_time": processing_time
        }


if __name__ == "__main__":
    # Example usage
    summarizer = LegalDocumentSummarizer()
    result = summarizer.generate_summary("/Users/shivanshmahajan/Desktop/Ultimate_Summarization/file/SampleContract-Shuttle.pdf")
    
    print("\n" + "="*50)
    print(f"DOCUMENT TYPE: {result['document_type']}")
    print("="*50)
    print(result['summary'])
    print("\n" + "="*50)
    print(f"Processing time: {result['processing_time']:.2f} seconds")