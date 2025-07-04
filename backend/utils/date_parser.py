import re
from datetime import datetime
from typing import Dict, Optional

class DateParser:
    """Utility class for parsing dates from invoice text"""
    
    def __init__(self):
        # Common date patterns
        self.date_patterns = [
            r'Date[:\s]+(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',  # Date: DD/MM/YYYY
            r'(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',  # DD/MM/YYYY
            r'(\d{1,2}\s+[A-Za-z]+\s+\d{4})',  # DD Month YYYY
            r'([A-Za-z]+\s+\d{1,2},?\s+\d{4})',  # Month DD, YYYY
            r'(\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2})',  # YYYY/MM/DD
            r'Reporting Date[:\s]+(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',  # Reporting Date
            r'Dropping point Date[:\s]+(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',  # Dropping Date
            r'Invoice Date[:\s]+(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',  # Invoice Date
        ]
        
        # Specific patterns for different date types
        self.reporting_date_patterns = [
            r'Reporting Date[:\s]+(\d{1,2}\s+[A-Za-z]+\s+\d{4})',
            r'Departure time[:\s]+(\d{1,2}:\d{2})',
            r'(\d{1,2}\s+[A-Za-z]+\s+\d{4})\s+Reporting Date'
        ]
        
        self.dropping_date_patterns = [
            r'Dropping point Date[:\s]+(\d{1,2}\s+[A-Za-z]+\s+\d{4})',
            r'Dropping point time[:\s]+(\d{1,2}:\d{2})',
            r'(\d{1,2}\s+[A-Za-z]+\s+\d{4})\s+Dropping point Date'
        ]
        
        # Month name mappings
        self.month_mappings = {
            'jan': 1, 'january': 1,
            'feb': 2, 'february': 2,
            'mar': 3, 'march': 3,
            'apr': 4, 'april': 4,
            'may': 5,
            'jun': 6, 'june': 6,
            'jul': 7, 'july': 7,
            'aug': 8, 'august': 8,
            'sep': 9, 'september': 9,
            'oct': 10, 'october': 10,
            'nov': 11, 'november': 11,
            'dec': 12, 'december': 12
        }
    
    def extract_dates(self, text: str) -> Dict[str, Optional[str]]:
        """
        Extract various dates from invoice text
        
        Args:
            text: Raw text from invoice
            
        Returns:
            Dictionary with different types of dates
        """
        dates = {
            "primary_date": None,
            "reporting_date": None,
            "dropping_date": None,
            "invoice_date": None
        }
        
        # Extract primary date (most common date pattern)
        dates["primary_date"] = self._extract_primary_date(text)
        
        # Extract specific travel dates
        dates["reporting_date"] = self._extract_reporting_date(text)
        dates["dropping_date"] = self._extract_dropping_date(text)
        
        # Extract invoice date
        dates["invoice_date"] = self._extract_invoice_date(text)
        
        return dates
    
    def _extract_primary_date(self, text: str) -> Optional[str]:
        """Extract the primary date from invoice"""
        for pattern in self.date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                date_str = matches[0]
                normalized_date = self._normalize_date(date_str)
                if normalized_date:
                    return normalized_date
        return None
    
    def _extract_reporting_date(self, text: str) -> Optional[str]:
        """Extract reporting date for travel invoices"""
        # Look for specific reporting date patterns
        for pattern in self.reporting_date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                date_str = matches[0]
                normalized_date = self._normalize_date(date_str)
                if normalized_date:
                    return normalized_date
        
        # Fallback: Look for date near "Reporting Date" text
        reporting_context = re.search(r'Reporting Date.*?(\d{1,2}\s+[A-Za-z]+\s+\d{4})', text, re.IGNORECASE | re.DOTALL)
        if reporting_context:
            date_str = reporting_context.group(1)
            normalized_date = self._normalize_date(date_str)
            if normalized_date:
                return normalized_date
        
        return None
    
    def _extract_dropping_date(self, text: str) -> Optional[str]:
        """Extract dropping date for travel invoices"""
        # Look for specific dropping date patterns
        for pattern in self.dropping_date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                date_str = matches[0]
                normalized_date = self._normalize_date(date_str)
                if normalized_date:
                    return normalized_date
        
        # Fallback: Look for date near "Dropping point Date" text
        dropping_context = re.search(r'Dropping point Date.*?(\d{1,2}\s+[A-Za-z]+\s+\d{4})', text, re.IGNORECASE | re.DOTALL)
        if dropping_context:
            date_str = dropping_context.group(1)
            normalized_date = self._normalize_date(date_str)
            if normalized_date:
                return normalized_date
        
        return None
    
    def _extract_invoice_date(self, text: str) -> Optional[str]:
        """Extract invoice date"""
        invoice_patterns = [
            r'Invoice Date[:\s]+(\d{1,2}\s+[A-Za-z]+\s+\d{4})',
            r'Date[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})',
            r'(\d{1,2}\s+[A-Za-z]+\s+\d{4})\s+\d{2}:\d{2}'
        ]
        
        for pattern in invoice_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                date_str = matches[0]
                normalized_date = self._normalize_date(date_str)
                if normalized_date:
                    return normalized_date
        
        return None
    
    def _normalize_date(self, date_str: str) -> Optional[str]:
        """Normalize date string to a consistent format"""
        if not date_str:
            return None
        
        try:
            # Remove extra whitespace
            date_str = date_str.strip()
            
            # Handle different date formats
            if re.match(r'\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}', date_str):
                # DD/MM/YYYY format
                parts = re.split(r'[\/\-\.]', date_str)
                if len(parts) == 3:
                    day, month, year = parts
                    if len(year) == 2:
                        year = '20' + year
                    return f"{day.zfill(2)}/{month.zfill(2)}/{year}"
            
            elif re.match(r'\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2}', date_str):
                # YYYY/MM/DD format
                parts = re.split(r'[\/\-\.]', date_str)
                if len(parts) == 3:
                    year, month, day = parts
                    return f"{day.zfill(2)}/{month.zfill(2)}/{year}"
            
            elif re.match(r'\d{1,2}\s+[A-Za-z]+\s+\d{4}', date_str):
                # DD Month YYYY format
                parts = date_str.split()
                if len(parts) == 3:
                    day, month_name, year = parts
                    month_num = self.month_mappings.get(month_name.lower())
                    if month_num:
                        return f"{day.zfill(2)}/{str(month_num).zfill(2)}/{year}"
            
            elif re.match(r'[A-Za-z]+\s+\d{1,2},?\s+\d{4}', date_str):
                # Month DD, YYYY format
                date_str = date_str.replace(',', '')
                parts = date_str.split()
                if len(parts) == 3:
                    month_name, day, year = parts
                    month_num = self.month_mappings.get(month_name.lower())
                    if month_num:
                        return f"{day.zfill(2)}/{str(month_num).zfill(2)}/{year}"
            
            return date_str  # Return as-is if no pattern matches
            
        except Exception:
            return None
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object"""
        if not date_str:
            return None
        
        try:
            # Try different date formats
            formats = [
                '%d/%m/%Y',
                '%d-%m-%Y',
                '%d.%m.%Y',
                '%Y/%m/%d',
                '%Y-%m-%d',
                '%d %B %Y',
                '%B %d %Y',
                '%d %b %Y',
                '%b %d %Y'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            return None
            
        except Exception:
            return None
