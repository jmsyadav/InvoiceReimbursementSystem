# Invoice Reimbursement System

An intelligent Invoice Reimbursement System that analyzes employee expense claims against company policies using Large Language Models (LLMs). The system provides automated invoice processing, fraud detection, and a conversational chatbot interface for querying processed invoices with vector database integration.

## Features

### Core Functionality
- **Smart Invoice Analysis**: Automatically extracts and analyzes data from PDF invoices against HR reimbursement policies
- **LLM-Powered Decision Making**: Uses Groq API with Llama3-8b-8192 for intelligent policy compliance analysis
- **Vector Database Integration**: Stores analysis results in Qdrant for semantic search and similarity matching
- **RAG-Powered Chatbot**: Natural language querying with conversation history and context awareness
- **Advanced Fraud Detection**: Multi-layered fraud detection including date validation, amount anomalies, and pattern recognition
- **Modern Web Interface**: Clean, professional Streamlit frontend with modular components

### Reimbursement Categories
- **Fully Reimbursed**: Entire invoice amount meets policy requirements
- **Partially Reimbursed**: Only a portion meets policy requirements (with calculated reimbursable amounts)
- **Declined**: Invoice does not meet policy requirements or contains fraudulent elements

### Fraud Detection Features
- **Impossible Travel Detection**: Identifies inconsistent arrival/departure dates in travel invoices
- **Suspicious Journey Duration**: Flags unusually long travel periods exceeding reasonable limits
- **Date Validation**: Checks for expired invoices and chronological inconsistencies
- **Amount Anomaly Detection**: Identifies suspicious amounts based on expense category limits

## Architecture

### Backend (FastAPI)
- **Single-File Architecture**: Streamlined `backend/simple_main.py` with all core functionality
- **Invoice Processing Pipeline**: Multi-stage processing with PDF parsing, LLM analysis, and vector embedding
- **Vector Database**: Qdrant integration for semantic search with metadata filtering
- **In-Memory Storage**: Efficient temporary storage for processed invoice data
- **RESTful API**: Clean endpoints for invoice analysis, chatbot queries, and data retrieval

### Frontend (Streamlit)
- **Modular Component Design**: Separate components for upload, results, and chatbot functionality
- **Interactive Dashboard**: Real-time analytics with filtering and visualization
- **Conversational Interface**: Chat-based querying with source attribution
- **Professional UI**: Clean interface without emojis, focused on business use

## Tech Stack

### Core Technologies
- **Python 3.11**: Primary programming language
- **FastAPI**: High-performance REST API framework
- **Streamlit**: Interactive web application framework
- **Groq API**: Fast LLM inference with Llama3-8b-8192 model
- **Qdrant**: Vector database for semantic search
- **pdfplumber**: PDF text extraction and processing

### Key Libraries
- **uvicorn**: ASGI server for FastAPI
- **pandas**: Data manipulation and analysis
- **plotly**: Interactive data visualizations
- **python-multipart**: File upload handling
- **qdrant-client**: Vector database client

### Development Features
- **Modular Architecture**: Clean separation of concerns
- **In-Memory Storage**: Efficient temporary data handling
- **Vector Embeddings**: Custom 384-dimensional feature vectors
- **RAG Pipeline**: Retrieval-Augmented Generation for chatbot
- **Streaming Interface**: Real-time processing feedback

## Installation

### Prerequisites
- Python 3.11+
- Required API keys:
  - `GROQ_API_KEY`: Groq API key for LLM processing
  - `QDRANT_API_KEY`: Qdrant API key for vector database
  - `QDRANT_URL`: Qdrant instance URL

### Quick Setup
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install fastapi groq pandas pdfplumber plotly pymongo python-multipart qdrant-client streamlit uvicorn
   ```

3. Set environment variables:
   ```bash
   export GROQ_API_KEY="your_groq_api_key"
   export QDRANT_API_KEY="your_qdrant_api_key"
   export QDRANT_URL="your_qdrant_url"
   ```

4. Start the application:
   ```bash
   # Start backend server
   uvicorn backend.simple_main:app --host 0.0.0.0 --port 8000
   
   # Start frontend (in another terminal)
   streamlit run app.py --server.port 5000
   ```

## Usage

### Processing Invoices
1. Upload an HR reimbursement policy PDF file
2. Upload invoice files (PDF format, supports ZIP archives)
3. The system will automatically:
   - Extract text from PDFs
   - Analyze each invoice against the policy
   - Detect potential fraud
   - Store results in Qdrant vector database

### Querying with Chatbot
- Ask natural language questions about processed invoices
- Examples:
  - "Show me all invoices for John"
  - "What's the total reimbursed amount?"
  - "Find all declined invoices"
  - "Show me invoices with fraud alerts"

### Viewing Results
- Browse all processed invoices with filtering options
- View analytics and fraud detection reports
- Export results for further analysis

## Key Features

### Advanced Analytics
- **Reimbursement Status Distribution**: View breakdown of fully/partially reimbursed vs declined invoices
- **Fraud Detection Dashboard**: Monitor flagged invoices with detailed fraud reasons
- **Employee-wise Analysis**: Track reimbursement patterns by employee
- **Smart Filtering**: Filter by status, employee, fraud alerts, and date ranges

### Intelligent Conversation
- **Context-Aware Responses**: Chatbot maintains conversation history
- **Source Attribution**: All responses include source invoice references
- **Metadata Filtering**: Automatic extraction of filters from natural language queries
- **Semantic Search**: Vector-based similarity matching for relevant results

## Architecture Highlights

### Streamlined Design
- **Single Backend File**: All core functionality in `backend/simple_main.py`
- **Modular Frontend**: Clean component separation for maintainability
- **Efficient Storage**: In-memory processing with vector database persistence
- **Professional Interface**: Clean, business-focused UI without distractions

### Data Flow
1. **PDF Upload** → **Text Extraction** → **LLM Analysis** → **Fraud Detection**
2. **Vector Embedding** → **Qdrant Storage** → **Chatbot Querying** → **Results Display**

## Version Information
- **Last Updated**: July 2025
- **Architecture**: Streamlined single-file backend with modular frontend
- **LLM Model**: Llama3-8b-8192 via Groq API
- **Vector Database**: Qdrant with 384-dimensional embeddings
- **Current Status**: Production-ready with comprehensive testing