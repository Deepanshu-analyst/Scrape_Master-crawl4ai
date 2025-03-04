# SaaS Web Scraper with AI and Microservices Architecture

## Features
- **Multi-page crawling with pagination** using Playwright.
- **Improved AI prompts** for better structured data extraction via Gemini AI (or your chosen model).
- **Enhanced error handling** for failed pages (with retries and error messages).
- **Caching for optimized speed** using in-memory caching.
- **User API key management** for secure access.
- Microservices and helper modules built using FastAPI and Streamlit for the frontend.
- Data is stored/retrieved via Supabase.

## Project Structure

## Installation

### Prerequisites
- Python 3.9+
- Node.js (required by Playwright)
- pip, virtualenv

### Setup
1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-repo/saas-web-scraper.git
   cd saas-web-scraper

### Create and activate a virtual environment:
    ```bash
    python -m venv venv

# On Windows:
 ```bash
venv\Scripts\activate

# On Mac/Linux:
 ```bash
source venv/bin/activate

### Install dependencies:
 ```bash
pip install -r requirements.txt

### Install Playwright browsers:
 ```bash
playwright install

## Set up environment variables: Create a .env file in the project root and add your API keys:

API_KEY=your-api-key
GEMINI_API_KEY=your-gemini-api-key
OPENAI_API_KEY=your-openai-api-key
SUPABASE_URL=your_supabase_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here

## Set up Supabase:

Create a free Supabase account.
Create a new project.
Run this SQL in the Supabase SQL Editor to create the table

 ```bash
CREATE TABLE IF NOT EXISTS scraped_data (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    unique_name TEXT NOT NULL,
    url TEXT,
    raw_data JSONB,
    formatted_data JSONB,
    pagination_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

## Running the App

Start the Streamlit Frontend: From the project root, run

 ```bash
streamlit run streamlit_app.py


# Use the UI to:
Enter one or more URLs (space/tab/newline separated).
Input your API keys (they are used to validate requests).
Specify the number of pages to scrape (pagination).
Optionally list fields to extract (e.g., for lead generation).
Launch the scraper to see structured data and pagination results.
Download results as JSON or CSV.
