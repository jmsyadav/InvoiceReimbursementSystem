"""
Dashboard component for the Invoice Reimbursement System
Provides overview statistics, charts, and key metrics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any
from datetime import datetime, timedelta
import calendar

class Dashboard:
    """Main dashboard component for invoice analytics"""
    
    def __init__(self, api_client):
        self.api_client = api_client
    
    def render(self):
        """Render the complete dashboard"""
        st.header("Invoice Reimbursement Dashboard")
        
        # Load data
        with st.spinner("Loading dashboard data..."):
            try:
                response = self.api_client.get_invoices()
                
                if response.get("success"):
                    invoices = response.get("invoices", [])
                    
                    if not invoices:
                        st.info("No invoice data available. Please process some invoices first.")
                        return
                    
                    # Convert to DataFrame
                    df = pd.DataFrame(invoices)
                    
                    # Render dashboard sections
                    self.render_summary_metrics(df)
                    self.render_status_overview(df)
                    self.render_employee_analytics(df)
                    self.render_fraud_overview(df)
                    self.render_amount_analytics(df)
                    self.render_recent_activity(df)
                    
                else:
                    st.error("Failed to load dashboard data")
                    
            except Exception as e:
                st.error(f"Error loading dashboard: {str(e)}")
    
    def render_summary_metrics(self, df: pd.DataFrame):
        """Render key summary metrics"""
        st.subheader("📈 Key Metrics")
        
        # Calculate metrics
        total_invoices = len(df)
        total_amount = df['amount'].sum()
        avg_amount = df['amount'].mean()
        
        # Approved amount (fully + partially reimbursed)
        approved_df = df[df['reimbursement_status'].isin(['Fully Reimbursed', 'Partially Reimbursed'])]
        approved_amount = approved_df['amount'].sum()
        
        # Fraud cases
        fraud_count = df['fraud_detected'].sum()
        fraud_amount = df[df['fraud_detected'] == True]['amount'].sum()
        
        # Approval rate
        approval_rate = (len(approved_df) / total_invoices) * 100 if total_invoices > 0 else 0
        
        # Display metrics in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Invoices",
                f"{total_invoices:,}",
                help="Total number of processed invoices"
            )
            
        with col2:
            st.metric(
                "Total Amount",
                f"₹{total_amount:,.2f}",
                help="Total claimed amount across all invoices"
            )
            
        with col3:
            st.metric(
                "Approved Amount",
                f"₹{approved_amount:,.2f}",
                delta=f"{approval_rate:.1f}% approval rate",
                help="Total amount approved for reimbursement"
            )
            
        with col4:
            st.metric(
                "Fraud Cases",
                f"{fraud_count}",
                delta=f"₹{fraud_amount:,.2f}" if fraud_amount > 0 else "₹0",
                delta_color="inverse",
                help="Number of invoices flagged for fraud"
            )
        
        # Additional metrics row
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            st.metric(
                "Average Amount",
                f"₹{avg_amount:,.2f}",
                help="Average invoice amount"
            )
            
        with col6:
            unique_employees = df['employee_name'].nunique()
            st.metric(
                "Active Employees",
                f"{unique_employees}",
                help="Number of employees with processed invoices"
            )
            
        with col7:
            declined_count = len(df[df['reimbursement_status'] == 'Declined'])
            decline_rate = (declined_count / total_invoices) * 100 if total_invoices > 0 else 0
            st.metric(
                "Declined Invoices",
                f"{declined_count}",
                delta=f"{decline_rate:.1f}% decline rate",
                delta_color="inverse",
                help="Number of declined invoices"
            )
            
        with col8:
            # Calculate processing efficiency (no errors)
            error_count = len(df[df['reimbursement_status'] == 'Error'])
            efficiency = ((total_invoices - error_count) / total_invoices) * 100 if total_invoices > 0 else 0
            st.metric(
                "Processing Efficiency",
                f"{efficiency:.1f}%",
                help="Percentage of invoices processed without errors"
            )
    
    def render_status_overview(self, df: pd.DataFrame):
        """Render status distribution charts"""
        st.subheader("Status Distribution")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Status count pie chart
            status_counts = df['reimbursement_status'].value_counts()
            
            fig_pie = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title="Invoice Status Distribution (Count)",
                color_discrete_map={
                    'Fully Reimbursed': '#28a745',
                    'Partially Reimbursed': '#ffc107',
                    'Declined': '#dc3545',
                    'Error': '#6c757d'
                }
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with col2:
            # Status amount bar chart
            status_amounts = df.groupby('reimbursement_status')['amount'].sum()
            
            fig_bar = px.bar(
                x=status_amounts.index,
                y=status_amounts.values,
                title="Invoice Status Distribution (Amount)",
                labels={'x': 'Status', 'y': 'Amount (₹)'},
                color=status_amounts.index,
                color_discrete_map={
                    'Fully Reimbursed': '#28a745',
                    'Partially Reimbursed': '#ffc107',
                    'Declined': '#dc3545',
                    'Error': '#6c757d'
                }
            )
            fig_bar.update_layout(showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Status details table
        st.subheader("📋 Status Details")
        
        status_summary = df.groupby('reimbursement_status').agg({
            'amount': ['count', 'sum', 'mean'],
            'fraud_detected': 'sum'
        }).round(2)
        
        status_summary.columns = ['Count', 'Total Amount (₹)', 'Average Amount (₹)', 'Fraud Cases']
        
        # Add percentage columns
        total_count = len(df)
        total_amount = df['amount'].sum()
        
        status_summary['Count %'] = (status_summary['Count'] / total_count * 100).round(1)
        status_summary['Amount %'] = (status_summary['Total Amount (₹)'] / total_amount * 100).round(1)
        
        st.dataframe(status_summary, use_container_width=True)
    
    def render_employee_analytics(self, df: pd.DataFrame):
        """Render employee-based analytics"""
        st.subheader("👥 Employee Analytics")
        
        # Employee summary
        employee_stats = df.groupby('employee_name').agg({
            'amount': ['count', 'sum', 'mean'],
            'fraud_detected': 'sum'
        }).round(2)
        
        employee_stats.columns = ['Invoice Count', 'Total Amount (₹)', 'Average Amount (₹)', 'Fraud Cases']
        employee_stats = employee_stats.sort_values('Total Amount (₹)', ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top employees by amount
            top_employees = employee_stats.head(10)
            
            fig_emp = px.bar(
                x=top_employees['Total Amount (₹)'],
                y=top_employees.index,
                orientation='h',
                title="Top 10 Employees by Total Amount",
                labels={'x': 'Total Amount (₹)', 'y': 'Employee'}
            )
            fig_emp.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_emp, use_container_width=True)
            
        with col2:
            # Employee invoice count
            fig_count = px.bar(
                x=top_employees['Invoice Count'],
                y=top_employees.index,
                orientation='h',
                title="Top 10 Employees by Invoice Count",
                labels={'x': 'Invoice Count', 'y': 'Employee'}
            )
            fig_count.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_count, use_container_width=True)
        
        # Employee details table
        st.subheader("Employee Details")
        
        # Add approval rate for each employee
        employee_approval = df.groupby('employee_name').apply(
            lambda x: (len(x[x['reimbursement_status'].isin(['Fully Reimbursed', 'Partially Reimbursed'])]) / len(x)) * 100
        ).round(1)
        
        employee_stats['Approval Rate %'] = employee_approval
        
        st.dataframe(employee_stats, use_container_width=True)
    
    def render_fraud_overview(self, df: pd.DataFrame):
        """Render fraud detection overview"""
        st.subheader("🚨 Fraud Detection Overview")
        
        fraud_df = df[df['fraud_detected'] == True]
        
        if len(fraud_df) == 0:
            st.success("✅ No fraud detected in processed invoices!")
            return
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            fraud_rate = (len(fraud_df) / len(df)) * 100
            st.metric(
                "Fraud Rate",
                f"{fraud_rate:.1f}%",
                delta=f"{len(fraud_df)} cases",
                delta_color="inverse"
            )
            
        with col2:
            fraud_amount = fraud_df['amount'].sum()
            total_amount = df['amount'].sum()
            fraud_amount_rate = (fraud_amount / total_amount) * 100
            st.metric(
                "Fraudulent Amount",
                f"₹{fraud_amount:,.2f}",
                delta=f"{fraud_amount_rate:.1f}% of total",
                delta_color="inverse"
            )
            
        with col3:
            avg_fraud_amount = fraud_df['amount'].mean()
            st.metric(
                "Avg Fraud Amount",
                f"₹{avg_fraud_amount:,.2f}",
                help="Average amount of fraudulent invoices"
            )
        
        # Fraud by employee
        if len(fraud_df) > 0:
            fraud_by_employee = fraud_df.groupby('employee_name').agg({
                'amount': ['count', 'sum']
            }).round(2)
            fraud_by_employee.columns = ['Fraud Count', 'Fraud Amount (₹)']
            
            col4, col5 = st.columns(2)
            
            with col4:
                fig_fraud_emp = px.bar(
                    x=fraud_by_employee.index,
                    y=fraud_by_employee['Fraud Count'],
                    title="Fraud Cases by Employee",
                    labels={'x': 'Employee', 'y': 'Fraud Count'},
                    color_discrete_sequence=['#dc3545']
                )
                st.plotly_chart(fig_fraud_emp, use_container_width=True)
                
            with col5:
                # Fraud by invoice type
                if 'invoice_type' in fraud_df.columns:
                    fraud_by_type = fraud_df['invoice_type'].value_counts()
                    fig_fraud_type = px.pie(
                        values=fraud_by_type.values,
                        names=fraud_by_type.index,
                        title="Fraud Distribution by Invoice Type"
                    )
                    st.plotly_chart(fig_fraud_type, use_container_width=True)
    
    def render_amount_analytics(self, df: pd.DataFrame):
        """Render amount-based analytics"""
        st.subheader("💰 Amount Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Amount distribution histogram
            fig_hist = px.histogram(
                df,
                x='amount',
                nbins=30,
                title="Invoice Amount Distribution",
                labels={'x': 'Amount (₹)', 'y': 'Count'}
            )
            st.plotly_chart(fig_hist, use_container_width=True)
            
        with col2:
            # Amount by invoice type (if available)
            if 'invoice_type' in df.columns:
                type_amounts = df.groupby('invoice_type')['amount'].sum().sort_values(ascending=False)
                
                fig_type = px.bar(
                    x=type_amounts.index,
                    y=type_amounts.values,
                    title="Total Amount by Invoice Type",
                    labels={'x': 'Invoice Type', 'y': 'Total Amount (₹)'}
                )
                st.plotly_chart(fig_type, use_container_width=True)
            else:
                # Amount by status
                status_amounts = df.groupby('reimbursement_status')['amount'].sum()
                
                fig_status_amt = px.bar(
                    x=status_amounts.index,
                    y=status_amounts.values,
                    title="Total Amount by Status",
                    labels={'x': 'Status', 'y': 'Total Amount (₹)'}
                )
                st.plotly_chart(fig_status_amt, use_container_width=True)
        
        # Amount ranges analysis
        st.subheader("Amount Ranges")
        
        # Create amount range bins
        df['amount_range'] = pd.cut(
            df['amount'],
            bins=[0, 1000, 5000, 10000, 25000, float('inf')],
            labels=['₹0-1K', '₹1K-5K', '₹5K-10K', '₹10K-25K', '₹25K+']
        )
        
        range_analysis = df.groupby('amount_range').agg({
            'amount': ['count', 'sum', 'mean'],
            'fraud_detected': 'sum'
        }).round(2)
        
        range_analysis.columns = ['Count', 'Total Amount (₹)', 'Average Amount (₹)', 'Fraud Cases']
        
        st.dataframe(range_analysis, use_container_width=True)
    
    def render_recent_activity(self, df: pd.DataFrame):
        """Render recent activity and trends"""
        st.subheader("📅 Recent Activity")
        
        # Sort by created_at if available, otherwise by a default order
        if 'created_at' in df.columns:
            df_sorted = df.sort_values('created_at', ascending=False)
        else:
            df_sorted = df.head(10)  # Show first 10 if no timestamp
        
        # Recent invoices table
        recent_invoices = df_sorted.head(10)[
            ['invoice_id', 'employee_name', 'amount', 'reimbursement_status', 'fraud_detected']
        ]
        
        st.subheader("🔔 Recent Invoices")
        
        # Format the table for better display
        for idx, row in recent_invoices.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                
                with col1:
                    st.write(f"**{row['invoice_id']}**")
                    st.caption(f"Employee: {row['employee_name']}")
                
                with col2:
                    st.write(f"₹{row['amount']:,.2f}")
                
                with col3:
                    status = row['reimbursement_status']
                    if status == "Fully Reimbursed":
                        st.success("✅ Approved")
                    elif status == "Partially Reimbursed":
                        st.warning("⚠️ Partial")
                    elif status == "Declined":
                        st.error("❌ Declined")
                    else:
                        st.info("ℹ️ Processing")
                
                with col4:
                    if row['fraud_detected']:
                        st.error("🚨 Fraud")
                    else:
                        st.success("✅ Clean")
                
                st.divider()
        
        # Summary insights
        st.subheader("💡 Insights")
        
        insights = []
        
        # Generate insights based on data
        total_invoices = len(df)
        approval_rate = (len(df[df['reimbursement_status'].isin(['Fully Reimbursed', 'Partially Reimbursed'])]) / total_invoices) * 100
        
        if approval_rate > 80:
            insights.append("✅ High approval rate indicates good policy compliance")
        elif approval_rate < 50:
            insights.append("⚠️ Low approval rate - consider reviewing expense policies")
        
        fraud_rate = (df['fraud_detected'].sum() / total_invoices) * 100
        if fraud_rate > 10:
            insights.append("🚨 High fraud rate detected - implement additional controls")
        elif fraud_rate == 0:
            insights.append("✅ No fraud detected in current batch")
        
        avg_amount = df['amount'].mean()
        if avg_amount > 5000:
            insights.append("📈 High average claim amount - monitor for unusual patterns")
        
        # Employee concentration
        top_employee_share = df.groupby('employee_name')['amount'].sum().max() / df['amount'].sum()
        if top_employee_share > 0.3:
            insights.append("⚠️ High concentration of claims from single employee")
        
        if insights:
            for insight in insights:
                st.info(insight)
        else:
            st.info("All metrics appear normal - no specific recommendations at this time")


def render_dashboard():
    """Main function to render the dashboard"""
    # Initialize API client
    api_client = st.session_state.api_client
    
    # Create and render dashboard
    dashboard = Dashboard(api_client)
    dashboard.render()
    
    # Refresh button
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("Refresh Data", help="Reload dashboard data"):
            st.rerun()
    
    with col2:
        if st.button("Export Analytics", help="Export dashboard data"):
            export_dashboard_data(api_client)
    
    # Auto-refresh option
    with col3:
        auto_refresh = st.checkbox("Auto-refresh (30s)", help="Automatically refresh data every 30 seconds")
        
        if auto_refresh:
            import time
            time.sleep(30)
            st.rerun()


def export_dashboard_data(api_client):
    """Export dashboard data to CSV"""
    try:
        response = api_client.get_invoices()
        
        if response.get("success"):
            invoices = response.get("invoices", [])
            
            if invoices:
                # Convert to DataFrame
                df = pd.DataFrame(invoices)
                
                # Create CSV
                csv = df.to_csv(index=False)
                
                # Create download button
                st.download_button(
                    label="📥 Download Dashboard Data",
                    data=csv,
                    file_name=f"dashboard_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
                st.success("Dashboard data exported successfully!")
            else:
                st.warning("No data available for export")
        else:
            st.error("Failed to export data")
            
    except Exception as e:
        st.error(f"Error exporting data: {str(e)}")
