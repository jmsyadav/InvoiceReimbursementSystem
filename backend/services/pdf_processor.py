"""
PDF processing service for extracting text from PDF documents
"""

import os
import re
from typing import Optional, Dict, Any
import PyPDF2
import pdfplumber
from io import BytesIO

class PDFProcessor:
    """Service for processing PDF documents and extracting text"""
    
    def __init__(self):
        self.supported_formats = ['.pdf']
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file using multiple methods for better accuracy
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text content
        """
        try:
            # Try pdfplumber first (better for structured documents)
            text = self._extract_with_pdfplumber(pdf_path)
            
            # If pdfplumber fails or returns empty, try PyPDF2
            if not text.strip():
                text = self._extract_with_pypdf2(pdf_path)
            
            # Clean and normalize the text
            text = self._clean_text(text)
            
            return text
            
        except Exception as e:
            print(f"❌ Error extracting text from {pdf_path}: {e}")
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
    
    def _extract_with_pdfplumber(self, pdf_path: str) -> str:
        """Extract text using pdfplumber (better for tables and structured data)"""
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except Exception as e:
            print(f"⚠️ pdfplumber extraction failed: {e}")
            return ""
    
    def _extract_with_pypdf2(self, pdf_path: str) -> str:
        """Extract text using PyPDF2 (fallback method)"""
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except Exception as e:
            print(f"⚠️ PyPDF2 extraction failed: {e}")
            return ""
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that might cause issues
        text = re.sub(r'[^\w\s\-.,;:!?()₹$@#%&*+=<>\/\\"\']', ' ', text)
        
        # Normalize currency symbols
        text = re.sub(r'[₹$]', '₹', text)
        
        # Remove extra spaces
        text = ' '.join(text.split())
        
        return text.strip()
    
    def extract_text_from_bytes(self, pdf_bytes: bytes) -> str:
        """
        Extract text from PDF bytes
        
        Args:
            pdf_bytes: PDF file content as bytes
            
        Returns:
            Extracted text content
        """
        try:
            # Try pdfplumber first
            text = self._extract_with_pdfplumber_bytes(pdf_bytes)
            
            # If pdfplumber fails, try PyPDF2
            if not text.strip():
                text = self._extract_with_pypdf2_bytes(pdf_bytes)
            
            # Clean and normalize the text
            text = self._clean_text(text)
            
            return text
            
        except Exception as e:
            print(f"❌ Error extracting text from PDF bytes: {e}")
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
    
    def _extract_with_pdfplumber_bytes(self, pdf_bytes: bytes) -> str:
        """Extract text from PDF bytes using pdfplumber"""
        try:
            text = ""
            with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except Exception as e:
            print(f"⚠️ pdfplumber bytes extraction failed: {e}")
            return ""
    
    def _extract_with_pypdf2_bytes(self, pdf_bytes: bytes) -> str:
        """Extract text from PDF bytes using PyPDF2"""
        try:
            text = ""
            pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text
        except Exception as e:
            print(f"⚠️ PyPDF2 bytes extraction failed: {e}")
            return ""
    
    def validate_pdf(self, pdf_path: str) -> bool:
        """
        Validate if a file is a valid PDF
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            True if valid PDF, False otherwise
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                return len(pdf_reader.pages) > 0
        except Exception:
            return False
    
    def get_pdf_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract metadata from PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing PDF metadata
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                metadata = pdf_reader.metadata
                
                return {
                    'title': getattr(metadata, 'title', None),
                    'author': getattr(metadata, 'author', None),
                    'subject': getattr(metadata, 'subject', None),
                    'creator': getattr(metadata, 'creator', None),
                    'producer': getattr(metadata, 'producer', None),
                    'creation_date': getattr(metadata, 'creation_date', None),
                    'modification_date': getattr(metadata, 'modification_date', None),
                    'page_count': len(pdf_reader.pages)
                }
        except Exception as e:
            print(f"⚠️ Error extracting PDF metadata: {e}")
            return {}
