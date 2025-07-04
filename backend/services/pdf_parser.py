import pdfplumber
import re
from typing import Dict, Any, Optional
from ..utils.employee_extractor import EmployeeExtractor
from ..utils.date_parser import DateParser

class PDFParser:
    """Service for parsing PDF documents and extracting structured data"""
    
    def __init__(self):
        self.employee_extractor = EmployeeExtractor()
        self.date_parser = DateParser()
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text content from PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text content
        """
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def extract_invoice_data(self, text: str) -> Dict[str, Any]:
        """
        Extract structured data from invoice text
        
        Args:
            text: Raw text content from invoice
            
        Returns:
            Dictionary containing extracted invoice data
        """
        try:
            data = {}
            
            # Extract employee name using multiple strategies
            data["employee_name"] = self.employee_extractor.extract_employee_name(text)
            
            # Extract dates
            dates = self.date_parser.extract_dates(text)
            data["date"] = dates.get("primary_date")
            data["reporting_date"] = dates.get("reporting_date")
            data["dropping_date"] = dates.get("dropping_date")
            
            # Extract amount
            data["amount"] = self._extract_amount(text)
            
            # Determine invoice type
            data["invoice_type"] = self._determine_invoice_type(text)
            
            # Extract description
            data["description"] = self._extract_description(text)
            
            # Extract additional fields based on invoice type
            if data["invoice_type"] == "travel":
                data.update(self._extract_travel_details(text))
            elif data["invoice_type"] == "meal":
                data.update(self._extract_meal_details(text))
            elif data["invoice_type"] == "cab":
                data.update(self._extract_cab_details(text))
            
            return data
            
        except Exception as e:
            return {"error": f"Failed to extract invoice data: {str(e)}"}
    
    def _extract_amount(self, text: str) -> Optional[float]:
        """Extract monetary amount from text"""
        # Look for various currency patterns
        patterns = [
            r'Total[:\s]+₹\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'Net amount[:\s]+₹\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'₹\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'Total[:\s]+\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'Amount[:\s]+₹\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'Fare[:\s]+₹\s*(\d+(?:,\d{3})*(?:\.\d{2})?)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Clean and convert to float
                amount_str = matches[0].replace(',', '')
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        
        return None
    
    def _determine_invoice_type(self, text: str) -> str:
        """Determine the type of invoice based on content"""
        text_lower = text.lower()
        
        # Travel keywords
        travel_keywords = ['ticket', 'boarding', 'journey', 'passenger', 'seat', 'departure', 'arrival']
        if any(keyword in text_lower for keyword in travel_keywords):
            return "travel"
        
        # Meal keywords
        meal_keywords = ['restaurant', 'meal', 'food', 'coffee', 'lunch', 'dinner', 'receipt']
        if any(keyword in text_lower for keyword in meal_keywords):
            return "meal"
        
        # Cab keywords
        cab_keywords = ['cab', 'taxi', 'ride', 'driver', 'pickup', 'drop']
        if any(keyword in text_lower for keyword in cab_keywords):
            return "cab"
        
        return "general"
    
    def _extract_description(self, text: str) -> str:
        """Extract a brief description of the invoice"""
        # Take first few meaningful lines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        meaningful_lines = []
        
        for line in lines[:10]:  # Check first 10 lines
            if len(line) > 10 and not line.isdigit():
                meaningful_lines.append(line)
        
        return " | ".join(meaningful_lines[:3]) if meaningful_lines else "Invoice"
    
    def _extract_travel_details(self, text: str) -> Dict[str, Any]:
        """Extract travel-specific details"""
        details = {}
        
        # Extract boarding and destination
        boarding_match = re.search(r'Boarding[:\s]+([^\n]+)', text, re.IGNORECASE)
        if boarding_match:
            details["boarding_point"] = boarding_match.group(1).strip()
        
        destination_match = re.search(r'Destination[:\s]+([^\n]+)', text, re.IGNORECASE)
        if destination_match:
            details["destination"] = destination_match.group(1).strip()
        
        # Extract seat number
        seat_match = re.search(r'Seat\s*Number[:\s]+(\d+)', text, re.IGNORECASE)
        if seat_match:
            details["seat_number"] = seat_match.group(1)
        
        return details
    
    def _extract_meal_details(self, text: str) -> Dict[str, Any]:
        """Extract meal-specific details"""
        details = {}
        
        # Extract restaurant name
        restaurant_match = re.search(r'^([A-Z\s]+)', text)
        if restaurant_match:
            details["restaurant"] = restaurant_match.group(1).strip()
        
        # Extract items
        items = re.findall(r'(\d+)\s+([A-Za-z\s]+)\s+(\d+(?:\.\d{2})?)', text)
        if items:
            details["items"] = [{"quantity": qty, "name": name.strip(), "price": price} 
                             for qty, name, price in items]
        
        return details
    
    def _extract_cab_details(self, text: str) -> Dict[str, Any]:
        """Extract cab-specific details"""
        details = {}
        
        # Extract pickup address
        pickup_match = re.search(r'Pickup Address[:\s]+([^\n]+)', text, re.IGNORECASE)
        if pickup_match:
            details["pickup_address"] = pickup_match.group(1).strip()
        
        # Extract ride fee
        ride_fee_match = re.search(r'Ride Fee[:\s]+₹\s*(\d+(?:\.\d{2})?)', text, re.IGNORECASE)
        if ride_fee_match:
            details["ride_fee"] = float(ride_fee_match.group(1))
        
        return details
