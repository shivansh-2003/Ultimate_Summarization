import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
import os
from dotenv import load_dotenv

load_dotenv()

# Set your Groq API key here
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

async def fetch_transcript(url):
    browser_config = BrowserConfig()  # Default browser configuration
    run_config = CrawlerRunConfig()   # Default crawl run configuration

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=url, config=run_config)
        return result.markdown  # Return clean markdown content

async def summarize_content(content, summary_length):
    # Initialize the ChatGroq model
    llm = ChatGroq(model="gemma2-9b-it", groq_api_key=GROQ_API_KEY)

    # Ensure content is a string
    if not isinstance(content, str):
        raise ValueError("Content must be a string.")

    # Create messages for the model
    system_message = SystemMessage(content="You are a helpful assistant that summarizes content.")
    human_message = HumanMessage(content=f"Summarize the following content in {summary_length} words:\n\n{content}")

    # Run the summarization with proper message format
    response = await llm.ainvoke([system_message, human_message])
    
    # Return the content of the response
    return response.content

async def main():
    url = "https://www.assemblyai.com/docs/speech-to-text/pre-recorded-audio"  # Example URL
    transcript = await fetch_transcript(url)

    # Set summary length based on user selection (example: "Medium")
    summary_length = "Long"  # This can be dynamically set based on user input
    summary_word_count = {
        "Short": 100,
        "Medium": 300,
        "Long": 500
    }[summary_length]

    summary = await summarize_content(transcript, summary_word_count)
    print("Summary:")
    print(summary)

if __name__ == "__main__":
    asyncio.run(main())