# Invoice Reimbursement System - Setup Guide

## Prerequisites

- Python 3.11+
- API keys for required services (see Environment Variables section)

## Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd invoice-reimbursement-system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements-github.txt
   ```

## Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Required API Keys
GROQ_API_KEY=your_groq_api_key_here
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_URL=your_qdrant_cluster_url_here
MONGODB_URL=your_mongodb_connection_string_here
```

### Getting API Keys

1. **Groq API Key**: 
   - Sign up at [console.groq.com](https://console.groq.com/)
   - Create a new API key

2. **Qdrant**: 
   - Sign up at [cloud.qdrant.io](https://cloud.qdrant.io/)
   - Create a cluster and get API key + URL

3. **MongoDB**: 
   - Sign up at [mongodb.com](https://www.mongodb.com/)
   - Create a cluster and get connection string

## Running the Application

1. **Start the backend server**
   ```bash
   python -m uvicorn backend.simple_main:app --host 0.0.0.0 --port 8000
   ```

2. **Start the frontend (in a new terminal)**
   ```bash
   streamlit run app.py --server.port 5000
   ```

3. **Access the application**
   - Frontend: http://localhost:5000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Usage

1. **Upload Documents**: Upload HR reimbursement policy PDF and invoice ZIP files
2. **View Results**: Review processed invoices with reimbursement status and fraud detection
3. **Query Chatbot**: Ask questions about processed invoices using natural language

## Project Structure

```
invoice-reimbursement-system/
├── app.py                 # Main Streamlit application
├── backend/
│   ├── simple_main.py     # FastAPI backend with all endpoints
│   └── models.py          # Pydantic data models
├── frontend/
│   ├── components/        # Streamlit UI components
│   └── services/          # API client services
├── sample_data/           # Sample invoices and policy files
├── requirements-github.txt # Python dependencies
└── README.md             # Project documentation
```

## Troubleshooting

- **Port conflicts**: Change ports in the run commands if 5000/8000 are in use
- **API errors**: Verify your API keys are correctly set in the `.env` file
- **PDF processing issues**: Ensure uploaded files are valid PDFs
- **Database connection**: Check MongoDB and Qdrant connection strings

## License

This project is for educational and demonstration purposes.