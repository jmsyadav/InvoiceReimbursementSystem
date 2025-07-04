# Invoice Reimbursement System

An intelligent Invoice Reimbursement System that analyzes employee expense claims against company policies using Large Language Models and provides a chatbot interface for querying processed invoices.

## Features

### Core Functionality
- **Invoice Analysis**: Automatically processes PDF invoices against HR reimbursement policies
- **LLM Integration**: Uses Groq API for intelligent analysis and decision-making
- **Vector Database**: Stores analysis results in Qdrant for efficient similarity search
- **RAG-Powered Chatbot**: Natural language querying of processed invoice data
- **Fraud Detection**: Identifies potential fraud in travel invoices through date validation
- **Web Interface**: Clean Streamlit frontend for easy interaction

### Reimbursement Categories
- **Fully Reimbursed**: Entire invoice amount is reimbursable
- **Partially Reimbursed**: Only a portion meets policy requirements
- **Declined**: Invoice does not meet policy requirements

### Fraud Detection
- **Date Validation**: Checks for inconsistent reporting and dropping dates in travel invoices
- **Amount Anomalies**: Identifies unusually high amounts by expense category
- **Missing Fields**: Detects invoices with missing required information

## Architecture

### Backend (FastAPI)
- **Invoice Analysis Endpoint**: Processes PDF invoices and ZIP files
- **Chatbot Endpoint**: RAG-powered natural language querying
- **Vector Storage**: Qdrant integration for similarity search
- **Metadata Storage**: MongoDB for structured invoice data

### Frontend (Streamlit)
- **Upload Interface**: File upload and processing
- **Results Dashboard**: View and filter processed invoices
- **Analytics**: Statistical analysis and visualizations
- **Chatbot Interface**: Conversational querying

## Installation

### Prerequisites
- Python 3.8+
- Environment variables for API keys:
  - `GROQ_API_KEY`: Groq API key for LLM processing
  - `QDRANT_API_KEY`: Qdrant API key for vector database
  - `QDRANT_URL`: Qdrant instance URL
  - `MONGODB_URL`: MongoDB connection string

### Setup
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install fastapi uvicorn streamlit pdfplumber groq qdrant-client pymongo sentence-transformers pandas
   ```

3. Set environment variables:
   ```bash
   export GROQ_API_KEY="your_groq_api_key"
   export QDRANT_API_KEY="your_qdrant_api_key"
   export QDRANT_URL="your_qdrant_url"
   export MONGODB_URL="your_mongodb_url"
   ```

4. Start the backend server:
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port 8000
   