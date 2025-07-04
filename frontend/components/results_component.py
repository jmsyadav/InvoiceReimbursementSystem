import streamlit as st
import pandas as pd
from frontend.services.api_client import APIClient

def render_results_section():
    """Render the results viewing section"""
    st.header("View Results")
    
    # Initialize API client
    api_client = st.session_state.api_client
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["All Invoices", "Analytics", "Fraud Detection"])
    
    with tab1:
        render_all_invoices_tab(api_client)
    
    with tab2:
        render_analytics_tab(api_client)
    
    with tab3:
        render_fraud_detection_tab(api_client)

def render_all_invoices_tab(api_client):
    """Render the all invoices tab"""
    st.subheader("All Processed Invoices")
    
    # Fetch invoices from API
    try:
        with st.spinner("Loading invoices..."):
            response = api_client.get_invoices()
            
            if response.get("success"):
                invoices = response.get("invoices", [])
                
                if not invoices:
                    st.info("No invoices found. Please process some invoices first.")
                    return
                
                # Filter controls
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # Employee filter
                    employees = sorted(list(set(inv.get("employee_name", "Unknown") for inv in invoices)))
                    selected_employee = st.selectbox("Filter by Employee", ["All"] + employees)
                
                with col2:
                    # Status filter
                    statuses = sorted(list(set(inv.get("reimbursement_status", "Unknown") for inv in invoices)))
                    selected_status = st.selectbox("Filter by Status", ["All"] + statuses)
                
                with col3:
                    # Fraud filter
                    fraud_options = ["All", "Fraud Detected", "No Fraud"]
                    selected_fraud = st.selectbox("Filter by Fraud", fraud_options)
                
                # Apply filters
                filtered_invoices = invoices
                
                if selected_employee != "All":
                    filtered_invoices = [inv for inv in filtered_invoices if inv.get("employee_name") == selected_employee]
                
                if selected_status != "All":
                    filtered_invoices = [inv for inv in filtered_invoices if inv.get("reimbursement_status") == selected_status]
                
                if selected_fraud == "Fraud Detected":
                    filtered_invoices = [inv for inv in filtered_invoices if inv.get("fraud_detected")]
                elif selected_fraud == "No Fraud":
                    filtered_invoices = [inv for inv in filtered_invoices if not inv.get("fraud_detected")]
                
                # Display results count
                st.write(f"Showing {len(filtered_invoices)} of {len(invoices)} invoices")
                
                # Display invoices
                for invoice in filtered_invoices:
                    render_invoice_card(invoice)
            
            else:
                st.error("Failed to load invoices")
                
    except Exception as e:
        st.error(f"Error loading invoices: {str(e)}")

