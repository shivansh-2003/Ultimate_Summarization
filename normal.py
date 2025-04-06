import os
from typing import List, Dict, Any, Optional, Union
from dotenv import load_dotenv
import PyPDF2
import docx
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import re
import json
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
import math

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class SummarySettings(BaseModel):
    """Settings for document summary generation."""
    conciseness: str = Field(default="balanced", description="Level of summary conciseness: 'very_concise', 'balanced', or 'detailed'")
    focus_areas: List[str] = Field(default_factory=list, description="Specific areas to focus on in the summary")
    extract_topics: bool = Field(default=True, description="Whether to extract main topics from the document")
    extract_key_points: bool = Field(default=True, description="Whether to extract key points from the document")
    include_statistics: bool = Field(default=False, description="Whether to include basic document statistics")
    summary_length_percentage: Optional[float] = Field(default=None, description="Target summary length as percentage of original")
    
    model_config = {
        "extra": "allow"
    }
    
    @field_validator('conciseness')
    def validate_conciseness(cls, v):
        valid_values = ["very_concise", "balanced", "detailed"]
        if v not in valid_values:
            raise ValueError(f"conciseness must be one of {valid_values}")
        return v
    
    @field_validator('summary_length_percentage')
    def validate_length_percentage(cls, v):
        if v is not None and (v <= 0 or v > 100):
            raise ValueError("summary_length_percentage must be between 1 and 100")
        return v

class DocumentSection(BaseModel):
    """Section of a document with title and content."""
    title: Optional[str] = None
    content: str
    importance_score: Optional[float] = None
    
    model_config = {
        "extra": "allow"
    }

class DocumentStatistics(BaseModel):
    """Basic statistics about a document."""
    word_count: int
    sentence_count: int
    paragraph_count: int
    estimated_reading_time_minutes: float
    
    model_config = {
        "extra": "allow"
    }

class Topic(BaseModel):
    """Topic extracted from a document."""
    name: str
    relevance_score: Optional[float] = None
    related_sentences: List[str] = Field(default_factory=list)
    
    model_config = {
        "extra": "allow"
    }

class KeyPoint(BaseModel):
    """Key point extracted from a document."""
    point: str
    importance_score: Optional[float] = None
    supporting_evidence: List[str] = Field(default_factory=list)
    
    model_config = {
        "extra": "allow"
    }

class SummaryResult(BaseModel):
    """Result of document summary generation."""
    executive_summary: str
    detailed_summary: Optional[str] = None
    topics: List[Topic] = Field(default_factory=list)
    key_points: List[KeyPoint] = Field(default_factory=list)
    statistics: Optional[DocumentStatistics] = None
    processing_time: float
    processed_at: datetime = Field(default_factory=datetime.now)
    
    model_config = {
        "extra": "allow"
    }

