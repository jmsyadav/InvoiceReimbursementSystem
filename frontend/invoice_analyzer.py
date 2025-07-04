"""
Invoice Analyzer component for the Streamlit frontend
"""

import streamlit as st
import requests
import json
import time
from typing import List, Dict, Any
import zipfile
import tempfile
import os

class InvoiceAnalyzer:
    """Component for handling invoice analysis functionality"""
    
    def __init__(self, backend_url: str):
        self.backend_url = backend_url
    
    def render(self):
        """Render the invoice analyzer interface"""
        # File upload section
        self.render_file_upload()
        
        # Analysis results section
        if st.session_state.get('analysis_results'):
            self.render_analysis_results()
    
    def render_file_upload(self):
        """Render file upload interface"""
        st.subheader("📁 File Upload")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**HR Reimbursement Policy**")
            policy_file = st.file_uploader(
                "Upload HR policy document",
                type=['pdf'],
                help="Upload the company's HR reimbursement policy PDF"
            )
        
        with col2:
            st.markdown("**Invoice Files**")
            invoice_files = st.file_uploader(
                "Upload invoice ZIP files",
                type=['zip'],
                accept_multiple_files=True,
                help="Upload one or more ZIP files containing employee invoices"
            )
        
        # Analysis button
        if st.button("🔍 Analyze Invoices", type="primary", use_container_width=True):
            if policy_file and invoice_files:
                self.process_invoices(policy_file, invoice_files)
            else:
                st.error("Please upload both policy file and invoice files")
    
    def process_invoices(self, policy_file, invoice_files: List):
        """Process invoices using the backend API"""
        try:
            # Show progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("📤 Uploading files...")
            progress_bar.progress(20)
            
            # Prepare files for upload
            files = {
                'policy_file': (policy_file.name, policy_file.getvalue(), 'application/pdf')
            }
            

            
            status_text.text("🔄 Processing invoices...")
            progress_bar.progress(40)
            
            # Make API request with proper multipart format
            # Handle multiple files correctly - use dictionary format
            files_data = {}
            files_data['policy_file'] = (policy_file.name, policy_file.getvalue(), 'application/pdf')
            
            # For multiple files with same key, use list
            invoice_files_data = []
            for invoice_file in invoice_files:
                invoice_files_data.append((invoice_file.name, invoice_file.getvalue(), 'application/zip'))
            
            # If only one file, use single tuple; if multiple, use list
            if len(invoice_files_data) == 1:
                files_data['invoice_files'] = invoice_files_data[0]
            else:
                files_data['invoice_files'] = invoice_files_data
            
            response = requests.post(
                f"{self.backend_url}/analyze-invoices",
                files=files_data,
                timeout=300  # 5 minutes timeout
            )
            
            progress_bar.progress(80)
            
            if response.status_code == 200:
                result = response.json()
                
                # Store results in session state
                st.session_state.analysis_results = result
                st.session_state.processed_invoices = result.get('results', [])
                
                progress_bar.progress(100)
                status_text.text("✅ Analysis completed successfully!")
                
                # Show success message
                st.success(f"Successfully analyzed {result['processed_count']} invoices!")
                
                # Auto-refresh to show results
                time.sleep(1)
                st.rerun()
                
            else:
                st.error(f"Analysis failed: {response.text}")
                
        except requests.RequestException as e:
            st.error(f"Network error: {str(e)}")
        except Exception as e:
            st.error(f"Error processing invoices: {str(e)}")
        finally:
            # Clean up progress indicators - ignore if not initialized
            pass
    
    def render_analysis_results(self):
        """Render analysis results"""
        st.subheader("📊 Analysis Results")
        
        results = st.session_state.analysis_results
        
        # Summary metrics
        self.render_summary_metrics(results)
        
        # Detailed results
        self.render_detailed_results(results)
    
    def render_summary_metrics(self, results: Dict[str, Any]):
        """Render summary metrics"""
        st.markdown("### Summary")
        
        invoices = results.get('results', [])
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Invoices", len(invoices))
        
        with col2:
            fully_reimbursed = sum(1 for inv in invoices if inv['status'] == 'Fully Reimbursed')
            st.metric("Fully Reimbursed", fully_reimbursed)
        
        with col3:
            partially_reimbursed = sum(1 for inv in invoices if inv['status'] == 'Partially Reimbursed')
            st.metric("Partially Reimbursed", partially_reimbursed)
        
        with col4:
            declined = sum(1 for inv in invoices if inv['status'] == 'Declined')
            st.metric("Declined", declined)
        
        # Fraud detection summary
        fraud_detected = sum(1 for inv in invoices if inv.get('is_fraudulent', False))
        if fraud_detected > 0:
            st.warning(f"⚠️ Fraud detected in {fraud_detected} invoice(s)")
    
    def render_detailed_results(self, results: Dict[str, Any]):
        """Render detailed analysis results"""
        st.markdown("### Detailed Results")
        
        invoices = results.get('results', [])
        
        if not invoices:
            st.info("No invoices to display")
            return
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_filter = st.selectbox(
                "Filter by Status",
                ["All", "Fully Reimbursed", "Partially Reimbursed", "Declined"]
            )
        
        with col2:
            employee_filter = st.selectbox(
                "Filter by Employee",
                ["All"] + list(set(inv['employee_name'] for inv in invoices))
            )
        
        with col3:
            fraud_filter = st.selectbox(
                "Filter by Fraud Detection",
                ["All", "Fraud Detected", "No Fraud"]
            )
        
        # Apply filters
        filtered_invoices = self.apply_filters(invoices, status_filter, employee_filter, fraud_filter)
        
        # Display results
        for invoice in filtered_invoices:
            self.render_invoice_card(invoice)
    
    def apply_filters(self, invoices: List[Dict], status_filter: str, employee_filter: str, fraud_filter: str) -> List[Dict]:
        """Apply filters to invoice list"""
        filtered = invoices.copy()
        
        if status_filter != "All":
            filtered = [inv for inv in filtered if inv['status'] == status_filter]
        
        if employee_filter != "All":
            filtered = [inv for inv in filtered if inv['employee_name'] == employee_filter]
        
        if fraud_filter == "Fraud Detected":
            filtered = [inv for inv in filtered if inv.get('is_fraudulent', False)]
        elif fraud_filter == "No Fraud":
            filtered = [inv for inv in filtered if not inv.get('is_fraudulent', False)]
        
        return filtered
    
    def render_invoice_card(self, invoice: Dict[str, Any]):
        """Render an individual invoice card"""
        # Determine card color based on status
        if invoice['status'] == 'Fully Reimbursed':
            border_color = "#28a745"  # Green
        elif invoice['status'] == 'Partially Reimbursed':
            border_color = "#ffc107"  # Yellow
        else:
            border_color = "#dc3545"  # Red
        
        # Fraud indicator
        fraud_indicator = "🚨" if invoice.get('is_fraudulent', False) else ""
        
        with st.container():
            st.markdown(f"""
            <div style="border-left: 4px solid {border_color}; padding: 10px; margin: 10px 0; background-color: #f8f9fa;">
                <h4>{fraud_indicator} {invoice['invoice_id']} - {invoice['employee_name']}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Date:** {invoice['invoice_date']}")
                st.markdown(f"**Amount:** ₹{invoice['amount']}")
                st.markdown(f"**Status:** {invoice['status']}")
            
            with col2:
                if invoice.get('is_fraudulent', False):
                    st.markdown(f"**Fraud Detected:** Yes")
                    st.markdown(f"**Fraud Reason:** {invoice.get('fraud_reason', 'N/A')}")
                else:
                    st.markdown(f"**Fraud Detected:** No")
            
            # Reason
            st.markdown(f"**Analysis Reason:**")
            st.markdown(invoice['reason'])
            
            # Expandable invoice text
            with st.expander("View Full Invoice Text"):
                st.text_area(
                    "Invoice Content",
                    invoice['invoice_text'],
                    height=200,
                    disabled=True
                )
            
            st.markdown("---")
    
    def export_results(self, results: Dict[str, Any]):
        """Export results to CSV"""
        invoices = results.get('results', [])
        
        if not invoices:
            st.warning("No results to export")
            return
        
        # Prepare data for export
        export_data = []
        for invoice in invoices:
            export_data.append({
                'Invoice ID': invoice['invoice_id'],
                'Employee Name': invoice['employee_name'],
                'Date': invoice['invoice_date'],
                'Amount': invoice['amount'],
                'Status': invoice['status'],
                'Reason': invoice['reason'],
                'Fraud Detected': invoice.get('is_fraudulent', False),
                'Fraud Reason': invoice.get('fraud_reason', ''),
                'Processed At': invoice['processed_at']
            })
        
        # Create CSV
        import pandas as pd
        df = pd.DataFrame(export_data)
        csv = df.to_csv(index=False)
        
        st.download_button(
            label="📥 Download Results as CSV",
            data=csv,
            file_name=f"invoice_analysis_{results.get('processed_count', 0)}_invoices.csv",
            mime="text/csv"
        )
