# Document Summarization API

A FastAPI application that provides endpoints for summarizing and analyzing different types of documents:

1. **Legal Documents** - Specialized summarization for contracts, agreements, and other legal texts
2. **General Documents** - Comprehensive summarization for any general documents
3. **Resumes** - Structured extraction and analysis of resume information with ATS compatibility scoring

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the project root with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   TAVILY_API_KEY=your_tavily_api_key  # Optional, for legal document external context
   ```

## Running the API

Start the FastAPI server:

```
uvicorn main:app --reload
```

The API will be available at http://localhost:8000

API documentation is automatically generated and available at:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

## API Endpoints

### Legal Document Summarization

**POST** `/api/legal/summarize`

Upload a legal document (PDF) and get a comprehensive summary. Optionally provide a custom question to focus the summary.

### General Document Summarization 

**POST** `/api/general/summarize`

Upload a general document (PDF, DOCX, or TXT) and get both an executive summary and a detailed summary, along with key topics and points.

### Resume Analysis

**POST** `/api/resume/analyze`

Upload a resume (PDF) and get structured information extraction and a narrative summary. Optionally provide a job description to get ATS compatibility analysis.

## Example Usage

### Using curl

#### Legal Document Summarization:
```bash
curl -X POST "http://localhost:8000/api/legal/summarize" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@contract.pdf" \
     -F "custom_question=What are the key obligations of each party?"
```

#### General Document Summarization:
```bash
curl -X POST "http://localhost:8000/api/general/summarize" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@document.pdf" \
     -F "conciseness=very_concise" \
     -F "extract_topics=true" \
     -F "extract_key_points=true" \
     -F "include_statistics=true"
```

#### Resume Analysis:
```bash
curl -X POST "http://localhost:8000/api/resume/analyze" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@resume.pdf" \
     -F "job_description=Job description text here..."
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
