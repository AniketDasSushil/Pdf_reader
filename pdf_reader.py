import streamlit as st
import fitz  # PyMuPDF
import re
import pandas as pd
from collections import defaultdict
import json
from bs4 import BeautifulSoup
from typing import Dict, List, Tuple
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def set_page_config():
    st.set_page_config(
        page_title="Advanced PDF/HTML Keyword Search",
        page_icon="🔍",
        layout="wide",
    )

def read_pdf(file) -> str:
    try:
        with fitz.open(stream=file.read(), filetype="pdf") as doc:
            return "\n".join(page.get_text() for page in doc)
    except Exception as e:
        logger.error(f"An error occurred while reading the PDF: {str(e)}")
        st.error(f"An error occurred while reading the PDF: {str(e)}")
        return ""

def read_html(file) -> str:
    try:
        content = file.read().decode('utf-8')
        return BeautifulSoup(content, 'html.parser').get_text()
    except Exception as e:
        logger.error(f"An error occurred while reading the HTML: {str(e)}")
        st.error(f"An error occurred while reading the HTML: {str(e)}")
        return ""

def load_search_terms(file_path: str = 'search_terms.json') -> Dict[str, List[str]]:
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON: {str(e)}")
        st.error(f"Error parsing JSON: {str(e)}")
    except FileNotFoundError:
        logger.error(f"{file_path} file not found")
        st.error(f"{file_path} file not found")
    return {}

def search_keywords(content: str, search_terms: Dict[str, List[str]]) -> Dict[str, Dict[str, int]]:
    results = defaultdict(lambda: defaultdict(int))
    content_lower = content.lower()
    
    for main_term, alternatives in search_terms.items():
        for term in alternatives:
            count = len(re.findall(r'\b' + re.escape(term.lower()) + r'\b', content_lower))
            if count > 0:
                results[main_term][term] = count
    
    return results

def create_results_dataframe(results: Dict[str, Dict[str, int]]) -> pd.DataFrame:
    df_data = [
        {
            'Search Term': main_term,
            'Total Occurrences': sum(term_counts.values()),
            'Details': ', '.join(f"{term}: {count}" for term, count in term_counts.items())
        }
        for main_term, term_counts in results.items()
    ]
    return pd.DataFrame(df_data)

def highlight_search_terms(s: pd.Series) -> List[str]:
    return ['background-color: yellow' if s.name == 'Search Term' and s['Total Occurrences'] > 0 else '' for _ in s]

def process_file(file) -> Tuple[str, Dict[str, Dict[str, int]]]:
    if file.type == "application/pdf":
        content = read_pdf(file)
    elif file.type == "text/html":
        content = read_html(file)
    else:
        st.error("Unsupported file type. Please upload a PDF or HTML file.")
        return "", {}
    
    search_terms = load_search_terms()
    if not search_terms:
        return "", {}
    
    results = search_keywords(content, search_terms)
    return content, results

def main():
    set_page_config()
    
    st.title("🔍 Advanced PDF/HTML Keyword Search")
    
    uploaded_file = st.file_uploader("Choose a PDF or HTML file", type=["pdf", "html"])
    
    if uploaded_file is not None:
        with st.spinner("Reading file and searching keywords..."):
            content, results = process_file(uploaded_file)
            
            if content and results:
                st.success("File successfully read and analyzed!")
                
                df = create_results_dataframe(results)
                
                st.subheader("Search Results:")
                st.dataframe(
                    df.style.apply(highlight_search_terms, axis=1)
                        .highlight_max(axis=0, subset=['Total Occurrences']),
                    use_container_width=True
                )
                
                total_occurrences = df['Total Occurrences'].sum()
                st.metric("Total Occurrences", total_occurrences)
                
                if st.checkbox("Show processed content"):
                    st.text_area("Processed Content", content, height=300)

if __name__ == "__main__":
    main()
