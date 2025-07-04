import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from frontend.components.upload_component import render_upload_section
from frontend.components.results_component import render_results_section
from frontend.components.chatbot_component import render_chatbot_section
from frontend.services.api_client import APIClient
import subprocess
import threading
import time

def start_backend():
    """Start the FastAPI backend server in a separate thread"""
    try:
        subprocess.run(["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"], 
                      check=True, capture_output=True)
    except Exception as e:
        st.error(f"Failed to start backend: {e}")

def main():
    st.set_page_config(
        page_title="Invoice Reimbursement System",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize API client
    if 'api_client' not in st.session_state:
        st.session_state.api_client = APIClient()
    
    # Initialize session state
    if 'processed_invoices' not in st.session_state:
        st.session_state.processed_invoices = []
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Start backend server in a separate thread (non-blocking)
    if 'backend_started' not in st.session_state:
        backend_thread = threading.Thread(target=start_backend, daemon=True)
        backend_thread.start()
        st.session_state.backend_started = True
        time.sleep(2)  # Give backend time to start
    
    # Main title
    st.title("📄 Invoice Reimbursement System")
    st.markdown("---")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Choose a section:",
        ["Upload & Process", "View Results", "Chatbot Query"]
    )
    
    # Main content area
    if page == "Upload & Process":
        render_upload_section()
    elif page == "View Results":
        render_results_section()
    elif page == "Chatbot Query":
        render_chatbot_section()
    
    # Footer
    st.markdown("---")
    st.markdown("*Invoice Reimbursement System powered by AI*")

if __name__ == "__main__":
    main()
