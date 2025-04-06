# Ultimate Summarization API

A unified API for summarizing various types of content:
- YouTube videos
- Uploaded videos
- Audio files
- Documents (general, resume, legal)
- Websites

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your API keys:
   ```
   GOOGLE_API_KEY=your_google_api_key
   OPENAI_API_KEY=your_openai_api_key
   GROQ_API_KEY=your_groq_api_key
   ```

## Running the API

Start the FastAPI server:
```
python api.py
```

Or use uvicorn directly:
```
uvicorn api:app --reload
```

The API will be available at http://localhost:8000

## API Documentation

Interactive API documentation is automatically generated and available at http://localhost:8000/docs

## Endpoints

### Video Summarization

#### Summarize YouTube Video
```
POST /summarize/youtube
```
Request body:
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "query": "Summarize this video"
}
```

#### Summarize Uploaded Video
```
POST /summarize/video
```
Form data:
- `file`: Video file (mp4, etc.)
- `query`: Query for the video (default: "Summarize this video")

### Audio Summarization

```
POST /summarize/audio
```
Form data:
- `file`: Audio file (mp3, wav, etc.)

### Document Summarization

```
POST /summarize/document
```
Form data:
- `file`: Document file (pdf, docx, etc.)
- `mode`: Document type - "general", "resume", or "legal" (default: "general")
- `settings`: (Optional) Document-specific settings

### Website Summarization

```
POST /summarize/website
```
Request body:
```json
{
  "url": "https://example.com",
  "summary_length": "Medium"
}
```
Summary length options: "Short", "Medium", "Long"

## Examples

### cURL Examples

#### Summarize YouTube Video
```bash
curl -X 'POST' \
  'http://localhost:8000/summarize/youtube' \
  -H 'Content-Type: application/json' \
  -d '{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "query": "Summarize the main points of this video"
  }'
```

#### Summarize Website
```bash
curl -X 'POST' \
  'http://localhost:8000/summarize/website' \
  -H 'Content-Type: application/json' \
  -d '{
    "url": "https://en.wikipedia.org/wiki/Artificial_intelligence",
    "summary_length": "Medium"
  }'
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