def render_invoice_card(invoice):
    """Render a single invoice card"""
    with st.expander(f"📄 {invoice.get('invoice_id', 'Unknown')} - {invoice.get('employee_name', 'Unknown')}"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Employee:** {invoice.get('employee_name', 'Unknown')}")
            st.write(f"**Date:** {invoice.get('invoice_date', 'Unknown')}")
            st.write(f"**Amount:** ₹{invoice.get('amount', 0)}")
            st.write(f"**Type:** {invoice.get('invoice_type', 'general')}")
            
        with col2:
            # Status with color coding
            status = invoice.get('reimbursement_status', 'Unknown')
            if status == "Fully Reimbursed":
                st.success(f"**Status:** {status}")
            elif status == "Partially Reimbursed":
                st.warning(f"**Status:** {status}")
            elif status == "Declined":
                st.error(f"**Status:** {status}")
            else:
                st.info(f"**Status:** {status}")
            
            # Fraud indicator
            if invoice.get('fraud_detected'):
                st.error("⚠️ **Fraud Detected**")
            else:
                st.success("✅ **No Fraud**")
        
        # Reason
        st.write(f"**Reason:** {invoice.get('reason', 'No reason provided')}")
        
        # Fraud reason if applicable
        if invoice.get('fraud_detected') and invoice.get('fraud_reason'):
            st.error(f"**Fraud Reason:** {invoice.get('fraud_reason')}")
        
        # Additional details based on type
        if invoice.get('invoice_type') == 'travel':
            if invoice.get('reporting_date'):
                st.write(f"**Reporting Date:** {invoice.get('reporting_date')}")
            if invoice.get('dropping_date'):
                st.write(f"**Dropping Date:** {invoice.get('dropping_date')}")
        
        # Description
        if invoice.get('description'):
            st.write(f"**Description:** {invoice.get('description')}")

def render_analytics_tab(api_client):
    """Render the analytics tab"""
    st.subheader("📈 Invoice Analytics")
    
    try:
        with st.spinner("Loading analytics..."):
            response = api_client.get_invoices()
            
            if response.get("success"):
                invoices = response.get("invoices", [])
                
                if not invoices:
                    st.info("No data available for analytics.")
                    return
                
                # Convert to DataFrame for easier analysis
                df = pd.DataFrame(invoices)
                
                # Summary metrics
                st.subheader("📊 Summary Metrics")
                
                metric_cols = st.columns(4)
                
                with metric_cols[0]:
                    st.metric("Total Invoices", len(df))
                
                with metric_cols[1]:
                    total_amount = df['amount'].sum()
                    st.metric("Total Amount", f"₹{total_amount:,.2f}")
                
                with metric_cols[2]:
                    avg_amount = df['amount'].mean()
                    st.metric("Average Amount", f"₹{avg_amount:,.2f}")
                
                with metric_cols[3]:
                    fraud_count = df['fraud_detected'].sum()
                    st.metric("Fraud Cases", fraud_count)
                
                # Status distribution
                st.subheader("📊 Status Distribution")
                status_counts = df['reimbursement_status'].value_counts()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.bar_chart(status_counts)
                
                with col2:
                    for status, count in status_counts.items():
                        percentage = (count / len(df)) * 100
                        st.write(f"**{status}:** {count} ({percentage:.1f}%)")
                
                # Employee analysis
                st.subheader("👥 Employee Analysis")
                employee_stats = df.groupby('employee_name').agg({
                    'amount': ['count', 'sum', 'mean'],
                    'fraud_detected': 'sum'
                }).round(2)
                
                employee_stats.columns = ['Invoice Count', 'Total Amount', 'Average Amount', 'Fraud Cases']
                st.dataframe(employee_stats)
                
                # Amount distribution
                st.subheader("💰 Amount Distribution")
                st.histogram_chart(df['amount'])
                
                # Fraud analysis
                if df['fraud_detected'].sum() > 0:
                    st.subheader("🚨 Fraud Analysis")
                    fraud_df = df[df['fraud_detected'] == True]
                    
                    st.write(f"**Fraud Rate:** {(len(fraud_df) / len(df)) * 100:.1f}%")
                    st.write(f"**Fraudulent Amount:** ₹{fraud_df['amount'].sum():,.2f}")
                    
                    # Fraud by employee
                    fraud_by_employee = fraud_df['employee_name'].value_counts()
                    if len(fraud_by_employee) > 0:
                        st.write("**Fraud Cases by Employee:**")
                        st.bar_chart(fraud_by_employee)
                
            else:
                st.error("Failed to load analytics data")
                
    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")

def render_fraud_detection_tab(api_client):
    """Render the fraud detection tab"""
    st.subheader("🚨 Fraud Detection")
    
    try:
        with st.spinner("Loading fraud data..."):
            response = api_client.get_invoices()
            
            if response.get("success"):
                invoices = response.get("invoices", [])
                fraud_invoices = [inv for inv in invoices if inv.get('fraud_detected')]
                
                if not fraud_invoices:
                    st.success("✅ No fraud detected in processed invoices!")
                    return
                
                st.error(f"⚠️ {len(fraud_invoices)} fraudulent invoice(s) detected")
                
                # Fraud summary
                st.subheader("📊 Fraud Summary")
                
                fraud_amount = sum(inv.get('amount', 0) for inv in fraud_invoices)
                fraud_rate = (len(fraud_invoices) / len(invoices)) * 100
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Fraud Cases", len(fraud_invoices))
                
                with col2:
                    st.metric("Fraudulent Amount", f"₹{fraud_amount:,.2f}")
                
                with col3:
                    st.metric("Fraud Rate", f"{fraud_rate:.1f}%")
                
                # Fraud details
                st.subheader("🔍 Fraud Details")
                
                for fraud_invoice in fraud_invoices:
                    with st.expander(f"🚨 {fraud_invoice.get('invoice_id', 'Unknown')} - {fraud_invoice.get('employee_name', 'Unknown')}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Employee:** {fraud_invoice.get('employee_name', 'Unknown')}")
                            st.write(f"**Date:** {fraud_invoice.get('invoice_date', 'Unknown')}")
                            st.write(f"**Amount:** ₹{fraud_invoice.get('amount', 0)}")
                        
                        with col2:
                            st.write(f"**Type:** {fraud_invoice.get('invoice_type', 'general')}")
                            st.write(f"**Status:** {fraud_invoice.get('reimbursement_status', 'Unknown')}")
                        
                        st.error(f"**Fraud Reason:** {fraud_invoice.get('fraud_reason', 'No reason provided')}")
                        
                        # Additional fraud indicators
                        if fraud_invoice.get('reporting_date') and fraud_invoice.get('dropping_date'):
                            st.write(f"**Reporting Date:** {fraud_invoice.get('reporting_date')}")
                            st.write(f"**Dropping Date:** {fraud_invoice.get('dropping_date')}")
                
                # Fraud prevention tips
                st.subheader("💡 Fraud Prevention Tips")
                st.markdown("""
                - **Date Validation**: Ensure travel dates are logical and consistent
                - **Amount Verification**: Check for unusually high amounts for expense categories
                - **Documentation**: Require proper receipts and supporting documents
                - **Employee Training**: Educate employees on expense policy compliance
                - **Regular Audits**: Conduct periodic reviews of expense patterns
                """)
            
            else:
                st.error("Failed to load fraud data")
                
    except Exception as e:
        st.error(f"Error loading fraud data: {str(e)}")
