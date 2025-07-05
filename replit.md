# Invoice Reimbursement System

## Overview

The Invoice Reimbursement System is an intelligent application that automates the analysis of employee expense claims against company policies using Large Language Models (LLMs). The system leverages AI to process PDF invoices, detect fraud, and provide automated reimbursement decisions through a modern web interface.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit-based web application with component-based architecture
- **Structure**: Modular design with separate components for upload, results, and chatbot functionality
- **UI Philosophy**: Clean, professional interface focused on business use without excessive visual elements
- **Main Entry Point**: `app.py` orchestrates the entire frontend experience

### Backend Architecture
- **Framework**: FastAPI single-file architecture in `backend/simple_main.py`
- **Design Pattern**: Streamlined monolithic approach with all core functionality in one file
- **API Design**: RESTful endpoints for invoice analysis, chatbot queries, and data retrieval
- **Storage**: In-memory storage for processed invoice data with vector database integration

### Data Processing Pipeline
1. **PDF Processing**: Extract text from policy documents and invoices using pdfplumber
2. **LLM Analysis**: Analyze invoices against policies using Groq API with Llama3-8b-8192 model
3. **Vector Embedding**: Store analysis results in Qdrant vector database for semantic search
4. **Fraud Detection**: Multi-layered fraud detection including date validation and pattern recognition

## Key Components

### Core Services
- **Invoice Analysis Engine**: Processes PDF invoices and compares against HR policies
- **Fraud Detection System**: Identifies suspicious patterns including impossible travel, date inconsistencies, and amount anomalies
- **Vector Search**: Semantic search capabilities using Qdrant for intelligent querying
- **RAG Chatbot**: Conversational interface with context awareness and source attribution

### Data Models
- **InvoiceData**: Structured invoice information extraction
- **InvoiceAnalysisResult**: Comprehensive analysis results with fraud detection
- **ChatbotRequest/Response**: Conversational AI interface models
- **VectorSearchRequest**: Semantic search functionality

### Reimbursement Categories
- **Fully Reimbursed**: Complete invoice amount approved
- **Partially Reimbursed**: Portion of invoice approved with calculated amounts
- **Declined**: Invoice rejected due to policy violations or fraud detection

## Data Flow

1. **Upload Phase**: Users upload HR policy PDF and employee invoice files (ZIP or individual PDFs)
2. **Processing Phase**: Backend extracts text, analyzes against policies using LLM, and stores results
3. **Analysis Phase**: System categorizes invoices and detects potential fraud
4. **Storage Phase**: Results stored in vector database for semantic search
5. **Query Phase**: Users interact through chatbot or view results in dashboard

## External Dependencies

### Required API Services
- **Groq API**: LLM inference using Llama3-8b-8192 model for policy analysis
- **Qdrant Cloud**: Vector database for semantic search and similarity matching
- **MongoDB**: Document storage (configured but not actively used in current implementation)

### Python Libraries
- **FastAPI**: High-performance web framework for API endpoints
- **Streamlit**: Interactive web application framework
- **pdfplumber**: PDF text extraction and processing
- **qdrant-client**: Vector database client for semantic search
- **requests**: HTTP client for API communication

## Deployment Strategy

### Local Development
- **Backend**: FastAPI server runs on localhost:8000 with uvicorn
- **Frontend**: Streamlit application auto-starts backend server
- **Environment**: Python 3.11+ with virtual environment setup

### Configuration Management
- **Environment Variables**: Centralized configuration via .env file
- **API Keys**: Secure storage of Groq, Qdrant, and MongoDB credentials
- **CORS**: Cross-origin resource sharing enabled for frontend-backend communication

### Scalability Considerations
- **Single-file backend**: Simplified deployment but may require refactoring for scale
- **Vector database**: Qdrant provides horizontal scaling capabilities
- **In-memory storage**: Current limitation that may require database persistence for production

## Changelog

- July 05, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.