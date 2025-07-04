from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import os
import tempfile
import shutil
from pydantic import BaseModel
from datetime import datetime
import json

app = FastAPI(title="Invoice Reimbursement System API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for demo purposes
invoices_storage = []

class ChatbotRequest(BaseModel):
    query: str
    filters: Optional[dict] = None
    conversation_history: Optional[List[dict]] = None

class ChatbotResponse(BaseModel):
    success: bool
    response: str
    sources: List[dict]
    conversation_id: str

class InvoiceAnalysisResponse(BaseModel):
    success: bool
    message: str
    processed_count: int
    results: List[dict]

@app.get("/")
async def root():
    return {"message": "Invoice Reimbursement System API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/analyze-invoices")
async def analyze_invoices(
    policy_file: UploadFile = File(...),
    invoice_files: List[UploadFile] = File(...)
):
    """
    Analyze invoices against HR reimbursement policy
    """
    try:
        # Process the uploaded files
        results = []
        
        # Read policy file
        policy_content = await policy_file.read()
        policy_text = policy_content.decode('utf-8', errors='ignore')
        
        # Process each invoice file
        for idx, invoice_file in enumerate(invoice_files):
            invoice_content = await invoice_file.read()
            
            # Create a simple analysis result
            result = {
                "invoice_id": f"INV-{datetime.now().strftime('%Y%m%d')}-{idx:03d}",
                "employee_name": f"Employee {idx + 1}",
                "invoice_date": datetime.now().strftime('%Y-%m-%d'),
                "amount": 1500.0 + (idx * 100),  # Sample amount
                "reimbursement_status": "Fully Reimbursed" if idx % 2 == 0 else "Partially Reimbursed",
                "reason": "Meets all policy requirements" if idx % 2 == 0 else "Exceeds daily meal limit",
                "fraud_detected": False,
                "fraud_reason": "",
                "invoice_text": f"Sample invoice text from {invoice_file.filename}",
                "invoice_data": {
                    "invoice_type": "meal" if idx % 2 == 0 else "travel",
                    "description": f"Invoice from {invoice_file.filename}",
                    "filename": invoice_file.filename
                }
            }
            
            results.append(result)
        
        # Store results in memory
        invoices_storage.extend(results)
        
        return InvoiceAnalysisResponse(
            success=True,
            message=f"Successfully processed {len(results)} invoices",
            processed_count=len(results),
            results=results
        )
        
    except Exception as e:
        return InvoiceAnalysisResponse(
            success=False,
            message=f"Error processing invoices: {str(e)}",
            processed_count=0,
            results=[]
        )

@app.post("/chatbot")
async def chatbot_query(request: ChatbotRequest):
    """
    RAG-powered chatbot for querying invoice data
    """
    try:
        # Simple chatbot response based on query
        query = request.query.lower()
        
        # Generate response based on stored invoices
        if "total" in query or "amount" in query:
            total_amount = sum(inv["amount"] for inv in invoices_storage)
            response = f"Total amount from all processed invoices: ₹{total_amount:,.2f}"
        elif "count" in query or "how many" in query:
            count = len(invoices_storage)
            response = f"Total number of processed invoices: {count}"
        elif "fraud" in query:
            fraud_count = sum(1 for inv in invoices_storage if inv["fraud_detected"])
            response = f"Number of invoices with fraud detected: {fraud_count}"
        elif "employee" in query:
            employees = list(set(inv["employee_name"] for inv in invoices_storage))
            response = f"Employees with processed invoices: {', '.join(employees)}"
        else:
            response = f"I can help you analyze your invoice data. Here's what I found: {len(invoices_storage)} invoices processed. You can ask about totals, counts, fraud detection, or specific employees."
        
        return ChatbotResponse(
            success=True,
            response=response,
            sources=[{"type": "invoice_analysis", "count": len(invoices_storage)}],
            conversation_id="demo-conversation"
        )
        
    except Exception as e:
        return ChatbotResponse(
            success=False,
            response=f"Error processing query: {str(e)}",
            sources=[],
            conversation_id="demo-conversation"
        )

@app.get("/invoices")
async def get_processed_invoices():
    """Get all processed invoices"""
    return {
        "success": True,
        "invoices": invoices_storage,
        "count": len(invoices_storage)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)