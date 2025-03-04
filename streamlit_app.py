import streamlit as st
from streamlit_tags import st_tags_sidebar
import pandas as pd
import json
import re
import sys
import asyncio
# Local imports
from scraper import scrape_urls
from pagination import paginate_urls
from markdown import fetch_and_store_markdowns
from assets import MODELS_USED
from api_management import get_supabase_client

# Set event loop policy for Windows
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

st.set_page_config(page_title=" TRAI SpiderMIND", page_icon="🦑")
supabase = get_supabase_client()
if supabase is None:
    st.error("🚨 Supabase is not configured! Follow the README instructions to set it up.")
    st.stop()

st.title("TRAI SpiderMIND  🦑")

if 'scraping_state' not in st.session_state:
    st.session_state['scraping_state'] = 'idle'
if 'results' not in st.session_state:
    st.session_state['results'] = None

st.sidebar.title("Web Scraper Settings")

with st.sidebar.expander("API Keys", expanded=False):
    for model, required_keys in MODELS_USED.items():
        for key_name in required_keys:
            st.text_input(key_name, type="password", key=key_name)
    st.session_state['SUPABASE_URL'] = st.text_input("SUPABASE URL")
    st.session_state['SUPABASE_ANON_KEY'] = st.text_input("SUPABASE ANON KEY", type="password")

model_selection = st.sidebar.selectbox("Select Model", options=list(MODELS_USED.keys()), index=0)
st.sidebar.markdown("---")
st.sidebar.write("## URL Input Section")

if "urls_splitted" not in st.session_state:
    st.session_state["urls_splitted"] = []

with st.sidebar.container():
    col1, col2 = st.columns([3, 1], gap="small")
    with col1:
        if "text_temp" not in st.session_state:
            st.session_state["text_temp"] = ""
        url_text = st.text_area("Enter one or more URLs (space/tab/newline separated):", st.session_state["text_temp"], key="url_text_input", height=68)
    with col2:
        if st.button("Add URLs"):
            if url_text.strip():
                new_urls = re.split(r"\s+", url_text.strip())
                new_urls = [u for u in new_urls if u]
                st.session_state["urls_splitted"].extend(new_urls)
                st.session_state["text_temp"] = ""
                st.rerun()
        if st.button("Clear URLs"):
            st.session_state["urls_splitted"] = []
            st.rerun()
    with st.expander("Added URLs", expanded=True):
        if st.session_state["urls_splitted"]:
            bubble_html = ""
            for url in st.session_state["urls_splitted"]:
                bubble_html += (
                    f"<span style='background-color: #E6F9F3; color: #0074D9; border-radius: 15px; padding: 8px 12px; margin: 5px; display: inline-block; text-decoration: none; font-weight: bold; font-family: Arial, sans-serif; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);'>{url}</span>"
                )
            st.markdown(bubble_html, unsafe_allow_html=True)
        else:
            st.write("No URLs added yet.")

st.sidebar.markdown("---")
show_tags = st.sidebar.toggle("Enable Scraping")
fields = []
if show_tags:
    fields = st_tags_sidebar(label='Enter Fields to Extract:', text='Press enter to add a field', value=[], suggestions=[], maxtags=-1, key='fields_input')

st.sidebar.markdown("---")
use_pagination = st.sidebar.toggle("Enable Pagination")
pagination_details = ""
if use_pagination:
    pagination_details = st.sidebar.text_input("Enter Pagination Details (optional)", help="Describe how to navigate through pages (e.g., 'Next' button class, URL pattern)")
st.sidebar.markdown("---")

if st.sidebar.button("LAUNCH", type="primary"):
    if not st.session_state["urls_splitted"]:
        st.error("Please enter at least one URL.")
    elif show_tags and len(fields) == 0:
        st.error("Please enter at least one field to extract.")
    else:
        st.session_state['urls'] = st.session_state["urls_splitted"]
        st.session_state['fields'] = fields
        st.session_state['model_selection'] = model_selection
        st.session_state['use_pagination'] = use_pagination
        st.session_state['pagination_details'] = pagination_details
        unique_names = fetch_and_store_markdowns(st.session_state["urls_splitted"])
        st.session_state["unique_names"] = unique_names
        st.session_state['scraping_state'] = 'scraping'

if st.session_state['scraping_state'] == 'scraping':
    try:
        with st.spinner("Processing..."):
            unique_names = st.session_state["unique_names"]
            total_input_tokens = 0
            total_output_tokens = 0
            total_cost = 0
            all_data = []
            if show_tags:
                in_tokens_s, out_tokens_s, cost_s, parsed_data = scrape_urls(unique_names, st.session_state['fields'], st.session_state['model_selection'])
                total_input_tokens += in_tokens_s
                total_output_tokens += out_tokens_s
                total_cost += cost_s
                all_data = parsed_data
                st.session_state['in_tokens_s'] = in_tokens_s
                st.session_state['out_tokens_s'] = out_tokens_s
                st.session_state['cost_s'] = cost_s
            pagination_info = None
            if st.session_state['use_pagination']:
                in_tokens_p, out_tokens_p, cost_p, page_results = paginate_urls(unique_names, st.session_state['model_selection'], st.session_state['pagination_details'], st.session_state["urls_splitted"])
                total_input_tokens += in_tokens_p
                total_output_tokens += out_tokens_p
                total_cost += cost_p
                pagination_info = page_results
                st.session_state['in_tokens_p'] = in_tokens_p
                st.session_state['out_tokens_p'] = out_tokens_p
                st.session_state['cost_p'] = cost_p
            st.session_state['results'] = {
                'data': all_data,
                'input_tokens': total_input_tokens,
                'output_tokens': total_output_tokens,
                'total_cost': total_cost,
                'pagination_info': pagination_info
            }
            st.session_state['scraping_state'] = 'completed'
    except Exception as e:
        st.error(f"An error occurred during scraping: {e}")
        st.session_state['scraping_state'] = 'idle'

