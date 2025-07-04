"""
Invoice parser utility for extracting structured data from invoice text
"""

import re
from typing import Dict, Any, Optional
from datetime import datetime

class InvoiceParser:
    """Utility class for parsing invoice text and extracting structured data"""
    
    def __init__(self):
        # Common patterns for different invoice fields
        self.patterns = {
            'amount': [
                r'total[:\s]*[₹$]?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'amount[:\s]*[₹$]?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'net amount[:\s]*[₹$]?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'₹\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'fare[:\s]*[₹$]?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)'
            ],
            'date': [
                r'date[:\s]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})',
                r'date[:\s]*(\d{1,2}\s+\w+\s+\d{4})',
                r'invoice date[:\s]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})',
                r'(\d{1,2}\s+\w+\s+\d{4})',
                r'(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})',
                r'reporting date[:\s]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})'
            ],
            'employee_name': [
                r'customer name[:\s]*([a-zA-Z\s]+)',
                r'passenger[:\s]*([a-zA-Z\s]+)',
                r'employee[:\s]*([a-zA-Z\s]+)',
                r'name[:\s]*([a-zA-Z\s]+)',
                r'passenger details[:\s]*([a-zA-Z\s]+)',
                r'([a-zA-Z]+\s+[a-zA-Z])\s*\d+,?\s*\w*'  # Pattern for "Name Age, Gender"
            ],
            'invoice_id': [
                r'invoice\s+(?:id|no|number)[:\s]*([a-zA-Z0-9]+)',
                r'receipt\s+(?:id|no|number)[:\s]*([a-zA-Z0-9]+)',
                r'ticket\s+(?:id|no|number)[:\s]*([a-zA-Z0-9]+)',
                r'(?:id|no|number)[:\s]*([a-zA-Z0-9]+)'
            ],
            'type': [
                r'(meal|food|restaurant|cafe)',
                r'(travel|cab|taxi|bus|train|flight)',
                r'(accommodation|hotel|lodging)',
                r'(fuel|petrol|diesel|gas)'
            ]
        }
    
    def parse_invoice(self, invoice_text: str) -> Dict[str, Any]:
        """
        Parse invoice text and extract structured data
        
        Args:
            invoice_text: Raw text extracted from invoice
            
        Returns:
            Dictionary containing parsed invoice data
        """
        try:
            invoice_text_lower = invoice_text.lower()
            parsed_data = {}
            
            # Extract amount
            parsed_data['amount'] = self._extract_amount(invoice_text_lower)
            
            # Extract date
            parsed_data['date'] = self._extract_date(invoice_text)
            
            # Extract employee name
            parsed_data['employee_name'] = self._extract_employee_name(invoice_text)
            
            # Extract invoice ID
            parsed_data['invoice_id'] = self._extract_invoice_id(invoice_text)
            
            # Extract invoice type
            parsed_data['type'] = self._extract_type(invoice_text_lower)
            
            # Extract additional fields for travel invoices
            if parsed_data['type'] == 'travel':
                parsed_data.update(self._extract_travel_details(invoice_text))
            
            return parsed_data
            
        except Exception as e:
            print(f"❌ Error parsing invoice: {e}")
            return {
                'amount': 0.0,
                'date': 'Unknown',
                'employee_name': 'Unknown',
                'invoice_id': 'Unknown',
                'type': 'Unknown'
            }
    
    def _extract_amount(self, invoice_text: str) -> float:
        """Extract amount from invoice text"""
        for pattern in self.patterns['amount']:
            match = re.search(pattern, invoice_text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        return 0.0
    
    def _extract_date(self, invoice_text: str) -> str:
        """Extract date from invoice text"""
        for pattern in self.patterns['date']:
            match = re.search(pattern, invoice_text, re.IGNORECASE)
            if match:
                return match.group(1)
        return 'Unknown'
    
    def _extract_employee_name(self, invoice_text: str) -> str:
        """Extract employee name from invoice text"""
        for pattern in self.patterns['employee_name']:
            match = re.search(pattern, invoice_text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Clean up the name
                name = re.sub(r'\s+', ' ', name)  # Remove extra whitespace
                name = re.sub(r'[0-9,]+.*$', '', name)  # Remove age/gender info
                name = name.strip()
                if len(name) > 1 and name.replace(' ', '').isalpha():
                    return name.title()
        return 'Unknown'
    
    def _extract_invoice_id(self, invoice_text: str) -> str:
        """Extract invoice ID from invoice text"""
        for pattern in self.patterns['invoice_id']:
            match = re.search(pattern, invoice_text, re.IGNORECASE)
            if match:
                return match.group(1)
        return 'Unknown'
    
    def _extract_type(self, invoice_text: str) -> str:
        """Extract invoice type from invoice text"""
        for pattern in self.patterns['type']:
            if re.search(pattern, invoice_text, re.IGNORECASE):
                return pattern.strip('()')
        return 'Unknown'
    
    def _extract_travel_details(self, invoice_text: str) -> Dict[str, Any]:
        """Extract additional details for travel invoices"""
        details = {}
        
        # Extract reporting date and dropping date for fraud detection
        reporting_date_match = re.search(
            r'reporting date[:\s]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})',
            invoice_text,
            re.IGNORECASE
        )
        if reporting_date_match:
            details['reporting_date'] = reporting_date_match.group(1)
        
        dropping_date_match = re.search(
            r'dropping point date[:\s]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})',
            invoice_text,
            re.IGNORECASE
        )
        if dropping_date_match:
            details['dropping_date'] = dropping_date_match.group(1)
        
        # Extract departure time
        departure_match = re.search(
            r'departure time[:\s]*(\d{1,2}:\d{2})',
            invoice_text,
            re.IGNORECASE
        )
        if departure_match:
            details['departure_time'] = departure_match.group(1)
        
        # Extract pickup and drop locations
        pickup_match = re.search(
            r'pickup.*?address[:\s]*([a-zA-Z0-9\s,#-]+)',
            invoice_text,
            re.IGNORECASE
        )
        if pickup_match:
            details['pickup_location'] = pickup_match.group(1).strip()
        
        return details
    
    def _clean_text_field(self, text: str) -> str:
        """Clean and normalize text fields"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters
        text = re.sub(r'[^\w\s\-.,;:!?()₹$@#%&*+=<>\/\\"\']', ' ', text)
        
        return text.strip()
    
    def validate_extracted_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean extracted data
        
        Args:
            data: Dictionary containing extracted data
            
        Returns:
            Validated and cleaned data dictionary
        """
        validated_data = {}
        
        # Validate amount
        amount = data.get('amount', 0.0)
        if isinstance(amount, (int, float)) and amount > 0:
            validated_data['amount'] = float(amount)
        else:
            validated_data['amount'] = 0.0
        
        # Validate date
        date = data.get('date', 'Unknown')
        if date and date != 'Unknown':
            # Try to parse and reformat date
            try:
                parsed_date = self._parse_date(date)
                validated_data['date'] = parsed_date
            except:
                validated_data['date'] = date
        else:
            validated_data['date'] = 'Unknown'
        
        # Validate employee name
        name = data.get('employee_name', 'Unknown')
        if name and name != 'Unknown' and len(name.strip()) > 0:
            validated_data['employee_name'] = name.strip().title()
        else:
            validated_data['employee_name'] = 'Unknown'
        
        # Validate invoice ID
        invoice_id = data.get('invoice_id', 'Unknown')
        if invoice_id and invoice_id != 'Unknown':
            validated_data['invoice_id'] = invoice_id
        else:
            validated_data['invoice_id'] = f"INV_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Validate type
        invoice_type = data.get('type', 'Unknown')
        validated_data['type'] = invoice_type
        
        # Copy other fields
        for key, value in data.items():
            if key not in validated_data:
                validated_data[key] = value
        
        return validated_data
    
    def _parse_date(self, date_str: str) -> str:
        """Parse and normalize date string"""
        try:
            # Try different date formats
            formats = [
                '%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y',
                '%d %B %Y', '%d %b %Y',
                '%B %d %Y', '%b %d %Y',
                '%Y-%m-%d', '%Y/%m/%d'
            ]
            
            for fmt in formats:
                try:
                    parsed = datetime.strptime(date_str, fmt)
                    return parsed.strftime('%d %B %Y')
                except ValueError:
                    continue
            
            # If no format matches, return original
            return date_str
            
        except Exception:
            return date_str
