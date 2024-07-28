# Ultimate Summarization App
## Introduction
Welcome to the Ultimate Summarization App! This versatile application is designed to provide concise and accurate summaries for various types of content, including websites, documents, and speech. Built using state-of-the-art technologies and APIs, our app leverages Langchain, Grog API, OpenAI API, AssemblyAI, and Hugging Face Transformers to deliver high-quality summarization results.
## Features
1. Website URL Summarization
2. Document Summarization
3. Speech to Text Summarization
## Technologies Used

**Langchain**: A library for building applications with language models.\
**Grog API**: Used for website content summarization.\
**OpenAI API**: Used for document summarization.
**AssemblyAI**: Used for converting speech to text.
**Hugging Face Transformers**: Used for text summarization with the sshleifer/distilbart-cnn-12-6 model.
## Installation
1. Clone the repository:

```
git clone https://github.com/yourusername/ultimate-summarization-app.git
cd ultimate-summarization-app
```
2. Install the required Python packages:
```
pip install -r requirements.txt
```
3. Set up API keys:

Obtain your API keys from Grog, OpenAI, and AssemblyAI.\
Create a .env file in the root directory of the project and add the following lines:
```
GROG_API_KEY=your_grog_api_key
OPENAI_API_KEY=your_openai_api_key
ASSEMBLYAI_API_KEY=your_assemblyai_api_key
```