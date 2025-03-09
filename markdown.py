import asyncio
from api_management import get_supabase_client
from utils import generate_unique_name
from crawl4ai import AsyncWebCrawler

supabase = get_supabase_client()

async def get_fit_markdown_async(url: str) -> str:
    """
    Uses crawl4ai's AsyncWebCrawler to produce raw markdown.
    """
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        if result.success:
            return result.markdown
        else:
            return ""

def fetch_fit_markdown(url: str) -> str:
    """
    Synchronous wrapper for get_fit_markdown_async.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(get_fit_markdown_async(url))
    finally:
        loop.close()

def read_raw_data(unique_name: str) -> str:
    """
    Retrieves 'raw_data' from Supabase for the given unique_name.
    """
    response = supabase.table("scraped_data").select("raw_data").eq("unique_name", unique_name).execute()
    data = response.data
    if data and len(data) > 0:
        return data[0]["raw_data"]
    return ""

def save_raw_data(unique_name: str, url: str, raw_data: str) -> None:
    """
    Saves or updates raw_data in Supabase.
    """
    supabase.table("scraped_data").upsert({
        "unique_name": unique_name,
        "url": url,
        "raw_data": raw_data
    }, on_conflict="id").execute()
    print(f"INFO: Raw data stored for {unique_name}")

def fetch_and_store_markdowns(urls: list) -> list:
    """
    For each URL, generate a unique name, check for existing data, and fetch/store markdown.
    Returns a list of unique names.
    """
    unique_names = []
    for url in urls:
        unique_name = generate_unique_name(url)
        raw_data = read_raw_data(unique_name)
        if raw_data:
            print(f"Found existing data for {url} => {unique_name}")
        else:
            fit_md = fetch_fit_markdown(url)
            save_raw_data(unique_name, url, fit_md)
        unique_names.append(unique_name)
    return unique_names
