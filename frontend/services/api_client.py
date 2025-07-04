import requests
import streamlit as st
from typing import List, Dict, Any, Optional
import time

class APIClient:
    """Client for interacting with the FastAPI backend"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def _wait_for_backend(self, max_retries: int = 30, delay: float = 1.0):
        """Wait for backend to be ready"""
        for i in range(max_retries):
            try:
                response = self.session.get(f"{self.base_url}/health", timeout=5)
                if response.status_code == 200:
                    return True
            except requests.exceptions.RequestException:
                pass
            
            if i < max_retries - 1:
                time.sleep(delay)
        
        return False
    
    def analyze_invoices(self, policy_file, invoice_files) -> Dict[str, Any]:
        """
        Analyze invoices against policy
        
        Args:
            policy_file: Uploaded policy PDF file
            invoice_files: List of uploaded invoice files
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Wait for backend to be ready
            if not self._wait_for_backend():
                return {"success": False, "message": "Backend service is not available. Please try again later."}
            
            # Prepare files for upload
            files = [
                ("policy_file", (policy_file.name, policy_file.getvalue(), "application/pdf"))
            ]
            
            # Add invoice files
            for invoice_file in invoice_files:
                files.append(("invoice_files", (invoice_file.name, invoice_file.getvalue(), 
                                             "application/pdf" if invoice_file.name.endswith('.pdf') else "application/zip")))
            
            # Make API request
            response = self.session.post(
                f"{self.base_url}/analyze-invoices",
                files=files,
                timeout=300  # 5 minutes timeout for processing
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.headers.get("content-type") == "application/json" else response.text
                return {
                    "success": False,
                    "message": f"API Error ({response.status_code}): {error_detail}"
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "message": "Request timed out. Processing large files may take longer."
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "message": "Cannot connect to backend service. Please ensure the backend is running."
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Unexpected error: {str(e)}"
            }
    
    def query_chatbot(self, query: str, filters: Optional[Dict[str, Any]] = None, 
                     conversation_history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Query the chatbot
        
        Args:
            query: User's question
            filters: Optional filters for the query
            conversation_history: Previous conversation turns
            
        Returns:
            Dictionary with chatbot response
        """
        try:
            # Wait for backend to be ready
            if not self._wait_for_backend():
                return {"success": False, "response": "Backend service is not available. Please try again later."}
            
            # Prepare request payload
            payload = {
                "query": query,
                "filters": filters or {},
                "conversation_history": conversation_history or []
            }
            
            # Make API request
            response = self.session.post(
                f"{self.base_url}/chatbot",
                json=payload,
                timeout=60  # 1 minute timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.headers.get("content-type") == "application/json" else response.text
                return {
                    "success": False,
                    "response": f"API Error ({response.status_code}): {error_detail}",
                    "sources": []
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "response": "Request timed out. Please try a simpler query.",
                "sources": []
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "response": "Cannot connect to backend service. Please ensure the backend is running.",
                "sources": []
            }
        except Exception as e:
            return {
                "success": False,
                "response": f"Unexpected error: {str(e)}",
                "sources": []
            }
    
    def get_invoices(self) -> Dict[str, Any]:
        """
        Get all processed invoices
        
        Returns:
            Dictionary with invoices data
        """
        try:
            # Wait for backend to be ready
            if not self._wait_for_backend():
                return {"success": False, "invoices": []}
            
            # Make API request
            response = self.session.get(f"{self.base_url}/invoices", timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "invoices": [],
                    "message": f"API Error ({response.status_code})"
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "invoices": [],
                "message": "Request timed out"
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "invoices": [],
                "message": "Cannot connect to backend service"
            }
        except Exception as e:
            return {
                "success": False,
                "invoices": [],
                "message": f"Unexpected error: {str(e)}"
            }
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check backend health
        
        Returns:
            Dictionary with health status
        """
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            
            if response.status_code == 200:
                return {"success": True, "status": "healthy"}
            else:
                return {"success": False, "status": "unhealthy", "code": response.status_code}
                
        except Exception as e:
            return {"success": False, "status": "unreachable", "error": str(e)}
