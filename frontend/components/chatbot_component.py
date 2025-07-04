import streamlit as st
from frontend.services.api_client import APIClient

def render_chatbot_section():
    """Render the chatbot query section"""
    st.header("🤖 Chatbot Query")
    
    # Initialize API client
    api_client = st.session_state.api_client
    
    # Instructions
    st.markdown("""
    **Ask questions about your processed invoices:**
    - "Show me all invoices for John Doe"
    - "Which invoices were declined?"
    - "What are the fraud cases?"
    - "Show me travel expenses over ₹2000"
    - "List all partially reimbursed invoices"
    """)
    
    # Chat interface
    render_chat_interface(api_client)

def render_chat_interface(api_client):
    """Render the chat interface"""
    
    # Chat history container
    chat_container = st.container()
    
    # Display chat history
    with chat_container:
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your invoices..."):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process query and get response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Prepare conversation history for API
                    conversation_history = []
                    for msg in st.session_state.chat_history[-10:]:  # Last 10 messages
                        if msg["role"] == "user":
                            conversation_history.append({"user": msg["content"], "assistant": ""})
                        elif msg["role"] == "assistant" and conversation_history:
                            conversation_history[-1]["assistant"] = msg["content"]
                    
                    # Call chatbot API
                    response = api_client.query_chatbot(
                        query=prompt,
                        conversation_history=conversation_history[:-1]  # Exclude current query
                    )
                    
                    if response.get("success"):
                        answer = response.get("response", "I couldn't process your query.")
                        sources = response.get("sources", [])
                        
                        # Display answer
                        st.markdown(answer)
                        
                        # Display sources if available
                        if sources:
                            render_sources_section(sources)
                        
                        # Add assistant response to chat history
                        st.session_state.chat_history.append({"role": "assistant", "content": answer})
                        
                    else:
                        error_msg = "I apologize, but I encountered an error while processing your query. Please try again."
                        st.error(error_msg)
                        st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
                
                except Exception as e:
                    error_msg = f"Error processing query: {str(e)}"
                    st.error(error_msg)
                    st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
    
    # Chat controls
    render_chat_controls()

def render_sources_section(sources):
    """Render the sources section"""
    if not sources:
        return
    
    with st.expander("📚 Sources", expanded=False):
        st.markdown("**Relevant invoices used to answer your question:**")
        
        for i, source in enumerate(sources, 1):
            with st.container():
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.write(f"**{i}. {source.get('invoice_id', 'Unknown')}**")
                    st.write(f"Employee: {source.get('employee_name', 'Unknown')}")
                
                with col2:
                    st.write(f"Date: {source.get('invoice_date', 'Unknown')}")
                    st.write(f"Amount: ₹{source.get('amount', 0)}")
                
                with col3:
                    status = source.get('reimbursement_status', 'Unknown')
                    if status == "Fully Reimbursed":
                        st.success("✅ Approved")
                    elif status == "Partially Reimbursed":
                        st.warning("⚠️ Partial")
                    elif status == "Declined":
                        st.error("❌ Declined")
                    else:
                        st.info("ℹ️ Unknown")
                
                # Similarity score
                similarity_score = source.get('similarity_score', 0)
                if similarity_score > 0:
                    st.caption(f"Relevance: {similarity_score:.2f}")
                
                st.markdown("---")

def render_chat_controls():
    """Render chat control buttons"""
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🗑️ Clear Chat", help="Clear the chat history"):
            st.session_state.chat_history = []
            st.rerun()
    
    with col2:
        if st.button("💾 Export Chat", help="Export chat history"):
            export_chat_history()
    
    with col3:
        # Sample queries
        sample_queries = [
            "Show me all declined invoices",
            "Which employees have fraud cases?",
            "What are the highest expense claims?",
            "Show me all travel expenses",
            "List invoices from this month"
        ]
        
        selected_query = st.selectbox(
            "💡 Try a sample query:",
            [""] + sample_queries,
            help="Select a sample query to get started"
        )
        
        if selected_query and st.button("Send Sample Query"):
            # Add sample query to chat
            st.session_state.chat_history.append({"role": "user", "content": selected_query})
            st.rerun()

def export_chat_history():
    """Export chat history to downloadable format"""
    if not st.session_state.chat_history:
        st.warning("No chat history to export.")
        return
    
    # Create export content
    export_content = "# Invoice Reimbursement Chat History\n\n"
    
    for i, message in enumerate(st.session_state.chat_history, 1):
        role = "**User**" if message["role"] == "user" else "**Assistant**"
        export_content += f"{i}. {role}: {message['content']}\n\n"
    
    # Create download button
    st.download_button(
        label="📥 Download Chat History",
        data=export_content,
        file_name="chat_history.md",
        mime="text/markdown"
    )

# Advanced query features
def render_advanced_features():
    """Render advanced chatbot features"""
    st.subheader("🔧 Advanced Features")
    
    with st.expander("Filter Options"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.selectbox("Employee", ["All", "John Doe", "Jane Smith"])
            st.selectbox("Status", ["All", "Fully Reimbursed", "Partially Reimbursed", "Declined"])
        
        with col2:
            st.date_input("From Date")
            st.date_input("To Date")
        
        st.slider("Amount Range", 0, 10000, (0, 10000))
        st.checkbox("Include Fraud Cases Only")
    
    with st.expander("Query Examples"):
        st.markdown("""
        **Employee-specific queries:**
        - "Show all invoices by John Doe"
        - "What's the total amount claimed by Jane Smith?"
        
        **Status-based queries:**
        - "List all declined invoices"
        - "Show me partially reimbursed claims"
        
        **Amount-based queries:**
        - "Find invoices over ₹5000"
        - "What are the smallest expense claims?"
        
        **Date-based queries:**
        - "Show invoices from last month"
        - "Find claims submitted this week"
        
        **Fraud-related queries:**
        - "Show me all fraud cases"
        - "Which employees have suspicious claims?"
        """)