class GeneralDocumentSummarizer:
    """
    A general-purpose document summarizer that can process various document types 
    including PDF, Word, and plain text files.
    """
    
    def __init__(self, model_name="gpt-4o-mini", temperature=0.0):
        """Initialize the document summarizer with necessary components."""
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            openai_api_key=OPENAI_API_KEY
        )
        
        # Text splitter tuned for general documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2500,
            chunk_overlap=250,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len
        )
        
        # Document analysis prompt template
        self.document_analysis_prompt = PromptTemplate(
            input_variables=["document_text", "settings"],
            template="""
            You are an expert document analyst capable of identifying key topics, extracting important points, 
            and creating concise summaries that preserve the core meaning of documents.
            
            DOCUMENT TEXT:
            {document_text}
            
            SETTINGS:
            {settings}
            
            Please analyze this document and provide a structured JSON response that includes:
            
            1. An executive summary that captures the essential information
            2. A list of main topics discussed in the document
            3. Key points from the document
            4. Any statistics mentioned
            
            The summary should be {settings[conciseness]}, focusing on the most important information.
            
            Format your response as a valid JSON object with the following structure:
            
            ```json
            {{
                "executive_summary": "Concise overview of the entire document",
                "topics": [
                    {{
                        "name": "First topic name",
                        "relevance_score": 0.95,
                        "related_sentences": ["Related sentence 1", "Related sentence 2"]
                    }},
                    ...
                ],
                "key_points": [
                    {{
                        "point": "First key point",
                        "importance_score": 0.92,
                        "supporting_evidence": ["Evidence 1", "Evidence 2"]
                    }},
                    ...
                ]
            }}
            ```
            
            Focus on extracting factual information and the main arguments or conclusions.
            """
        )
        
        # Sectional summary prompt
        self.sectional_summary_prompt = PromptTemplate(
            input_variables=["section", "settings"],
            template="""
            You are an expert document analyst. Summarize the following document section based on the provided settings.
            
            SECTION:
            {section}
            
            SETTINGS:
            {settings}
            
            Create a concise summary of this section that preserves the main ideas and important details.
            The summary should be {settings[conciseness]}.
            """
        )
        
        # Combined summary prompt
        self.combined_summary_prompt = PromptTemplate(
            input_variables=["section_summaries", "settings", "document_statistics"],
            template="""
            You are an expert document analyst. Based on the summaries of individual sections,
            create a comprehensive summary of the entire document.
            
            SECTION SUMMARIES:
            {section_summaries}
            
            DOCUMENT STATISTICS:
            {document_statistics}
            
            SETTINGS:
            {settings}
            
            Create two summaries:
            1. An executive summary (1-2 paragraphs) that provides a high-level overview
            2. A detailed summary that integrates the key information from all sections
            
            Both summaries should be {settings[conciseness]} and should accurately represent the original document's
            content, tone, and conclusions.
            """
        )
    
    def load_document(self, file_path: str) -> str:
        """Load text from various document formats (PDF, DOCX, TXT)."""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            return self._load_pdf(file_path)
        elif file_extension == '.docx':
            return self._load_docx(file_path)
        elif file_extension == '.txt':
            return self._load_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    
    def _load_pdf(self, pdf_path: str) -> str:
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
    
    def _load_docx(self, docx_path: str) -> str:
        """Extract text from a Word document."""
        print(f"Loading Word document from {docx_path}...")
        
        doc = docx.Document(docx_path)
        text = "\n\n".join([paragraph.text for paragraph in doc.paragraphs])
        
        print(f"Extracted {len(text)} characters from Word document.")
        return text
    
    def _load_txt(self, txt_path: str) -> str:
        """Load text from a TXT file."""
        print(f"Loading text file from {txt_path}...")
        
        with open(txt_path, 'r', encoding='utf-8') as file:
            text = file.read()
        
        print(f"Extracted {len(text)} characters from text file.")
        return text
    
    def compute_document_statistics(self, text: str) -> DocumentStatistics:
        """Compute basic document statistics."""
        # Count words
        words = re.findall(r'\b\w+\b', text)
        word_count = len(words)
        
        # Count sentences using regex-based approach
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        sentence_count = len(sentences)
        
        # Count paragraphs
        paragraphs = text.split('\n\n')
        paragraph_count = len([p for p in paragraphs if p.strip()])  # Count non-empty paragraphs
        
        # Estimate reading time (assuming average reading speed of 200 words per minute)
        estimated_reading_time_minutes = word_count / 200.0
        
        return DocumentStatistics(
            word_count=word_count,
            sentence_count=sentence_count,
            paragraph_count=paragraph_count,
            estimated_reading_time_minutes=estimated_reading_time_minutes
        )
    
    def _split_into_sections(self, text: str) -> List[DocumentSection]:
        """Split document into sections based on structure."""
        # First, try to identify section headers
        lines = text.split('\n')
        sections = []
        current_section_title = None
        current_section_content = []
        
        # Simple heuristic for section headers: short lines, often uppercase or with numbers
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this line looks like a header
            is_header = (
                (len(line) < 60 and (line.isupper() or line.istitle())) or
                re.match(r'^(\d+\.|\(?\d+\)?)\s+[A-Z]', line) or  # Numbered section
                re.match(r'^[A-Z][a-zA-Z\s]{0,30}:?$', line)  # Title case short line
            )
            
            if is_header:
                # Save the previous section if it exists
                if current_section_content:
                    section_text = '\n'.join(current_section_content).strip()
                    if section_text:
                        sections.append(DocumentSection(
                            title=current_section_title,
                            content=section_text
                        ))
                
                # Start a new section
                current_section_title = line
                current_section_content = []
            else:
                current_section_content.append(line)
        
        # Add the last section
        if current_section_content:
            section_text = '\n'.join(current_section_content).strip()
            if section_text:
                sections.append(DocumentSection(
                    title=current_section_title,
                    content=section_text
                ))
        
        # If no clear sections were found, fall back to chunking
        if not sections or (len(sections) == 1 and not sections[0].title):
            chunks = self.text_splitter.split_text(text)
            sections = [DocumentSection(content=chunk) for chunk in chunks]
        
        return sections
    
    def _score_section_importance(self, sections: List[DocumentSection]) -> List[DocumentSection]:
        """Score sections by importance using heuristics."""
        # Simple heuristic: length and position
        total_content = sum(len(section.content) for section in sections)
        
        for i, section in enumerate(sections):
            # Position factor (beginning and end often more important)
            position_factor = 1.0
            if i < len(sections) * 0.2:  # First 20% of sections
                position_factor = 1.2
            elif i > len(sections) * 0.8:  # Last 20% of sections
                position_factor = 1.1
            
            # Length factor (longer sections may contain more information)
            length_factor = min(1.0, len(section.content) / (total_content / len(sections) * 2))
            
            # Keyword factor (presence of important words)
            important_keywords = ["conclusion", "summary", "result", "finding", "important", 
                                 "significant", "key", "critical", "essential", "crucial"]
            keyword_factor = 1.0
            section_lower = section.content.lower()
            if section.title:
                section_lower += " " + section.title.lower()
            
            keyword_matches = sum(1 for keyword in important_keywords if keyword in section_lower)
            keyword_factor += 0.1 * keyword_matches
            
            # Combined score
            section.importance_score = position_factor * length_factor * keyword_factor
        
        return sections
    
    def summarize_document(self, document_path: str, settings: Optional[Dict[str, Any]] = None) -> SummaryResult:
        """Generate a summary of the document with customizable settings."""
        start_time = datetime.now()
        
        # Use default settings if none provided
        if settings is None:
            settings = {}
        
        # Convert settings to Pydantic model for validation
        summary_settings = SummarySettings(**settings)
        
        # Load document
        document_text = self.load_document(document_path)
        
        # Calculate statistics
        statistics = self.compute_document_statistics(document_text)
        
        # Prepare settings for the prompt
        settings_dict = summary_settings.model_dump()  # Ensure this is a dictionary
        
        # For shorter documents, use a single-pass approach
        if statistics.word_count < 3000:
            result = self._summarize_short_document(document_text, settings_dict, statistics)
        else:
            # For longer documents, use a multi-stage approach
            result = self._summarize_long_document(document_text, settings_dict, statistics)
        
        # Set processing time
        result.processing_time = (datetime.now() - start_time).total_seconds()
        
        return result
    
    def _summarize_short_document(self, document_text: str, settings: Dict[str, Any], 
                                statistics: DocumentStatistics) -> SummaryResult:
        """Summarize a short document using a single-pass approach."""
        print("Using single-pass approach for short document...")
        
        # Generate analysis with the LLM
        prompt = self.document_analysis_prompt.format(
            document_text=document_text,
            settings=settings  # Use the dictionary directly
        )
        
        response = self.llm.invoke(prompt).content
        
        # Extract JSON from response
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                analysis_str = response[json_start:json_end]
                analysis = json.loads(analysis_str)
                
                # Create SummaryResult
                result = SummaryResult(
                    executive_summary=analysis.get("executive_summary", ""),
                    detailed_summary=analysis.get("detailed_summary", None),
                    topics=[Topic(**topic) for topic in analysis.get("topics", [])],
                    key_points=[KeyPoint(**point) for point in analysis.get("key_points", [])],
                    statistics=statistics,
                    processing_time=0  # Will be set later
                )
                
                return result
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
        
        # Fallback if parsing fails
        return SummaryResult(
            executive_summary="Failed to generate summary.",
            statistics=statistics,
            processing_time=0  # Will be set later
        )
    
    def _summarize_long_document(self, document_text: str, settings: Dict[str, Any],
                               statistics: DocumentStatistics) -> SummaryResult:
        """Summarize a long document using a multi-stage approach."""
        print("Using multi-stage approach for long document...")
        
        # Step 1: Split document into sections
        sections = self._split_into_sections(document_text)
        print(f"Document split into {len(sections)} sections.")
        
        # Step 2: Score and possibly filter sections
        sections = self._score_section_importance(sections)
        
        # Sort sections by importance score
        sections.sort(key=lambda x: x.importance_score or 0, reverse=True)
        
        # If summary length percentage is specified, use only the most important sections
        if settings.get('summary_length_percentage') is not None:
            section_limit = max(1, math.ceil(len(sections) * settings['summary_length_percentage'] / 100))
            sections = sections[:section_limit]
            print(f"Using top {section_limit} sections for summary.")
        
        # Step 3: Summarize each section
        section_summaries = []
        
        for i, section in enumerate(sections):
            print(f"Summarizing section {i+1}/{len(sections)}...")
            
            prompt = self.sectional_summary_prompt.format(
                section=section.content,
                settings=settings
            )
            
            summary = self.llm.invoke(prompt).content
            section_summaries.append(f"Section: {section.title or f'Section {i+1}'}\n{summary}")
        
        # Step 4: Combine section summaries into a single document summary
        combined_summaries = "\n\n".join(section_summaries)
        statistics_str = f"Word count: {statistics.word_count}, Sentence count: {statistics.sentence_count}, " \
                         f"Paragraph count: {statistics.paragraph_count}, " \
                         f"Reading time: {statistics.estimated_reading_time_minutes:.1f} minutes"
        
        prompt = self.combined_summary_prompt.format(
            section_summaries=combined_summaries,
            document_statistics=statistics_str,
            settings=settings
        )
        
        combined_response = self.llm.invoke(prompt).content
        
        # Step 5: Extract topics and key points
        topics_prompt = PromptTemplate(
            input_variables=["document_text"],
            template="""
            Extract the main topics from this document. For each topic, provide a relevance score 
            and 1-2 related sentences from the document. Format as JSON:
            
            ```json
            [
                {
                    "name": "Topic name",
                    "relevance_score": 0.95,
                    "related_sentences": ["Related sentence 1", "Related sentence 2"]
                },
                ...
            ]
            ```
            
            DOCUMENT:
            {document_text}
            """
        ).format(document_text=combined_summaries)
        
        topics_response = self.llm.invoke(topics_prompt).content
        
        key_points_prompt = PromptTemplate(
            input_variables=["document_text"],
            template="""
            Extract the key points from this document. For each point, provide an importance score 
            and supporting evidence. Format as JSON:
            
            ```json
            [
                {
                    "point": "Key point statement",
                    "importance_score": 0.92,
                    "supporting_evidence": ["Evidence 1", "Evidence 2"]
                },
                ...
            ]
            ```
            
            DOCUMENT:
            {document_text}
            """
        ).format(document_text=combined_summaries)
        
        key_points_response = self.llm.invoke(key_points_prompt).content
        
        # Parse topics and key points
        topics = []
        try:
            json_start = topics_response.find('[')
            json_end = topics_response.rfind(']') + 1
            if json_start >= 0 and json_end > json_start:
                topics_json = topics_response[json_start:json_end]
                topics_data = json.loads(topics_json)
                topics = [Topic(**topic) for topic in topics_data]
        except Exception as e:
            print(f"Error parsing topics: {e}")
        
        key_points = []
        try:
            json_start = key_points_response.find('[')
            json_end = key_points_response.rfind(']') + 1
            if json_start >= 0 and json_end > json_start:
                key_points_json = key_points_response[json_start:json_end]
                key_points_data = json.loads(key_points_json)
                key_points = [KeyPoint(**point) for point in key_points_data]
        except Exception as e:
            print(f"Error parsing key points: {e}")
        
        # Extract executive and detailed summaries from combined response
        parts = combined_response.split('\n\n')
        executive_summary = parts[0] if parts else combined_response
        detailed_summary = '\n\n'.join(parts[1:]) if len(parts) > 1 else None
        
        # Create the final result
        result = SummaryResult(
            executive_summary=executive_summary,
            detailed_summary=detailed_summary,
            topics=topics,
            key_points=key_points,
            statistics=statistics,
            processing_time=0  # Will be set later
        )
        
        return result


