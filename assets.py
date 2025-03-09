"""
This module contains configuration variables and constants used across the application.
"""

GEMINI_MODEL_FULLNAME = "gemini/gemini-1.5-flash"
OPENAI_MODEL_FULLNAME = "gpt-4o-mini"
DEEPSEEK_MODEL_FULLNAME = "groq/deepseek-r1-distill-llama-70b"

MODELS_USED = {
    OPENAI_MODEL_FULLNAME: {"OPENAI_API_KEY"},
    GEMINI_MODEL_FULLNAME: {"GEMINI_API_KEY"},
    DEEPSEEK_MODEL_FULLNAME: {"GROQ_API_KEY"},
}

# Timeout settings for web scraping
TIMEOUT_SETTINGS = {
    "page_load": 30,
    "script": 10
}

NUMBER_SCROLL = 2

SYSTEM_MESSAGE = (
    "You are an intelligent text extraction and conversion assistant. Your task is to extract structured information "
    "from the given text and convert it into a pure JSON format. The JSON should contain only the structured data extracted, "
    "with no additional commentary, explanations, or extraneous information. In cases where data is missing or in a foreign language, "
    "handle accordingly. Process the following text and provide the output in pure JSON format with no extra text."
)

USER_MESSAGE = "Extract the following information from the provided text:\nPage content:\n\n"

PROMPT_PAGINATION = """
You are an assistant that extracts pagination URLs from markdown content of websites. 
Your task is to identify and generate a list of pagination URLs based on a detected URL pattern where page numbers increment sequentially. Follow these instructions carefully:

- Identify the Pagination Pattern:
  Analyze the provided markdown text to detect URLs that follow a pattern where only a numeric page indicator changes.
  If the numbers start from a low value and increment, generate the full sequence of URLs—even if not all numbers are present in the text.

- Construct Complete URLs:
  In cases where only part of a URL is provided, combine it with the given base URL to form complete URLs.
  Ensure that every URL you generate is clickable and leads directly to the intended page.

- Incorporate User Indications:
  Use any additional user instructions to refine your URL generation.

Output only a valid JSON object with the following structure:
{
    "page_urls": ["url1", "url2", "url3", ..., "urlN"]
}

IMPORTANT: Output only the JSON with no extra text.
"""
