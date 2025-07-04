import streamlit as st
import tempfile
import os
from frontend.services.api_client import APIClient

def render_upload_section():
    """Render the invoice upload and processing section"""
    st.header("Upload & Process Invoices")
    
    # Instructions
    st.markdown("""
    **Instructions:**
    1. Upload the HR reimbursement policy PDF file
    2. Upload one or more ZIP files containing employee invoice PDFs (or individual PDF files)
    3. Click 'Process Invoices' to analyze them against the policy
    """)
    
    # File upload sections
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("HR Reimbursement Policy")
        policy_file = st.file_uploader(
            "Upload policy PDF",
            type=['pdf'],
            help="Upload the HR reimbursement policy document"
        )
        
        if policy_file:
            st.success(f"Policy file uploaded: {policy_file.name}")
    
    with col2:
        st.subheader("Employee Invoices")
        invoice_files = st.file_uploader(
            "Upload invoice files",
            type=['zip', 'pdf'],
            accept_multiple_files=True,
            help="Upload ZIP files containing employee invoices or individual PDF files"
        )
        
        if invoice_files:
            st.success(f"{len(invoice_files)} invoice file(s) uploaded")
            for file in invoice_files:
                st.write(f"- {file.name}")
    
    # Process button
    if st.button("Process Invoices", type="primary", disabled=not (policy_file and invoice_files)):
        with st.spinner("Processing invoices... This may take a few minutes."):
            try:
                # Initialize API client
                api_client = st.session_state.api_client
                
                # Process invoices
                response = api_client.analyze_invoices(policy_file, invoice_files)
                
                if response.get("success"):
                    st.success(f"✅ {response['message']}")
                    
                    # Store results in session state
                    st.session_state.processed_invoices = response.get("results", [])
                    
                    # Show summary
                    results = response.get("results", [])
                    if results:
                        st.subheader("📊 Processing Summary")
                        
                        # Create summary metrics
                        total_invoices = len(results)
                        fully_reimbursed = sum(1 for r in results if r.get("reimbursement_status") == "Fully Reimbursed")
                        partially_reimbursed = sum(1 for r in results if r.get("reimbursement_status") == "Partially Reimbursed")
                        declined = sum(1 for r in results if r.get("reimbursement_status") == "Declined")
                        fraud_detected = sum(1 for r in results if r.get("fraud_detected"))
                        
                        # Display metrics
                        metric_cols = st.columns(5)
                        with metric_cols[0]:
                            st.metric("Total Invoices", total_invoices)
                        with metric_cols[1]:
                            st.metric("Fully Reimbursed", fully_reimbursed)
                        with metric_cols[2]:
                            st.metric("Partially Reimbursed", partially_reimbursed)
                        with metric_cols[3]:
                            st.metric("Declined", declined)
                        with metric_cols[4]:
                            st.metric("Fraud Detected", fraud_detected)
                        
                        # Show top results
                        st.subheader("🔍 Recent Results")
                        for i, result in enumerate(results[:5]):
                            with st.expander(f"Invoice: {result.get('invoice_id', 'Unknown')} - {result.get('employee_name', 'Unknown')}"):
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.write(f"**Employee:** {result.get('employee_name', 'Unknown')}")
                                    st.write(f"**Date:** {result.get('invoice_date', 'Unknown')}")
                                    st.write(f"**Amount:** ₹{result.get('amount', 0)}")
                                
                                with col2:
                                    status = result.get('reimbursement_status', 'Unknown')
                                    if status == "Fully Reimbursed":
                                        st.success(f"Status: {status}")
                                    elif status == "Partially Reimbursed":
                                        st.warning(f"Status: {status}")
                                    elif status == "Declined":
                                        st.error(f"Status: {status}")
                                    else:
                                        st.info(f"Status: {status}")
                                    
                                    if result.get('fraud_detected'):
                                        st.error("⚠️ Fraud detected")
                                
                                st.write(f"**Reason:** {result.get('reason', 'No reason provided')}")
                                
                                if result.get('fraud_detected'):
                                    st.write(f"**Fraud Reason:** {result.get('fraud_reason', 'No fraud reason provided')}")
                        
                        # Navigation suggestion
                        st.info("💡 Go to 'View Results' to see all processed invoices or 'Chatbot Query' to ask questions about the data.")
                
                else:
                    st.error(f"❌ Processing failed: {response.get('message', 'Unknown error')}")
                    
            except Exception as e:
                st.error(f"❌ Error processing invoices: {str(e)}")
                st.exception(e)
    
    # Processing tips
    st.markdown("---")
    st.subheader("💡 Processing Tips")
    st.markdown("""
    - **Policy Format**: Ensure your policy PDF is clear and well-formatted
    - **Invoice Quality**: Upload high-quality, readable invoice PDFs
    - **ZIP Files**: Organize invoices by employee or department in ZIP files
    - **File Names**: Use descriptive file names for better identification
    - **Processing Time**: Large batches may take several minutes to process
    """)
