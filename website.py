import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
import os
import logging
import time
from dotenv import load_dotenv

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set your Groq API key here
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

async def fetch_transcript(url, max_retries=3, timeout=60):
    """
    Fetch website content with retry logic for handling browser issues.
    
    Args:
        url (str): The URL to fetch content from
        max_retries (int): Maximum number of retry attempts
        timeout (int): Timeout in seconds for the browser operation
        
    Returns:
        str: Markdown content from the website
    """
    retry_count = 0
    last_error = None
    
    while retry_count < max_retries:
        try:
            # Configure browser with longer timeout and more robust settings
            browser_config = BrowserConfig(
                timeout=timeout * 1000,  # Convert to milliseconds
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            
            # Configure crawler run with more robust settings
            run_config = CrawlerRunConfig(
                timeout=timeout,
                wait_for=2000  # Wait 2 seconds after page load
            )
            
            logger.info(f"Attempting to fetch URL: {url} (Attempt {retry_count + 1}/{max_retries})")
            
            # Use a separate try/except block to handle browser context issues
            try:
                async with AsyncWebCrawler(config=browser_config) as crawler:
                    result = await crawler.arun(url=url, config=run_config)
                    content = result.markdown  # Get markdown content
                    
                    # Verify we got actual content
                    if not content or len(content.strip()) < 50:
                        logger.warning(f"Retrieved content seems too short, retrying: {len(content) if content else 0} chars")
                        raise ValueError("Content too short")
                        
                    logger.info(f"Successfully fetched content from {url} ({len(content)} chars)")
                    return content
            except Exception as browser_error:
                logger.error(f"Browser error: {str(browser_error)}")
                raise  # Re-raise for outer handler
                
        except Exception as e:
            last_error = e
            logger.warning(f"Error fetching {url} (attempt {retry_count + 1}): {str(e)}")
            retry_count += 1
            
            if retry_count < max_retries:
                # Exponential backoff: 1s, 2s, 4s, etc.
                wait_time = 2 ** (retry_count - 1)
                logger.info(f"Waiting {wait_time}s before retry...")
                await asyncio.sleep(wait_time)
    
    # If we get here, all retries failed
    logger.error(f"All {max_retries} attempts to fetch {url} failed")
    raise last_error or ValueError(f"Failed to fetch content from {url} after {max_retries} attempts")

async def summarize_content(content, summary_length):
    # Initialize the ChatGroq model
    llm = ChatGroq(model="gemma2-9b-it", groq_api_key=GROQ_API_KEY)

    # Ensure content is a string
    if not isinstance(content, str):
        raise ValueError("Content must be a string.")

    # Create messages for the model
    system_message = SystemMessage(content="You are a helpful assistant that summarizes content.")
    human_message = HumanMessage(content=f"Summarize the following content in {summary_length} words:\n\n{content}")

    logger.info(f"Sending content to Groq for summarization ({len(content)} chars)")
    
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