from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class InvoiceData(BaseModel):
    """Model for structured invoice data"""
    employee_name: Optional[str] = None
    date: Optional[str] = None
    amount: Optional[float] = None
    invoice_type: Optional[str] = None
    description: Optional[str] = None
    reporting_date: Optional[str] = None
    dropping_date: Optional[str] = None

class InvoiceAnalysisResult(BaseModel):
    """Model for individual invoice analysis result"""
    invoice_id: str
    employee_name: str
    invoice_date: str
    amount: float
    reimbursement_status: str
    reason: str
    fraud_detected: bool
    fraud_reason: str
    invoice_text: str
    invoice_data: Dict[str, Any]

class InvoiceAnalysisResponse(BaseModel):
    """Response model for invoice analysis endpoint"""
    success: bool
    message: str
    processed_count: int
    results: List[InvoiceAnalysisResult]

class ChatbotRequest(BaseModel):
    """Request model for chatbot endpoint"""
    query: str
    filters: Optional[Dict[str, Any]] = None
    conversation_history: Optional[List[Dict[str, str]]] = None

class ChatbotResponse(BaseModel):
    """Response model for chatbot endpoint"""
    success: bool
    response: str
    sources: List[Dict[str, Any]]
    conversation_id: str

class VectorSearchRequest(BaseModel):
    """Request model for vector search"""
    query: str
    filters: Optional[Dict[str, Any]] = None
    limit: int = 10

class VectorSearchResult(BaseModel):
    """Result model for vector search"""
    id: str
    score: float
    metadata: Dict[str, Any]
    content: str
