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
        # Use Popen instead of run for non-blocking execution
        process = subprocess.Popen(
            ["python", "-m", "uvicorn", "backend.simple_main:app", "--host", "0.0.0.0", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a bit to check if process started successfully
        time.sleep(3)
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            print(f"Backend failed to start: {stderr}")
        else:
            print("Backend server started successfully")
            
    except Exception as e:
        print(f"Failed to start backend: {e}")

def main():
    st.set_page_config(
        page_title="Invoice Reimbursement System",
        page_icon="",
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
    
    
    is_cloud = os.getenv("STREAMLIT_ENV") == "cloud" or os.getenv("PORT") == "8501"
    cloud_env = is_cloud or os.getenv("DISABLE_BACKEND") == "1"
    if not cloud_env and 'backend_started' not in st.session_state:
        backend_thread = threading.Thread(target=start_backend, daemon=True)
        backend_thread.start()
        st.session_state.backend_started = True
        time.sleep(2)  # Give backend time to start
    
    # Main title
    st.title("Invoice Reimbursement System")
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

if __name__ == "__main__":
    main()
