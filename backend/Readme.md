# Ultimate Summarization API - Backend Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [System Overview](#system-overview)
3. [Installation and Setup](#installation-and-setup)
4. [API Endpoints](#api-endpoints)
5. [Core Components](#core-components)
   - [API Module (`api.py`)](#api-module-apipy)
   - [Legal Document Processing (`legal.py`)](#legal-document-processing-legalpy)
   - [General Document Processing (`normal.py`)](#general-document-processing-normalpy)
   - [Resume Processing (`resume.py` & `resume_models.py`)](#resume-processing-resumepy--resume_modelspy)
   - [Speech/Audio Processing (`speech.py`)](#speechaudio-processing-speechpy)
   - [Video Processing (`video_agent.py`)](#video-processing-video_agentpy)
   - [Website Processing (`website.py`)](#website-processing-websitepy)
6. [Development Guidelines](#development-guidelines)
7. [Environment Variables](#environment-variables)
8. [Troubleshooting](#troubleshooting)
9. [Future Development](#future-development)

## Introduction

The Ultimate Summarization API is a comprehensive backend solution for processing and summarizing various types of content, including:

- Legal documents (PDF)
- General documents (PDF, DOCX, TXT)
- Resumes (PDF)
- Audio files
- Video content (both YouTube and uploaded videos)
- Website content

This API leverages state-of-the-art language models and specialized processing techniques to extract meaningful insights from different content types. The system is built with modularity in mind, allowing for easy extension and maintenance.

## System Overview

The system architecture follows a modular design pattern where each type of content (legal documents, general documents, resumes, audio, video, and websites) has its own dedicated processing module. The central FastAPI application (`api.py`) serves as the orchestrator, directing requests to the appropriate processing modules.

Key features of the architecture include:
- **FastAPI framework** for efficient API routing and request handling
- **Langchain** integration for advanced language processing capabilities
- **Multiple AI models** (OpenAI, Groq, Google Gemini) providing specialized processing for different content types
- **Pydantic models** for robust data validation and structured responses
- **Asynchronous processing** where appropriate to enhance performance
- **Background tasks** for resource cleanup and management
- **Temporary file handling** for secure processing of uploaded content

## Installation and Setup

### Prerequisites
- Python 3.8+
- Required API keys (OpenAI, Google, Tavily, Groq)
- Virtual environment (recommended)

### Installation Steps

1. Clone the repository:
```bash
git clone [repository-url]
cd ultimate-summarization-api
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```
OPENAI_API_KEY=your_openai_api_key
GOOGLE_API_KEY=your_google_api_key
TAVILY_API_KEY=your_tavily_api_key
GROQ_API_KEY=your_groq_api_key
```

5. Start the server:
```bash
uvicorn backend.api:app --reload
```

The API will be available at `http://localhost:8000`.

## API Endpoints

The API provides the following endpoints:

### Legal Document Processing
- **POST** `/api/legal/summarize`: Summarizes a legal document (PDF format)
  - Parameters: `file` (PDF), `custom_question` (optional)

### General Document Processing
- **POST** `/api/general/summarize`: Summarizes a general document (PDF, DOCX, TXT)
  - Parameters: `file`, `conciseness`, `extract_topics`, `extract_key_points`, `include_statistics`, `summary_length_percentage`

### Resume Analysis
- **POST** `/api/resume/analyze`: Analyzes a resume with optional job description comparison
  - Parameters: `file` (PDF), `job_description` (optional)

### Audio Processing
- **POST** `/api/process-audio`: Transcribes and summarizes audio files
  - Parameters: `file` (audio file)

### Video Processing
- **POST** `/api/summarize/youtube`: Summarizes YouTube videos
  - Parameters: `url`, `query`
- **POST** `/summarize/video`: Summarizes uploaded videos
  - Parameters: `file`, `query`

### Website Processing
- **POST** `/summarize/website`: Summarizes website content
  - Parameters: `url`, `summary_length`

### Health Check
- **GET** `/`: Simple health check endpoint

## Core Components

### API Module (`api.py`)

The `api.py` file serves as the central routing hub for the entire system. It uses FastAPI to create a RESTful API that handles various document and media processing requests.

#### Key Features:
- **FastAPI Application Setup**: Configures routes, validators, and error handlers
- **Dependency Injection**: Implements a lazy-loading pattern for summarizers to optimize resource usage
- **Request/Response Models**: Defines Pydantic models for structured data validation
- **Exception Handling**: Provides graceful error handling with informative messages
- **Background Tasks**: Manages resource cleanup (like temporary files) after processing
- **File Upload Handling**: Processes multipart form data for file uploads

#### Dependency Injection Pattern:
The API module implements a singleton pattern through dependency injection, which ensures that resource-intensive summarizers are only initialized when needed:

```python
def get_legal_summarizer():
    global legal_summarizer
    if legal_summarizer is None:
        legal_summarizer = LegalDocumentSummarizer()
    return legal_summarizer
```

This pattern prevents the system from initializing all summarizers at startup, which would be inefficient since users typically only use a subset of the available functionality.

#### Response Handling:
Each endpoint returns structured responses using Pydantic models, ensuring consistent and well-formed API responses. For example, the legal document summarization endpoint returns a `LegalSummaryResponse` with fields for document type, summary content, and processing time.

#### Error Handling:
The API implements comprehensive error handling with specific error messages and appropriate HTTP status codes:

```python
except Exception as e:
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)
    raise HTTPException(status_code=500, detail=f"Error processing legal document: {str(e)}")
```

This ensures that temporary resources are properly cleaned up even when errors occur, and clients receive informative error messages.

### Legal Document Processing (`legal.py`)

The `legal.py` module provides specialized functionality for analyzing and summarizing legal documents. It's designed to understand the structure and terminology commonly found in legal texts.

#### Key Components:

1. **LegalDocumentSummarizer Class**: The main class responsible for processing legal documents with the following key methods:
   - `load_pdf()`: Extracts text content from PDF files
   - `detect_document_type()`: Automatically identifies the type of legal document (e.g., contract, NDA, terms of service)
   - `chunk_document()`: Splits text into manageable chunks for processing
   - `search_legal_context()`: Optionally enriches analysis with external legal information (via Tavily API)
   - `summarize_chunks()`: Processes document chunks using a map-reduce approach for longer documents
   - `enhance_with_legal_context()`: Adds relevant legal context to make summaries more informative
   - `generate_summary()`: Orchestrates the complete analysis process

2. **Text Processing Strategy**:
   The module uses a specialized text splitter configured for legal documents:
   ```python
   self.text_splitter = RecursiveCharacterTextSplitter(
       chunk_size=4000,
       chunk_overlap=400,
       separators=["\n\n", "\n", ".", " ", ""],
       length_function=len
   )
   ```
   This configuration with larger chunk sizes and overlaps is optimized for legal content to ensure that contextual connections between sections are maintained.

3. **Legal-Specific Prompting**:
   The module uses carefully crafted prompt templates designed for legal analysis:
   ```python
   self.summary_prompt = PromptTemplate(
       input_variables=["text_chunks", "document_type", "question"],
       template="""
       You are a highly skilled legal expert tasked with summarizing legal documents...
       """
   )
   ```
   These prompts guide the language model to focus on legally relevant information such as parties, provisions, obligations, rights, dates, deadlines, conditions, and potential risks.

4. **Map-Reduce Approach for Long Documents**:
   For longer documents, the module uses a two-stage approach:
   1. Individual chunks are summarized separately
   2. The individual summaries are then combined into a coherent whole
   
   This approach allows the system to handle documents of arbitrary length while maintaining context.

5. **External Knowledge Integration**:
   When available, the module can use the Tavily API to fetch relevant legal information to enhance summaries:
   ```python
   def search_legal_context(self, query: str, num_results: int = 3) -> List[Dict]:
       """Use Tavily API to search for relevant legal context."""
       # Implementation details...
   ```
   This integration allows the system to add explanations of legal concepts that might not be explicitly defined in the document itself.

### General Document Processing (`normal.py`)

The `normal.py` module provides generalized document analysis capabilities for a variety of document types, including PDF, DOCX, and TXT files. It focuses on extracting key information regardless of document format or structure.

#### Key Components:

1. **Pydantic Models**: The module defines several Pydantic models for structured data handling:
   - `SummarySettings`: Configuration options for summary generation
   - `DocumentSection`: Represents a section of a document with title and content
   - `DocumentStatistics`: Basic statistics about a document (word count, reading time, etc.)
   - `Topic`: Represents a topic extracted from a document
   - `KeyPoint`: Represents a key point extracted from a document
   - `SummaryResult`: The complete result of document summary generation

2. **GeneralDocumentSummarizer Class**: The main class responsible for processing documents with methods for:
   - Document loading (`load_document()`, `_load_pdf()`, `_load_docx()`, `_load_txt()`)
   - Document analysis (`compute_document_statistics()`)
   - Document sectioning (`_split_into_sections()`, `_score_section_importance()`)
   - Summarization (`summarize_document()`, `_summarize_short_document()`, `_summarize_long_document()`)

3. **Dynamic Processing Strategy**:
   The module adapts its processing strategy based on document length:
   ```python
   if statistics.word_count < 3000:
       result = self._summarize_short_document(document_text, settings_dict, statistics)
   else:
       result = self._summarize_long_document(document_text, settings_dict, statistics)
   ```
   This ensures efficient processing for shorter documents while maintaining high-quality results for longer texts.

4. **Section Extraction and Importance Scoring**:
   The module implements heuristic-based section detection and importance scoring:
   ```python
   def _score_section_importance(self, sections: List[DocumentSection]) -> List[DocumentSection]:
       """Score sections by importance using heuristics."""
       # Position factor, length factor, keyword factor...
   ```
   This allows the system to focus on the most important parts of a document when generating summaries.

5. **Configurable Summary Generation**:
   Users can control various aspects of summary generation through the `SummarySettings` model:
   ```python
   class SummarySettings(BaseModel):
       conciseness: str = Field(default="balanced", description="Level of summary conciseness")
       focus_areas: List[str] = Field(default_factory=list)
       extract_topics: bool = Field(default=True)
       extract_key_points: bool = Field(default=True)
       include_statistics: bool = Field(default=False)
       summary_length_percentage: Optional[float] = Field(default=None)
   ```
   This allows for customization of summaries to meet different user needs.

### Resume Processing (`resume.py` & `resume_models.py`)

The resume processing functionality is split across two files:
- `resume_models.py`: Defines structured data models for resume information
- `resume.py`: Implements the processing logic for resume analysis

#### Resume Models (`resume_models.py`)

This module defines Pydantic models for representing structured resume data:

1. **Basic Models**:
   - `BasicInformation`: Personal contact details
   - `Skill`: Individual skills with proficiency levels
   - `SkillCategory`: Grouping of related skills
   - `Experience`: Work experience entries
   - `Education`: Educational background entries
   - `Certification`: Professional certifications
   - `Project`: Project details

2. **Analysis Result Models**:
   - `ResumeData`: Complete structured data extracted from a resume
   - `KeywordMatch`: ATS keyword matching results
   - `ATSAnalysis`: Applicant Tracking System compatibility analysis
   - `ResumeSummaryResult`: Overall result including structured data and narrative summary

3. **Data Validation**:
   The models include field validators to normalize and validate data:
   ```python
   @field_validator('proficiency')
   def validate_proficiency(cls, v):
       """Normalize proficiency levels if present."""
       if v:
           # Convert various formats to consistent levels
           v = v.lower().strip()
           if v in ('expert', 'advanced', 'proficient', 'high'):
               return 'Advanced'
           # ...
   ```
   This ensures consistent data representation regardless of input variations.

#### Resume Processing (`resume.py`)

This module implements the logic for extracting structured information from resumes and generating analyses:

1. **ResumeSummarizer Class**: The main class with methods for:
   - `load_pdf()`: Extract text from PDF resumes
   - `process_resume()`: Convert raw text to structured data
   - `generate_summary()`: Create a narrative summary from structured data
   - `analyze_ats_compatibility()`: Analyze resume compatibility with ATS systems
   - `process_resume_file()`: Orchestrate the complete analysis process

2. **ATS Compatibility Analysis**:
   When a job description is provided, the system can analyze how well a resume aligns with specific job requirements:
   ```python
   def analyze_ats_compatibility(self, resume_data: ResumeData, job_description: str) -> ATSAnalysis:
       """Analyze how well the resume would perform in an ATS for a specific job."""
       # Implementation details...
   ```
   This functionality helps job seekers optimize their resumes for specific positions.

3. **Structured Information Extraction**:
   The module uses carefully designed prompts to extract structured information:
   ```python
   self.resume_analysis_prompt = PromptTemplate(
       input_variables=["resume_text"],
       template="""
       You are an expert resume analyzer and HR professional. Extract and structure information...
       """
   )
   ```
   The extracted information is then validated against the Pydantic models to ensure consistency.

4. **Error Handling**:
   The module includes robust error handling to manage parsing failures:
   ```python
   try:
       # Extract JSON if it's embedded in other text
       json_start = structured_data_str.find('{')
       json_end = structured_data_str.rfind('}') + 1
       # ...
   except Exception as e:
       print(f"Error parsing response: {e}")
       # Return a minimal structure if parsing fails
       return ResumeData()
   ```
   This ensures the system can gracefully handle unexpected outputs from language models.

### Speech/Audio Processing (`speech.py`)

The `speech.py` module provides functionality for transcribing and summarizing audio content. It integrates with AssemblyAI for transcription and uses language models for summarization.

#### Key Components:

1. **Core Functions**:
   - `transcribe_audio()`: Converts audio to text using AssemblyAI
   - `split_text_recursive()`: Divides long transcripts into manageable chunks
   - `summarize_text()`: Creates concise summaries of transcribed text
   - `process_audio()`: Orchestrates the complete audio processing pipeline

2. **Chunking Strategy**:
   For managing long audio transcripts, the module uses a recursive text splitter:
   ```python
   text_splitter = RecursiveCharacterTextSplitter(
       chunk_size=chunk_size,
       chunk_overlap=chunk_overlap,
       length_function=len,
       separators=["\n\n", "\n", ". ", " ", ""]
   )
   ```
   This ensures that text is split at natural boundaries when possible.

3. **Adaptive Summarization**:
   The module adjusts summary length based on the input size:
   ```python
   # Calculate target summary length per chunk
   target_length_per_chunk = max_summary_length // len(chunks)
   ```
   This approach produces proportional summaries regardless of input length.

4. **Map-Reduce Summarization**:
   For longer audio, the module uses a two-stage approach:
   1. Generate individual summaries for each chunk
   2. Combine and refine these into a final summary
   
   ```python
   # Generate a final, cohesive summary if there are multiple chunks
   if len(chunks) > 1:
       try:
           final_prompt = f"""
           Create a coherent, unified summary from these partial summaries...
           """
           # ...
   ```
   This produces cohesive summaries even for lengthy content.

### Video Processing (`video_agent.py`)

The `video_agent.py` module provides functionality for analyzing and summarizing video content from both YouTube and uploaded files. It leverages agent-based architectures from `agno` and `phi` libraries.

#### Key Components:

1. **Agent Initialization**:
   - `initialize_youtube_agent()`: Creates an agent specifically for YouTube videos
   - `initialize_multimodal_agent()`: Creates an agent for processing uploaded videos

2. **Video Processing Functions**:
   - `process_youtube_video()`: Extracts and summarizes content from YouTube videos
   - `process_uploaded_video()`: Analyzes uploaded video files
   - `save_uploaded_video()`: Temporarily stores uploaded video data
   - `cleanup_video_file()`: Removes temporary video files

3. **Fallback Mechanisms**:
   The module includes robust fallback mechanisms for handling processing failures:
   ```python
   except Exception as error:
       # Fallback approach if video processing fails
       try:
           fallback_prompt = (
               f"This is a video analysis request. The user asked: {query}. "
               # ...
           )
           # ...
       except:
           return f"An error occurred during analysis: {error}"
   ```
   This ensures users receive helpful responses even when direct video processing isn't possible.

4. **Multi-Model Integration**:
   The module uses different AI models depending on the task:
   - OpenAI for YouTube caption analysis
   - Google Gemini for multimodal video analysis
   
   This specialized approach provides optimal results for each type of content.

### Website Processing (`website.py`)

The `website.py` module handles the extraction and summarization of content from websites. It uses asyncio for non-blocking operations and integrates with crawl4ai for web content extraction.

#### Key Components:

1. **Core Async Functions**:
   - `fetch_transcript()`: Extracts clean content from websites
   - `summarize_content()`: Creates concise summaries of web content
   - `main()`: Example function demonstrating usage

2. **Web Crawling Integration**:
   The module uses crawler configurations from crawl4ai:
   ```python
   browser_config = BrowserConfig()  # Default browser configuration
   run_config = CrawlerRunConfig()   # Default crawl run configuration

   async with AsyncWebCrawler(config=browser_config) as crawler:
       result = await crawler.arun(url=url, config=run_config)
   ```
   This provides robust web content extraction capabilities.

3. **Customizable Summary Length**:
   The module allows for different summary lengths based on user preference:
   ```python
   summary_word_count = {
       "Short": 100,
       "Medium": 300,
       "Long": 500
   }[summary_length]
   ```
   This flexibility accommodates different user needs.

4. **Model Integration**:
   The module uses Groq's implementation of the Gemma model for efficient summarization:
   ```python
   llm = ChatGroq(model="gemma2-9b-it", groq_api_key=GROQ_API_KEY)
   ```
   This provides high-quality summaries while potentially offering better performance than larger models.

## Development Guidelines

When extending or modifying the Ultimate Summarization API, consider the following guidelines:

1. **Modularity**:
   - Keep the distinct processing modules (legal, general, resume, audio, video, website) separate
   - Use consistent interfaces across modules to ensure API consistency

2. **Error Handling**:
   - Always clean up temporary resources, especially in error scenarios
   - Provide specific, actionable error messages
   - Use appropriate HTTP status codes for different error types

3. **Configuration Management**:
   - Use environment variables for sensitive information (API keys)
   - Consider allowing runtime configuration for model selection and other parameters

4. **Testing**:
   - Add unit tests for individual components
   - Implement integration tests for API endpoints
   - Consider adding performance benchmarks for monitoring

5. **Documentation**:
   - Update this README when adding new functionality
   - Document API changes in the OpenAPI schema
   - Add inline comments for complex logic

## Environment Variables

The system requires several environment variables to function properly:

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | API key for OpenAI services (required for most modules) |
| `GOOGLE_API_KEY` | API key for Google Gemini services (required for video processing) |
| `TAVILY_API_KEY` | API key for Tavily search (optional, enhances legal document analysis) |
| `GROQ_API_KEY` | API key for Groq services (required for website summarization) |

These should be set in a `.env` file or through your deployment environment.

## Troubleshooting

### Common Issues and Solutions

1. **API Key Errors**:
   - Ensure all required API keys are correctly set in the environment
   - Check that keys have not expired or hit usage limits

2. **File Processing Errors**:
   - Verify that uploaded files meet the expected format requirements
   - Check that file sizes are within acceptable limits

3. **Model Response Issues**:
   - For intermittent failures, consider implementing retry logic
   - For consistently poor responses, consider adjusting prompt templates

4. **Memory Usage**:
   - Monitor memory usage when processing large files
   - Consider implementing streaming responses for large outputs

5. **Performance Optimization**:
   - Use asynchronous processing where possible
   - Consider caching results for frequently accessed content

## Future Development

Potential areas for enhancement include:

1. **Additional Content Types**:
   - Email summarization
   - Social media content analysis
   - Academic paper analysis

2. **Enhanced Integration Options**:
   - Webhook notifications for long-running processes
   - OAuth support for accessing protected content

3. **Performance Improvements**:
   - Response caching layer
   - Query parameter optimization
   - Streaming response support

4. **User Experience Enhancements**:
   - Customizable templates for different summary formats
   - Progress tracking for long-running processes
   - Batch processing capabilities

5. **Monitoring and Analytics**:
   - Usage tracking and reporting
   - Performance metrics collection
   - Quality assessment of generated summaries