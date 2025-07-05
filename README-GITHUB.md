# Invoice Reimbursement System

An intelligent Invoice Reimbursement System that analyzes employee expense claims against company policies using Large Language Models (LLMs). The system provides automated invoice processing, fraud detection, and a conversational chatbot interface for querying processed invoices.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)

## 🚀 Features

### Core Functionality
- **📄 PDF Processing**: Extract and analyze invoice data from PDF documents
- **🔍 Policy Analysis**: Compare invoices against HR reimbursement policies using LLM
- **🚨 Fraud Detection**: Identify suspicious patterns, date inconsistencies, and policy violations
- **💰 Reimbursement Classification**: Categorize invoices as Fully Reimbursed, Partially Reimbursed, or Declined
- **🤖 RAG Chatbot**: Query processed invoices using natural language with vector search

### Technical Capabilities
- **📱 Multi-format Support**: Process various PDF invoice formats and layouts
- **🔍 Vector Database**: Semantic search using Qdrant for intelligent query responses
- **🧠 LLM Integration**: Groq API with Llama3-8b-8192 for cost-effective analysis
- **⚡ Real-time Processing**: Streamlit frontend with FastAPI backend
- **🔄 Session Management**: Automatic data clearing between processing sessions

## 🛠 Tech Stack

- **Frontend**: Streamlit for interactive web interface
- **Backend**: FastAPI for REST API endpoints
- **LLM**: Groq API (Llama3-8b-8192) for invoice analysis and fraud detection
- **Vector Database**: Qdrant for semantic search and RAG implementation
- **Document Processing**: pdfplumber for PDF text extraction
- **Data Storage**: In-memory storage with Qdrant vector indexing

## 📦 Installation

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd invoice-reimbursement-system
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements-github.txt
   ```

3. **Set up environment variables** (see [SETUP.md](SETUP.md) for details)
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Run the application**
   ```bash
   # Start backend
   python -m uvicorn backend.simple_main:app --host 0.0.0.0 --port 8000

   # Start frontend (in new terminal)
   streamlit run app.py --server.port 5000
   ```

For detailed setup instructions, see [SETUP.md](SETUP.md).

## 🎯 Usage

1. **Upload Policy**: Upload your HR reimbursement policy PDF
2. **Upload Invoices**: Upload ZIP files containing invoice PDFs
3. **Review Results**: View processed invoices with status and fraud detection
4. **Query System**: Use the chatbot to ask questions about invoices

### Sample Queries
- "What is the total reimbursed amount?"
- "Show me all declined invoices"
- "Which employees have fraud cases?"
- "List all travel expenses over ₹5000"

## 📁 Project Structure

```
invoice-reimbursement-system/
├── app.py                    # Main Streamlit application
├── backend/
│   ├── simple_main.py       # FastAPI backend with all endpoints
│   └── models.py            # Pydantic data models
├── frontend/
│   ├── components/          # Streamlit UI components
│   │   ├── chatbot_component.py
│   │   ├── results_component.py
│   │   └── upload_component.py
│   └── services/
│       └── api_client.py    # Backend API communication
├── sample_data/             # Sample files for testing
├── requirements-github.txt  # Python dependencies
├── SETUP.md                # Detailed setup instructions
└── README.md               # This file
```

## 🔧 Key Features

### Invoice Processing
- Automatic employee name extraction from PDFs
- Invoice type detection (meal, travel, cab)
- Amount extraction and validation
- Date validation for fraud detection

### Fraud Detection
- Impossible travel date validation
- Suspicious journey duration checks
- Invoice age verification
- Amount anomaly detection

### Chatbot Capabilities
- Natural language query processing
- Vector similarity search
- Conversation history tracking
- Source citation for responses

## 🔄 Data Flow

1. PDF text extraction using pdfplumber
2. LLM analysis against policy using Groq API
3. Fraud detection with rule-based validation
4. Vector embedding and storage in Qdrant
5. RAG-powered chatbot responses with semantic search

## 🛡️ Security & Environment

- Environment variables for API key management
- Session isolation for data security
- No persistent storage of sensitive data
- Comprehensive input validation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📋 Requirements

- Python 3.11+
- API keys for Groq and Qdrant services
- See `requirements-github.txt` for full dependency list

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [Detailed Setup Guide](SETUP.md)
- [Sample Data](sample_data/)
- [API Documentation](http://localhost:8000/docs) (when running)

## ⚡ Performance

- Supports processing multiple invoices simultaneously
- Optimized vector search with Qdrant
- Session-based memory management
- Fallback mechanisms for robust operation