if __name__ == "__main__":
    # Example usage
    summarizer = GeneralDocumentSummarizer()
    
    # Define custom settings
    settings = {
        "conciseness": "very_concise",
        "extract_topics": True,
        "extract_key_points": True,
        "include_statistics": True
    }
    
    # Process a document
    result = summarizer.summarize_document("/Users/shivanshmahajan/Desktop/Ultimate_Summarization/file/temp.pdf", settings)
    
    print("\n" + "="*50)
    print("EXECUTIVE SUMMARY")
    print("="*50)
    print(result.executive_summary)
    
    if result.detailed_summary:
        print("\n" + "="*50)
        print("DETAILED SUMMARY")
        print("="*50)
        print(result.detailed_summary)
    
    print("\n" + "="*50)
    print("MAIN TOPICS")
    print("="*50)
    for topic in result.topics:
        print(f"- {topic.name} (Relevance: {topic.relevance_score})")
    
    print("\n" + "="*50)
    print("KEY POINTS")
    print("="*50)
    for point in result.key_points:
        print(f"- {point.point}")
    
    print("\n" + "="*50)
    print("DOCUMENT STATISTICS")
    print("="*50)
    print(f"Word count: {result.statistics.word_count}")
    print(f"Sentence count: {result.statistics.sentence_count}")
    print(f"Paragraph count: {result.statistics.paragraph_count}")
    print(f"Estimated reading time: {result.statistics.estimated_reading_time_minutes:.1f} minutes")
    
    print("\n" + "="*50)
    print(f"Processing time: {result.processing_time:.2f} seconds")