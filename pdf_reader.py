import streamlit as st
import fitz  # PyMuPDF
import re
import pandas as pd
from collections import defaultdict
import json
from bs4 import BeautifulSoup

def set_page_config():
    st.set_page_config(
        page_title="Advanced PDF/HTML Keyword Search",
        page_icon="🔍",
        layout="wide",
    )

def read_pdf(file):
    try:
        doc = fitz.open(stream=file.read(), filetype="pdf")
        content = []
        for page in doc:
            content.append(page.get_text())
        doc.close()
        return '\n'.join(content)
    except Exception as e:
        st.error(f"An error occurred while reading the PDF: {str(e)}")
        return None

def read_html(file):
    try:
        content = file.read().decode('utf-8')
        soup = BeautifulSoup(content, 'html.parser')
        return soup.get_text()
    except Exception as e:
        st.error(f"An error occurred while reading the HTML: {str(e)}")
        return None

def load_search_terms():
    try:
        with open('search_terms.json', 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        st.error(f"Error parsing JSON: {str(e)}")
        return None
    except FileNotFoundError:
        st.error("search_terms.json file not found")
        return None

def search_keywords(content, search_terms):
    results = defaultdict(lambda: defaultdict(int))
    content_lower = content.lower()
    
    for main_term, alternatives in search_terms.items():
        for term in alternatives:
            count = len(re.findall(r'\b' + re.escape(term.lower()) + r'\b', content_lower))
            results[main_term][term] = count
    
    return results

def create_results_dataframe(results):
    df_data = []
    for main_term, term_counts in results.items():
        total_count = sum(term_counts.values())
        df_data.append({
            'Search Term': main_term,
            'Total Occurrences': total_count,
            'Details': ', '.join([f"{term}: {count}" for term, count in term_counts.items() if count > 0])
        })
    return pd.DataFrame(df_data)

def main():
    set_page_config()
    
    st.title("🔍 Advanced PDF/HTML Keyword Search")
    
    SEARCH_TERMS = load_search_terms()
    
    uploaded_file = st.file_uploader("Choose a PDF or HTML file", type=["pdf", "html"])
    
    if uploaded_file is not None:
        with st.spinner("Reading file and searching keywords..."):
            if uploaded_file.type == "application/pdf":
                content = read_pdf(uploaded_file)
            elif uploaded_file.type == "text/html":
                content = read_html(uploaded_file)
            else:
                st.error("Unsupported file type. Please upload a PDF or HTML file.")
                return
            
            if content:
                st.success("File successfully read and analyzed!")
                
                results = search_keywords(content, SEARCH_TERMS)
                df = create_results_dataframe(results)
                
                st.subheader("Search Results:")
                
                
                total_occurrences = df['Total Occurrences'].sum()
                st.metric("Total Occurrences", total_occurrences)

if __name__ == "__main__":
    main()
