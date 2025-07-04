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
- **Service Layer**: Simplified single-file architecture with embedded functions for PDF processing, LLM analysis, and fraud detection
- **Database Layer**: Hybrid approach with in-memory storage for metadata and Qdrant vector database for semantic search
- **Processing Pipeline**: Multi-stage processing with PDF parsing, LLM analysis, and vector embedding with automatic storage in Qdrant

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
- **Embedding Model**: Uses custom 384-dimensional feature vectors with keyword-based and hash-based features
- **Storage**: Qdrant vector database for similarity search and retrieval
- **Metadata Filtering**: Supports filtering by employee, date, status, and fraud indicators
- **Integration**: Automatic storage of processed invoices in Qdrant with semantic search capabilities

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
- July 04, 2025. Implemented complete RAG LLM Chatbot with vector search, metadata filtering, conversation history, and markdown response formatting using Groq API
- July 04, 2025. Fixed duplicate invoice storage issue - implemented comprehensive deduplication logic to prevent storage accumulation
- July 04, 2025. Updated RAG chatbot to use plain text responses instead of markdown formatting for better readability
- July 04, 2025. Cleaned up interface by removing all emojis and sample query prompts for professional appearance
- July 04, 2025. Fixed chatbot date display issue - resolved missing invoice_date field in source data formatting
- July 04, 2025. Integrated Qdrant vector store - implemented full vector database integration with automatic invoice storage, semantic search, and metadata filtering while maintaining simplified architecture
- July 04, 2025. Fixed critical chatbot search bug - enhanced employee name pattern matching and increased search limits to properly return all invoices for specific employees (previously only returning 1 of 3 invoices for Rani, 0 of 2 for Sachin)
- July 04, 2025. Fixed duplicate invoice results in chatbot - implemented deduplication logic to ensure unique results and removed Amount Distribution feature from results view for cleaner interface

## User Preferences

Preferred communication style: Simple, everyday language.