if st.session_state['scraping_state'] == 'completed' and st.session_state['results']:
    results = st.session_state['results']
    all_data = results['data']
    total_input_tokens = results['input_tokens']
    total_output_tokens = results['output_tokens']
    total_cost = results['total_cost']
    pagination_info = results['pagination_info']
    if show_tags:
        st.subheader("Scraping Results")
        all_rows = []
        for i, data_item in enumerate(all_data, start=1):
            if not isinstance(data_item, dict):
                st.error(f"data_item is not a dict, skipping. Type: {type(data_item)}")
                continue
            if "parsed_data" in data_item:
                parsed_obj = data_item["parsed_data"]
                if hasattr(parsed_obj, "dict"):
                    parsed_obj = parsed_obj.model_dump()
                elif isinstance(parsed_obj, str):
                    try:
                        parsed_obj = json.loads(parsed_obj)
                    except json.JSONDecodeError:
                        pass
                data_item["parsed_data"] = parsed_obj
            pd_obj = data_item["parsed_data"]
            if isinstance(pd_obj, dict) and "listings" in pd_obj and isinstance(pd_obj["listings"], list):
                for listing in pd_obj["listings"]:
                    row_dict = dict(listing)
                    all_rows.append(row_dict)
            else:
                row_dict = dict(data_item)
                all_rows.append(row_dict)
        if not all_rows:
            st.warning("No data rows to display.")
        else:
            df = pd.DataFrame(all_rows)
            st.dataframe(df, use_container_width=True)
        if "in_tokens_s" in st.session_state:
            st.sidebar.markdown("### Scraping Details")
            st.sidebar.markdown("#### Token Usage")
            st.sidebar.markdown(f"*Input Tokens:* {st.session_state['in_tokens_s']}")
            st.sidebar.markdown(f"*Output Tokens:* {st.session_state['out_tokens_s']}")
            st.sidebar.markdown(f"**Total Cost:** ${st.session_state['cost_s']:.4f}")
        st.subheader("Download Extracted Data")
        col1, col2 = st.columns(2)
        with col1:
            json_data = json.dumps(all_data, default=lambda o: o.dict() if hasattr(o, 'dict') else str(o), indent=4)
            st.download_button("Download JSON", data=json_data, file_name="scraped_data.json")
        with col2:
            all_listings = []
            for data in all_data:
                if isinstance(data, str):
                    try:
                        data = json.loads(data)
                    except json.JSONDecodeError:
                        continue
                if isinstance(data, dict) and 'listings' in data:
                    all_listings.extend(data['listings'])
                elif hasattr(data, 'listings'):
                    all_listings.extend([item.dict() for item in data.listings])
                else:
                    all_listings.append(data)
            combined_df = pd.DataFrame(all_listings)
            st.download_button("Download CSV", data=combined_df.to_csv(index=False), file_name="scraped_data.csv")
        st.success("Scraping completed. Results saved in database.")
    if pagination_info:
        all_page_rows = []
        for i, item in enumerate(pagination_info, start=1):
            if not isinstance(item, dict):
                st.error(f"item is not a dict, skipping. Type: {type(item)}")
                continue
            if "pagination_data" in item:
                pag_obj = item["pagination_data"]
                if hasattr(pag_obj, "dict"):
                    pag_obj = pag_obj.model_dump()
                elif isinstance(pag_obj, str):
                    try:
                        pag_obj = json.loads(pag_obj)
                    except json.JSONDecodeError:
                        pass
                item["pagination_data"] = pag_obj
            pd_obj = item["pagination_data"]
            if isinstance(pd_obj, dict) and "page_urls" in pd_obj and isinstance(pd_obj["page_urls"], list):
                for page_url in pd_obj["page_urls"]:
                    row_dict = {"page_url": page_url}
                    all_page_rows.append(row_dict)
            else:
                row_dict = dict(item)
                all_page_rows.append(row_dict)
        if not all_page_rows:
            st.warning("No page URLs found.")
        else:
            pagination_df = pd.DataFrame(all_page_rows)
            st.markdown("---")
            st.subheader("Pagination Information")
            st.write("**Page URLs:**")
            st.dataframe(pagination_df, use_container_width=True)
        if "in_tokens_p" in st.session_state:
            st.sidebar.markdown("---")
            st.sidebar.markdown("### Pagination Details")
            st.sidebar.markdown(f"**Number of Page URLs:** {len(all_page_rows)}")
            st.sidebar.markdown("#### Pagination Token Usage")
            st.sidebar.markdown(f"*Input Tokens:* {st.session_state['in_tokens_p']}")
            st.sidebar.markdown(f"*Output Tokens:* {st.session_state['out_tokens_p']}")
            st.sidebar.markdown(f"**Total Cost:** ${st.session_state['cost_p']:.4f}")
        st.subheader("Download Pagination URLs")
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("Download Pagination CSV", data=pagination_df.to_csv(index=False), file_name="pagination_urls.csv")
        with col2:
            st.download_button("Download Pagination JSON", data=json.dumps(all_page_rows, indent=4), file_name="pagination_urls.json")
    if st.sidebar.button("Clear Results"):
        st.session_state['scraping_state'] = 'idle'
        st.session_state['results'] = None
    if show_tags and pagination_info:
        st.markdown("---")
        st.markdown("### Total Counts and Cost (Including Pagination)")
        st.markdown(f"**Total Input Tokens:** {total_input_tokens}")
        st.markdown(f"**Total Output Tokens:** {total_output_tokens}")
        st.markdown(f"**Total Combined Cost:** ${total_cost:.4f}")
