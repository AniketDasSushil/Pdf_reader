import streamlit as st
import fitz  # PyMuPDF
import re
import pandas as pd
from collections import defaultdict
import json
from bs4 import BeautifulSoup

# ... [previous code remains unchanged] ...

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
                st.dataframe(df, use_container_width=True)  # Highlighting removed
                
                total_occurrences = df['Total Occurrences'].sum()
                st.metric("Total Occurrences", total_occurrences)

if __name__ == "__main__":
    main()
