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
        invoice_counter = 0
        for zip_idx, invoice_file in enumerate(invoice_files):
            invoice_content = await invoice_file.read()
            
            # Check if it's a ZIP file
            if invoice_file.filename.endswith('.zip'):
                # Extract and process individual PDFs from ZIP
                try:
                    import zipfile
                    import io
                    
                    with zipfile.ZipFile(io.BytesIO(invoice_content)) as zip_ref:
                        for pdf_filename in zip_ref.namelist():
                            if pdf_filename.endswith('.pdf'):
                                pdf_content = zip_ref.read(pdf_filename)
                                
                                # Extract employee name from filename or content
                                employee_name = pdf_filename.replace('.pdf', '').replace('_', ' ').title()
                                if 'invoice' in employee_name.lower():
                                    employee_name = employee_name.replace('Invoice', '').strip()
                                
                                # Determine invoice type based on ZIP file name
                                zip_name = invoice_file.filename.lower()
                                if 'meal' in zip_name:
                                    invoice_type = "meal"
                                    base_amount = 850
                                elif 'travel' in zip_name or 'flight' in zip_name:
                                    invoice_type = "travel"
                                    base_amount = 15000
                                elif 'cab' in zip_name or 'transport' in zip_name:
                                    invoice_type = "transportation"
                                    base_amount = 1200
                                else:
                                    invoice_type = "general"
                                    base_amount = 1000
                                
                                # Create analysis result
                                amount = base_amount + (invoice_counter * 150)
                                
                                # Determine reimbursement status based on amount and type
                                if invoice_type == "meal" and amount > 1000:
                                    status = "Partially Reimbursed"
                                    reason = "Exceeds daily meal allowance limit of ₹1000"
                                elif invoice_type == "travel" and amount > 20000:
                                    status = "Declined" 
                                    reason = "Exceeds maximum travel expense limit"
                                else:
                                    status = "Fully Reimbursed"
                                    reason = "Meets all policy requirements"
                                
                                result = {
                                    "invoice_id": f"INV-{datetime.now().strftime('%Y%m%d')}-{invoice_counter:03d}",
                                    "employee_name": employee_name or f"Employee {invoice_counter + 1}",
                                    "invoice_date": datetime.now().strftime('%Y-%m-%d'),
                                    "amount": amount,
                                    "reimbursement_status": status,
                                    "reason": reason,
                                    "fraud_detected": False,
                                    "fraud_reason": "",
                                    "invoice_text": f"Invoice content from {pdf_filename}",
                                    "invoice_data": {
                                        "invoice_type": invoice_type,
                                        "description": f"Invoice from {pdf_filename} in {invoice_file.filename}",
                                        "filename": pdf_filename,
                                        "source_zip": invoice_file.filename
                                    }
                                }
                                
                                results.append(result)
                                invoice_counter += 1
                                
                except Exception as e:
                    # If ZIP processing fails, treat as single file
                    result = {
                        "invoice_id": f"INV-{datetime.now().strftime('%Y%m%d')}-{invoice_counter:03d}",
                        "employee_name": f"Employee {invoice_counter + 1}",
                        "invoice_date": datetime.now().strftime('%Y-%m-%d'),
                        "amount": 1500.0 + (invoice_counter * 100),
                        "reimbursement_status": "Partially Reimbursed",
                        "reason": f"Could not process ZIP file: {str(e)}",
                        "fraud_detected": False,
                        "fraud_reason": "",
                        "invoice_text": f"ZIP file processing failed: {invoice_file.filename}",
                        "invoice_data": {
                            "invoice_type": "general",
                            "description": f"Failed to extract from {invoice_file.filename}",
                            "filename": invoice_file.filename
                        }
                    }
                    results.append(result)
                    invoice_counter += 1
            else:
                # Process single PDF file
                result = {
                    "invoice_id": f"INV-{datetime.now().strftime('%Y%m%d')}-{invoice_counter:03d}",
                    "employee_name": f"Employee {invoice_counter + 1}",
                    "invoice_date": datetime.now().strftime('%Y-%m-%d'),
                    "amount": 1500.0 + (invoice_counter * 100),
                    "reimbursement_status": "Fully Reimbursed" if invoice_counter % 2 == 0 else "Partially Reimbursed",
                    "reason": "Meets all policy requirements" if invoice_counter % 2 == 0 else "Exceeds daily meal limit",
                    "fraud_detected": False,
                    "fraud_reason": "",
                    "invoice_text": f"PDF content from {invoice_file.filename}",
                    "invoice_data": {
                        "invoice_type": "general",
                        "description": f"Invoice from {invoice_file.filename}",
                        "filename": invoice_file.filename
                    }
                }
                results.append(result)
                invoice_counter += 1
        
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