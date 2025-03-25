# Ultimate Summarization App

## Introduction

Welcome to the Ultimate Summarization App! This versatile application is designed to provide concise and accurate summaries for various types of content, including websites, documents, videos, and speech. Built using state-of-the-art technologies and APIs, our app leverages LangChain, Groq API, OpenAI API, AssemblyAI, Google Gemini, and Hugging Face Transformers to deliver high-quality summarization results that fit your needs.

## Features

### 1. Website URL Summarization
- Summarize content from any website or YouTube video URL
- Customize summary length (short, medium, or long)
- Automatically extracts and processes content using Groq's Gemma 2-9B model

### 2. Document Summarization
- Support for PDF and TXT file formats
- Three different summarization methods:
  - **Stuff**: Best for shorter documents, processes the entire text at once
  - **Map-Reduce**: Effective for longer documents, breaks text into chunks for processing
  - **Refine**: Iteratively builds a summary by adding information from each document section

### 3. Speech to Text Summarization
- Upload audio files (MP3, MP4, WAV, M4A formats supported)
- Automatic transcription using AssemblyAI
- Generates bullet-point summaries of the transcribed content

### 4. Video Analysis
- Upload video files (MP4, MOV, AVI formats)
- Ask specific questions about video content
- AI-powered analysis using Google Gemini 2.0 Flash
- Combines video insights with web research for contextual understanding

## Technologies Used

- **LangChain**: Framework for building applications with language models
- **Groq API**: Powers website content summarization with the Gemma 2-9B-IT model
- **OpenAI API**: Handles document summarization with GPT-3.5 Turbo
- **AssemblyAI**: Converts speech to text for audio summarization
- **Hugging Face Transformers**: Implements text summarization with the distilbart-cnn-12-6 model
- **Google Generative AI**: Powers video analysis with Gemini 2.0 Flash
- **Streamlit**: Creates the interactive web interface

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ultimate-summarization-app.git
cd ultimate-summarization-app
```

2. Install the required Python packages:
```bash
pip install -r requirements.txt
```

3. Set up API keys:

Obtain your API keys from Google, Groq, OpenAI, and AssemblyAI.
Create a `.env` file in the root directory of the project and add the following lines:

```
GOOGLE_API_KEY=your_google_api_key
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key
ASSEMBLYAI_API_KEY=your_assemblyai_api_key
```

## Usage

Run the application using Streamlit:

```bash
streamlit run final.py
```

Navigate to the provided local URL (typically http://localhost:8501) to access the application.

### Website Summarization
1. Select "Website" from the sidebar navigation
2. Enter a URL (website or YouTube video)
3. Choose your preferred summary length
4. Click "Summarize the Content from YT or Website"

### Speech Summarization
1. Select "Speech" from the sidebar navigation
2. Upload an audio file in a supported format
3. Click "Transcribe and Summarize"
4. View the bullet-point summary of your audio content

### Document Summarization
1. Select "Document" from the sidebar navigation
2. Upload a PDF or TXT file
3. Choose your preferred summarization method
4. Click "Summarize"
5. View both the original text and the generated summary

### Video Analysis
1. Select "Video" from the sidebar navigation
2. Upload a video file in a supported format
3. Enter a question or specify what insights you're seeking
4. Click "Analyze Video"
5. Review the AI-generated analysis

## Dependencies

See the full list of dependencies in the `requirements.txt` file. Key dependencies include:

- streamlit
- transformers
- assemblyai
- openai
- pymupdf
- langchain and related packages
- google-generativeai
- validators
- youtube_transcript_api
- and more...

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- This project uses several powerful AI APIs and tools
- Thanks to the creators and maintainers of LangChain, Transformers, and other libraries that make this possible
