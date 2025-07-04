from typing import Dict, Any
from datetime import datetime
from ..utils.date_parser import DateParser

class FraudDetector:
    """Service for detecting potential fraud in invoices"""
    
    def __init__(self):
        self.date_parser = DateParser()
    
    def detect_fraud(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect potential fraud in invoice data
        
        Args:
            invoice_data: Structured invoice data
            
        Returns:
            Dictionary with fraud detection results
        """
        try:
            fraud_indicators = []
            
            # Check for travel invoice date inconsistencies
            if invoice_data.get("invoice_type") == "travel":
                date_fraud = self._check_travel_date_fraud(invoice_data)
                if date_fraud["is_fraud"]:
                    fraud_indicators.append(date_fraud["reason"])
            
            # Check for duplicate invoices (based on amount and date)
            duplicate_fraud = self._check_duplicate_invoice(invoice_data)
            if duplicate_fraud["is_fraud"]:
                fraud_indicators.append(duplicate_fraud["reason"])
            
            # Check for amount anomalies
            amount_fraud = self._check_amount_anomalies(invoice_data)
            if amount_fraud["is_fraud"]:
                fraud_indicators.append(amount_fraud["reason"])
            
            # Check for missing required fields
            missing_field_fraud = self._check_missing_fields(invoice_data)
            if missing_field_fraud["is_fraud"]:
                fraud_indicators.append(missing_field_fraud["reason"])
            
            # Determine overall fraud status
            is_fraud = len(fraud_indicators) > 0
            reason = " | ".join(fraud_indicators) if fraud_indicators else "No fraud detected"
            
            return {
                "is_fraud": is_fraud,
                "reason": reason,
                "indicators": fraud_indicators,
                "confidence": self._calculate_fraud_confidence(fraud_indicators)
            }
            
        except Exception as e:
            return {
                "is_fraud": False,
                "reason": f"Fraud detection error: {str(e)}",
                "indicators": [],
                "confidence": 0.0
            }
    
    def _check_travel_date_fraud(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check for date inconsistencies in travel invoices"""
        try:
            reporting_date = invoice_data.get("reporting_date")
            dropping_date = invoice_data.get("dropping_date")
            
            if reporting_date and dropping_date:
                # Parse dates
                reporting_dt = self.date_parser.parse_date(reporting_date)
                dropping_dt = self.date_parser.parse_date(dropping_date)
                
                if reporting_dt and dropping_dt:
                    # Check if reporting date is after dropping date
                    if reporting_dt > dropping_dt:
                        return {
                            "is_fraud": True,
                            "reason": f"Travel date inconsistency: Reporting date ({reporting_date}) is after dropping date ({dropping_date})"
                        }
                    
                    # Check if dates are too far apart (more than 30 days)
                    date_diff = (dropping_dt - reporting_dt).days
                    if date_diff > 30:
                        return {
                            "is_fraud": True,
                            "reason": f"Suspicious travel duration: {date_diff} days between reporting and dropping dates"
                        }
            
            return {"is_fraud": False, "reason": ""}
            
        except Exception as e:
            return {"is_fraud": False, "reason": f"Date validation error: {str(e)}"}
    
    def _check_duplicate_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check for potential duplicate invoices"""
        # This would typically check against a database of existing invoices
        # For now, we'll implement basic validation
        
        amount = invoice_data.get("amount")
        date = invoice_data.get("date")
        employee = invoice_data.get("employee_name")
        
        # Basic duplicate detection logic
        if amount and date and employee:
            # Check for round numbers (potential indicator of fabricated invoices)
            if amount % 100 == 0 and amount > 1000:
                return {
                    "is_fraud": True,
                    "reason": f"Suspicious round amount: ₹{amount} (potential fabricated invoice)"
                }
        
        return {"is_fraud": False, "reason": ""}
    
    def _check_amount_anomalies(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check for amount-related anomalies"""
        amount = invoice_data.get("amount")
        invoice_type = invoice_data.get("invoice_type")
        
        if amount:
            # Check for unusually high amounts by category
            if invoice_type == "meal" and amount > 5000:
                return {
                    "is_fraud": True,
                    "reason": f"Unusually high meal expense: ₹{amount}"
                }
            elif invoice_type == "cab" and amount > 3000:
                return {
                    "is_fraud": True,
                    "reason": f"Unusually high cab fare: ₹{amount}"
                }
            elif invoice_type == "travel" and amount > 50000:
                return {
                    "is_fraud": True,
                    "reason": f"Unusually high travel expense: ₹{amount}"
                }
            
            # Check for negative amounts
            if amount < 0:
                return {
                    "is_fraud": True,
                    "reason": f"Negative amount detected: ₹{amount}"
                }
        
        return {"is_fraud": False, "reason": ""}
    
    def _check_missing_fields(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check for missing required fields"""
        required_fields = ["employee_name", "date", "amount"]
        missing_fields = []
        
        for field in required_fields:
            if not invoice_data.get(field):
                missing_fields.append(field)
        
        if missing_fields:
            return {
                "is_fraud": True,
                "reason": f"Missing required fields: {', '.join(missing_fields)}"
            }
        
        return {"is_fraud": False, "reason": ""}
    
    def _calculate_fraud_confidence(self, indicators: list) -> float:
        """Calculate confidence score for fraud detection"""
        if not indicators:
            return 0.0
        
        # Simple confidence calculation based on number of indicators
        base_confidence = len(indicators) * 0.3
        return min(base_confidence, 1.0)
