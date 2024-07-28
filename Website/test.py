import validators
import streamlit as st
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import YoutubeLoader, UnstructuredURLLoader

# Set your Groq API key here
#GROQ_API_KEY = "your grog api key"

def main():
    # Streamlit App Configuration
    st.set_page_config(page_title="LangChain: Summarize Text From YT or Website", page_icon="🦜")
    st.title("🦜 LangChain: Summarize Text From YT or Website")
    st.subheader('Summarize URL')

    # Input field for URL
    generic_url = st.text_input("Enter URL (YouTube or Website)", help="Paste the URL of the YouTube video or website to summarize")

    # Summary length option on the main page
    summary_length = st.selectbox("Summary Length", options=["Short", "Medium", "Long"], index=1, help="Select the length of the summary")

    # Set summary length based on user selection
    summary_word_count = {
        "Short": 100,
        "Medium": 300,
        "Long": 500
    }[summary_length]

    # Gemma Model using Groq API
    llm = ChatGroq(model="Gemma-7b-It", groq_api_key=GROQ_API_KEY)

    # Prompt template for summarization
    prompt_template = f"""
    Provide a summary of the following content in {summary_word_count} words:
    Content: {{text}}
    """
    prompt = PromptTemplate(template=prompt_template, input_variables=["text"])

    # Button to trigger summarization
    if st.button("Summarize the Content from YT or Website"):
        # Validate the inputs
        if not generic_url.strip():
            st.error("Please provide a URL to get started")
        elif not validators.url(generic_url):
            st.error("Please enter a valid URL. It can be a YouTube video URL or a website URL")
        else:
            try:
                with st.spinner("Fetching and summarizing content..."):
                    # Load the content from the URL
                    if "youtube.com" in generic_url or "youtu.be" in generic_url:
                        loader = YoutubeLoader.from_youtube_url(generic_url, add_video_info=True)
                        docs = loader.load()
                        # Display YouTube video info
                        video_info = docs[0].metadata
                        st.info(f"Title: {video_info['title']}\nChannel: {video_info['channel']}\nPublished At: {video_info['publish_date']}")
                    else:
                        loader = UnstructuredURLLoader(
                            urls=[generic_url],
                            ssl_verify=False,
                            headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"}
                        )
                        docs = loader.load()

                    # Chain for summarization
                    chain = load_summarize_chain(llm, chain_type="stuff", prompt=prompt)
                    output_summary = chain.run(docs)

                    st.success("Summary:")
                    st.write(output_summary)
            except Exception as e:
                st.error("An error occurred during summarization")
                st.exception(f"Exception: {e}")

if __name__ == "__main__":
    main()