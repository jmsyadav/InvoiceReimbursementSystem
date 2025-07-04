# Invoice Reimbursement System

## Overview

This is an intelligent Invoice Reimbursement System that analyzes employee expense claims against company policies using Large Language Models (LLMs). The system provides automated invoice processing, fraud detection, and a conversational chatbot interface for querying processed invoices.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit for web interface
- **Components**: Modular component structure with upload, results, and chatbot sections
- **State Management**: Session-based state management for processed invoices and chat history
- **API Communication**: RESTful API client for backend communication

### Backend Architecture
- **Framework**: FastAPI for REST API endpoints
- **Service Layer**: Modular services for PDF processing, LLM analysis, vector operations, and fraud detection
- **Database Layer**: Dual database approach with MongoDB for metadata and Qdrant for vector storage
- **Processing Pipeline**: Multi-stage processing with PDF parsing, LLM analysis, and vector embedding

### LLM Integration
- **Provider**: Groq API for fast inference
- **Model**: Llama3-8b-8192 for cost-effective processing
- **Use Cases**: Invoice analysis, fraud detection, and conversational querying

## Key Components

### PDF Processing Service
- **PDF Parser**: Extracts text from PDF documents using pdfplumber and PyPDF2
- **Data Extraction**: Structured data extraction for employee names, dates, amounts, and invoice types
- **Multi-format Support**: Handles various PDF formats and layouts

### LLM Analysis Service
- **Policy Comparison**: Analyzes invoices against HR reimbursement policies
- **Status Classification**: Categorizes invoices as Fully Reimbursed, Partially Reimbursed, or Declined
- **Reasoning**: Provides detailed explanations for reimbursement decisions

### Fraud Detection Service
- **Date Validation**: Checks for inconsistent reporting and dropping dates in travel invoices
- **Amount Anomalies**: Identifies suspicious amounts and patterns
- **Missing Information**: Detects invoices with incomplete required fields
- **Pattern Recognition**: Identifies potentially fraudulent behavior patterns

### Vector Database Service
- **Embedding Model**: Uses sentence-transformers (all-MiniLM-L6-v2) for efficient embeddings
- **Storage**: Qdrant vector database for similarity search and retrieval
- **Metadata Filtering**: Supports filtering by employee, date, status, and fraud indicators

### Chatbot Service
- **RAG Implementation**: Retrieval-Augmented Generation for accurate responses
- **Natural Language Processing**: Understands queries about invoices, employees, and policies
- **Context Awareness**: Maintains conversation history and provides relevant answers

## Data Flow

1. **Invoice Upload**: Users upload HR policy PDF and invoice ZIP files through Streamlit frontend
2. **PDF Processing**: Backend extracts text and structured data from all uploaded documents
3. **LLM Analysis**: Each invoice is analyzed against the policy using Groq API
4. **Fraud Detection**: Parallel fraud detection analysis for suspicious patterns
5. **Vector Storage**: Analysis results are embedded and stored in Qdrant with metadata
6. **Metadata Storage**: Structured data is stored in MongoDB for quick filtering
7. **User Interface**: Results are displayed in the frontend with filtering and analytics
8. **Chatbot Queries**: Users can ask natural language questions about processed invoices

## External Dependencies

### Required APIs
- **Groq API**: For LLM inference and analysis
- **Qdrant Cloud**: Vector database for similarity search
- **MongoDB**: Document database for metadata storage

### Python Libraries
- **FastAPI**: Backend web framework
- **Streamlit**: Frontend web application
- **pdfplumber/PyPDF2**: PDF text extraction
- **sentence-transformers**: Text embeddings
- **pymongo**: MongoDB client
- **qdrant-client**: Vector database client
- **groq**: LLM API client

### Environment Variables
- `GROQ_API_KEY`: API key for Groq LLM service
- `QDRANT_API_KEY`: API key for Qdrant vector database
- `QDRANT_URL`: Qdrant instance URL
- `MONGODB_URL`: MongoDB connection string

## Deployment Strategy

### Development Environment
- **Local Development**: Both frontend and backend run locally
- **Port Configuration**: Backend on port 8000, frontend on default Streamlit port
- **Threading**: Backend starts in separate thread from frontend

### Production Considerations
- **Containerization**: Docker support for consistent deployment
- **Scalability**: Separate frontend and backend services
- **Database Hosting**: Cloud-hosted MongoDB and Qdrant instances
- **Load Balancing**: Multiple backend instances for high availability

### Security Measures
- **API Key Management**: Environment variable-based configuration
- **CORS Configuration**: Properly configured cross-origin requests
- **Input Validation**: Comprehensive file type and size validation
- **Error Handling**: Graceful error handling and user feedback

## Changelog

- July 04, 2025. Initial setup
- July 04, 2025. Fixed critical fraud detection bug - improved travel date validation to properly identify impossible travel dates while allowing legitimate travel scenarios

## User Preferences

Preferred communication style: Simple, everyday language.