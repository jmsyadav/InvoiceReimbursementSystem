import re
from typing import Optional

class EmployeeExtractor:
    """Utility class for extracting employee names from invoice text"""
    
    def __init__(self):
        # Common patterns for employee name extraction
        self.name_patterns = [
            r'Customer Name[:\s]+([A-Za-z\s]+)',
            r'Passenger Details[:\s]+([A-Za-z\s]+)',
            r'Employee[:\s]+([A-Za-z\s]+)',
            r'Name[:\s]+([A-Za-z\s]+)',
            r'([A-Za-z]+\s+[A-Za-z]+)\s+\d+,\s*(?:male|female)',  # Name followed by age and gender
            r'Bill to[:\s]+([A-Za-z\s]+)',
            r'Traveler[:\s]+([A-Za-z\s]+)',
            r'Passenger[:\s]+([A-Za-z\s]+)'
        ]
    
    def extract_employee_name(self, text: str) -> Optional[str]:
        """
        Extract employee name from invoice text using multiple strategies
        
        Args:
            text: Raw text from invoice
            
        Returns:
            Extracted employee name or None if not found
        """
        # Try each pattern
        for pattern in self.name_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                name = matches[0].strip()
                # Clean and validate the name
                cleaned_name = self._clean_name(name)
                if self._is_valid_name(cleaned_name):
                    return cleaned_name
        
        # Fallback: Look for capitalized words that might be names
        fallback_name = self._extract_fallback_name(text)
        if fallback_name:
            return fallback_name
        
        return None
    
    def _clean_name(self, name: str) -> str:
        """Clean extracted name by removing extra characters"""
        # Remove extra whitespace
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Remove common non-name suffixes
        suffixes_to_remove = ['Mobile Number', 'Phone', 'Contact', 'Email', 'ID', 'No']
        for suffix in suffixes_to_remove:
            if suffix.lower() in name.lower():
                name = name.split(suffix)[0].strip()
        
        # Remove numbers and special characters
        name = re.sub(r'[^\w\s]', '', name)
        name = re.sub(r'\d+', '', name)
        
        # Capitalize properly
        name = ' '.join(word.capitalize() for word in name.split())
        
        return name.strip()
    
    def _is_valid_name(self, name: str) -> bool:
        """Validate if the extracted text is likely a valid name"""
        if not name or len(name) < 2:
            return False
        
        # Check if contains only letters and spaces
        if not re.match(r'^[A-Za-z\s]+$', name):
            return False
        
        # Check for common invalid patterns
        invalid_patterns = [
            r'^(invoice|receipt|bill|payment|total|amount|date|time)$',
            r'^\d+$',
            r'^[A-Z]{1}$',  # Single letter
            r'^(mr|ms|mrs|dr)$'
        ]
        
        for pattern in invalid_patterns:
            if re.match(pattern, name.lower()):
                return False
        
        # Must have at least one letter
        if not re.search(r'[A-Za-z]', name):
            return False
        
        return True
    
    def _extract_fallback_name(self, text: str) -> Optional[str]:
        """Fallback method to extract names from text"""
        # Look for patterns like "FirstName LastName" in the text
        lines = text.split('\n')
        
        for line in lines:
            # Look for lines with 2-3 capitalized words
            words = line.strip().split()
            if len(words) >= 2:
                # Check if all words are capitalized and contain only letters
                if all(word.isalpha() and word[0].isupper() for word in words[:3]):
                    potential_name = ' '.join(words[:3])
                    if self._is_valid_name(potential_name):
                        return potential_name
        
        return None
