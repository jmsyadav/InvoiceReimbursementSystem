"""
Fraud detection utility for identifying suspicious invoice patterns
"""

import re
from typing import Dict, Any, Tuple
from datetime import datetime, timedelta

class FraudDetector:
    """Utility class for detecting fraudulent patterns in invoices"""
    
    def __init__(self):
        # Define fraud detection rules
        self.rules = {
            'date_inconsistency': self._check_date_inconsistency,
            'amount_anomaly': self._check_amount_anomaly,
            'duplicate_detection': self._check_duplicate_patterns,
            'format_anomaly': self._check_format_anomaly
        }
    
    def detect_fraud(self, invoice_details: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Detect fraudulent patterns in invoice details
        
        Args:
            invoice_details: Dictionary containing parsed invoice data
            
        Returns:
            Tuple of (is_fraudulent, reason)
        """
        try:
            fraud_flags = []
            
            # Run all fraud detection rules
            for rule_name, rule_func in self.rules.items():
                is_fraud, reason = rule_func(invoice_details)
                if is_fraud:
                    fraud_flags.append(f"{rule_name}: {reason}")
            
            # Determine overall fraud status
            if fraud_flags:
                return True, "; ".join(fraud_flags)
            else:
                return False, None
                
        except Exception as e:
            print(f"❌ Error in fraud detection: {e}")
            return False, None
    
    def _check_date_inconsistency(self, invoice_details: Dict[str, Any]) -> Tuple[bool, str]:
        """Check for date inconsistencies in travel invoices"""
        try:
            invoice_type = invoice_details.get('type', '').lower()
            
            # Only check travel invoices
            if invoice_type != 'travel':
                return False, None
            
            reporting_date = invoice_details.get('reporting_date')
            dropping_date = invoice_details.get('dropping_date')
            
            if not reporting_date or not dropping_date:
                return False, None
            
            # Parse dates
            reporting_dt = self._parse_date_flexible(reporting_date)
            dropping_dt = self._parse_date_flexible(dropping_date)
            
            if not reporting_dt or not dropping_dt:
                return False, None
            
            # Check if dropping date is before reporting date
            if dropping_dt < reporting_dt:
                return True, f"Dropping date ({dropping_date}) is before reporting date ({reporting_date})"
            
            # Check if the gap is too large (more than 30 days)
            if (dropping_dt - reporting_dt).days > 30:
                return True, f"Unusually large gap between reporting and dropping dates ({(dropping_dt - reporting_dt).days} days)"
            
            return False, None
            
        except Exception as e:
            print(f"❌ Error checking date inconsistency: {e}")
            return False, None
    
    def _check_amount_anomaly(self, invoice_details: Dict[str, Any]) -> Tuple[bool, str]:
        """Check for suspicious amount patterns"""
        try:
            amount = invoice_details.get('amount', 0.0)
            
            # Check for zero or negative amounts
            if amount <= 0:
                return True, f"Invalid amount: ₹{amount}"
            
            # Check for extremely high amounts (adjust threshold as needed)
            if amount > 50000:  # ₹50,000 threshold
                return True, f"Unusually high amount: ₹{amount}"
            
            # Check for suspicious round numbers (might indicate fabrication)
            if amount == int(amount) and amount % 100 == 0 and amount > 1000:
                return True, f"Suspicious round amount: ₹{amount}"
            
            return False, None
            
        except Exception as e:
            print(f"❌ Error checking amount anomaly: {e}")
            return False, None
    
    def _check_duplicate_patterns(self, invoice_details: Dict[str, Any]) -> Tuple[bool, str]:
        """Check for duplicate or suspicious patterns"""
        try:
            # This is a simplified check - in production, you'd compare against a database
            # For now, we'll check for obvious duplicate patterns in the same invoice
            
            invoice_text = invoice_details.get('invoice_text', '').lower()
            
            # Check for repeated information that might indicate copy-paste fraud
            lines = invoice_text.split('\n')
            unique_lines = set(lines)
            
            # If there are many duplicate lines, it might be suspicious
            if len(lines) > 10 and len(unique_lines) < len(lines) * 0.5:
                return True, "Excessive duplicate information detected"
            
            return False, None
            
        except Exception as e:
            print(f"❌ Error checking duplicate patterns: {e}")
            return False, None
    
    def _check_format_anomaly(self, invoice_details: Dict[str, Any]) -> Tuple[bool, str]:
        """Check for format anomalies that might indicate fraud"""
        try:
            invoice_text = invoice_details.get('invoice_text', '')
            
            # Check for missing critical information
            critical_fields = ['amount', 'date', 'employee_name']
            missing_fields = []
            
            for field in critical_fields:
                if not invoice_details.get(field) or invoice_details.get(field) in ['Unknown', 'N/A', '']:
                    missing_fields.append(field)
            
            if len(missing_fields) > 1:
                return True, f"Missing critical information: {', '.join(missing_fields)}"
            
            # Check for extremely short invoice text (might be fake)
            if len(invoice_text.strip()) < 50:
                return True, "Invoice text too short to be legitimate"
            
            return False, None
            
        except Exception as e:
            print(f"❌ Error checking format anomaly: {e}")
            return False, None
    
    def _parse_date_flexible(self, date_str: str) -> datetime:
        """Parse date string with flexible format support"""
        if not date_str:
            return None
        
        try:
            # Try different date formats
            formats = [
                '%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y',
                '%d %B %Y', '%d %b %Y',
                '%B %d %Y', '%b %d %Y',
                '%Y-%m-%d', '%Y/%m/%d',
                '%d %m %Y', '%m/%d/%Y'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str.strip(), fmt)
                except ValueError:
                    continue
            
            # If no format matches, return None
            return None
            
        except Exception:
            return None
    
    def get_fraud_report(self, invoice_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive fraud analysis report
        
        Args:
            invoice_details: Dictionary containing parsed invoice data
            
        Returns:
            Dictionary containing fraud analysis report
        """
        try:
            report = {
                'invoice_id': invoice_details.get('invoice_id', 'Unknown'),
                'employee_name': invoice_details.get('employee_name', 'Unknown'),
                'fraud_detected': False,
                'fraud_reasons': [],
                'risk_score': 0,
                'checks_performed': [],
                'recommendations': []
            }
            
            # Run all fraud detection rules and collect results
            for rule_name, rule_func in self.rules.items():
                is_fraud, reason = rule_func(invoice_details)
                
                check_result = {
                    'rule': rule_name,
                    'passed': not is_fraud,
                    'reason': reason
                }
                report['checks_performed'].append(check_result)
                
                if is_fraud:
                    report['fraud_detected'] = True
                    report['fraud_reasons'].append(reason)
                    report['risk_score'] += 25  # Each fraud rule adds 25 points
            
            # Cap risk score at 100
            report['risk_score'] = min(report['risk_score'], 100)
            
            # Add recommendations based on findings
            if report['fraud_detected']:
                report['recommendations'].append("Manual review required")
                if report['risk_score'] > 50:
                    report['recommendations'].append("High risk - consider rejecting")
                else:
                    report['recommendations'].append("Medium risk - investigate further")
            else:
                report['recommendations'].append("No fraud indicators detected")
            
            return report
            
        except Exception as e:
            print(f"❌ Error generating fraud report: {e}")
            return {
                'invoice_id': invoice_details.get('invoice_id', 'Unknown'),
                'employee_name': invoice_details.get('employee_name', 'Unknown'),
                'fraud_detected': False,
                'fraud_reasons': [],
                'risk_score': 0,
                'checks_performed': [],
                'recommendations': ['Error during fraud analysis'],
                'error': str(e)
            }
    
    def validate_travel_invoice(self, invoice_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Specific validation for travel invoices
        
        Args:
            invoice_details: Dictionary containing parsed invoice data
            
        Returns:
            Dictionary containing validation results
        """
        validation_result = {
            'is_valid': True,
            'issues': [],
            'warnings': []
        }
        
        try:
            # Check for required travel invoice fields
            required_fields = ['reporting_date', 'amount', 'employee_name']
            
            for field in required_fields:
                if not invoice_details.get(field) or invoice_details.get(field) == 'Unknown':
                    validation_result['issues'].append(f"Missing required field: {field}")
                    validation_result['is_valid'] = False
            
            # Check date consistency
            is_fraud, reason = self._check_date_inconsistency(invoice_details)
            if is_fraud:
                validation_result['issues'].append(reason)
                validation_result['is_valid'] = False
            
            # Check amount reasonableness
            amount = invoice_details.get('amount', 0)
            if amount > 10000:  # Warning for high amounts
                validation_result['warnings'].append(f"High amount detected: ₹{amount}")
            
            return validation_result
            
        except Exception as e:
            return {
                'is_valid': False,
                'issues': [f"Validation error: {str(e)}"],
                'warnings': []
            }
