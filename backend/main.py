from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import os
import zipfile
import tempfile
import shutil
from pydantic import BaseModel
import uvicorn

from .models import InvoiceAnalysisResponse, ChatbotResponse, ChatbotRequest
from .services.pdf_parser import PDFParser
from .services.llm_service import LLMService
from .services.vector_service import VectorService
from .services.fraud_detector import FraudDetector
from .services.chatbot_service import ChatbotService
from .database.qdrant_client import QdrantClient
from .database.mongodb_client import MongoDBClient

app = FastAPI(title="Invoice Reimbursement System API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
pdf_parser = PDFParser()
llm_service = LLMService()
vector_service = VectorService()
fraud_detector = FraudDetector()
chatbot_service = ChatbotService()
qdrant_client = QdrantClient()
mongodb_client = MongoDBClient()

@app.on_event("startup")
async def startup_event():
    """Initialize database connections and vector store"""
    await qdrant_client.initialize()
    await mongodb_client.initialize()
    await vector_service.initialize()

@app.get("/")
async def root():
    return {"message": "Invoice Reimbursement System API is running"}

@app.post("/analyze-invoices", response_model=InvoiceAnalysisResponse)
async def analyze_invoices(
    policy_file: UploadFile = File(...),
    invoice_files: List[UploadFile] = File(...)
):
    """
    Analyze invoices against HR reimbursement policy
    
    Args:
        policy_file: PDF file containing HR reimbursement policy
        invoice_files: List of ZIP files containing employee invoice PDFs
    
    Returns:
        InvoiceAnalysisResponse with analysis results
    """
    try:
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save and parse policy file
            policy_path = os.path.join(temp_dir, "policy.pdf")
            with open(policy_path, "wb") as f:
                shutil.copyfileobj(policy_file.file, f)
            
            policy_text = pdf_parser.extract_text_from_pdf(policy_path)
            
            # Process each invoice file (ZIP or PDF)
            processed_invoices = []
            
            for invoice_file in invoice_files:
                if invoice_file.filename.endswith('.zip'):
                    # Handle ZIP file
                    zip_path = os.path.join(temp_dir, invoice_file.filename)
                    with open(zip_path, "wb") as f:
                        shutil.copyfileobj(invoice_file.file, f)
                    
                    # Extract ZIP file
                    extract_dir = os.path.join(temp_dir, "extracted")
                    os.makedirs(extract_dir, exist_ok=True)
                    
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(extract_dir)
                    
                    # Process each PDF in the ZIP
                    for root, dirs, files in os.walk(extract_dir):
                        for file in files:
                            if file.endswith('.pdf'):
                                pdf_path = os.path.join(root, file)
                                invoice_result = await process_single_invoice(
                                    pdf_path, policy_text, file
                                )
                                processed_invoices.append(invoice_result)
                
                elif invoice_file.filename.endswith('.pdf'):
                    # Handle single PDF file
                    pdf_path = os.path.join(temp_dir, invoice_file.filename)
                    with open(pdf_path, "wb") as f:
                        shutil.copyfileobj(invoice_file.file, f)
                    
                    invoice_result = await process_single_invoice(
                        pdf_path, policy_text, invoice_file.filename
                    )
                    processed_invoices.append(invoice_result)
            
            # Store results in vector database
            await vector_service.store_analysis_results(processed_invoices)
            
            # Store metadata in MongoDB
            await mongodb_client.store_invoice_metadata(processed_invoices)
            
            return InvoiceAnalysisResponse(
                success=True,
                message=f"Successfully processed {len(processed_invoices)} invoices",
                processed_count=len(processed_invoices),
                results=processed_invoices
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

async def process_single_invoice(pdf_path: str, policy_text: str, filename: str) -> dict:
    """Process a single invoice PDF against the policy"""
    try:
        # Extract text from invoice
        invoice_text = pdf_parser.extract_text_from_pdf(pdf_path)
        
        # Extract structured data from invoice
        invoice_data = pdf_parser.extract_invoice_data(invoice_text)
        
        # Detect fraud (for travel invoices)
        fraud_result = fraud_detector.detect_fraud(invoice_data)
        
        # Analyze invoice against policy using LLM
        analysis_result = await llm_service.analyze_invoice(
            invoice_text, policy_text, invoice_data
        )
        
        # Combine results
        result = {
            "invoice_id": filename,
            "employee_name": invoice_data.get("employee_name", "Unknown"),
            "invoice_date": invoice_data.get("date", "Unknown"),
            "amount": invoice_data.get("amount", 0),
            "reimbursement_status": analysis_result["status"],
            "reason": analysis_result["reason"],
            "fraud_detected": fraud_result["is_fraud"],
            "fraud_reason": fraud_result["reason"],
            "invoice_text": invoice_text,
            "invoice_data": invoice_data
        }
        
        return result
        
    except Exception as e:
        return {
            "invoice_id": filename,
            "employee_name": "Unknown",
            "invoice_date": "Unknown",
            "amount": 0,
            "reimbursement_status": "Error",
            "reason": f"Processing error: {str(e)}",
            "fraud_detected": False,
            "fraud_reason": "",
            "invoice_text": "",
            "invoice_data": {}
        }

@app.post("/chatbot", response_model=ChatbotResponse)
async def chatbot_query(request: ChatbotRequest):
    """
    RAG-powered chatbot for querying invoice data
    
    Args:
        request: ChatbotRequest with user query and optional filters
    
    Returns:
        ChatbotResponse with AI-generated answer
    """
    try:
        # Process query using chatbot service
        response = await chatbot_service.process_query(
            query=request.query,
            filters=request.filters,
            conversation_history=request.conversation_history
        )
        
        return ChatbotResponse(
            success=True,
            response=response["answer"],
            sources=response["sources"],
            conversation_id=response["conversation_id"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chatbot query failed: {str(e)}")

@app.get("/invoices")
async def get_processed_invoices():
    """Get all processed invoices from MongoDB"""
    try:
        invoices = await mongodb_client.get_all_invoices()
        return {"success": True, "invoices": invoices}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve invoices: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
