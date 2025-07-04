"""
Chatbot component for the Streamlit frontend
"""

import streamlit as st
import requests
import json
from typing import List, Dict, Any
from datetime import datetime

class ChatBot:
    """Component for handling chatbot functionality"""
    
    def __init__(self, backend_url: str):
        self.backend_url = backend_url
    
    def render(self):
        """Render the chatbot interface"""
        # Check if there are processed invoices
        if not st.session_state.get('processed_invoices'):
            st.info("📋 No processed invoices found. Please analyze some invoices first using the Invoice Analyzer.")
            return
        
        # Chat interface
        self.render_chat_interface()
        
        # Quick actions
        self.render_quick_actions()
    
    def render_chat_interface(self):
        """Render the main chat interface"""
        st.subheader("💬 Chat with Your Invoice Data")
        
        # Chat history display
        chat_container = st.container()
        
        with chat_container:
            # Display chat history
            if st.session_state.chat_history:
                for message in st.session_state.chat_history:
                    self.render_chat_message(message)
            else:
                st.info("👋 Hi! I'm your AI assistant. Ask me questions about your processed invoices.")
        
        # Chat input
        self.render_chat_input()
    
    def render_chat_message(self, message: Dict[str, Any]):
        """Render a single chat message"""
        if message['role'] == 'user':
            with st.chat_message("user", avatar="👤"):
                st.markdown(message['content'])
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(message['content'])
    
    def render_chat_input(self):
        """Render chat input area"""
        # Chat input
        user_input = st.chat_input("Ask me about your invoices...")
        
        if user_input:
            # Add user message to history
            user_message = {
                'role': 'user',
                'content': user_input,
                'timestamp': datetime.now().isoformat()
            }
            st.session_state.chat_history.append(user_message)
            
            # Get AI response
            with st.spinner("🤖 Thinking..."):
                response = self.get_ai_response(user_input)
            
            # Add assistant response to history
            assistant_message = {
                'role': 'assistant',
                'content': response,
                'timestamp': datetime.now().isoformat()
            }
            st.session_state.chat_history.append(assistant_message)
            
            # Refresh the page to show new messages
            st.rerun()
    
    def get_ai_response(self, user_input: str) -> str:
        """Get AI response from the backend"""
        try:
            # Prepare the request
            chat_request = {
                'query': user_input,
                'conversation_history': st.session_state.chat_history[-10:]  # Last 10 messages
            }
            
            # Make API request
            response = requests.post(
                f"{self.backend_url}/chat",
                json=chat_request,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['response']
            else:
                return f"Sorry, I encountered an error: {response.text}"
                
        except requests.RequestException as e:
            return f"Network error: {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def render_quick_actions(self):
        """Render quick action buttons"""
        st.subheader("⚡ Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Show Summary", use_container_width=True):
                self.ask_predefined_question("Give me a summary of all processed invoices")
        
        with col2:
            if st.button("🚨 Show Fraud Cases", use_container_width=True):
                self.ask_predefined_question("Show me all invoices with fraud detected")
        
        with col3:
            if st.button("❌ Show Declined", use_container_width=True):
                self.ask_predefined_question("Show me all declined invoices")
        
        # Additional quick actions
        st.markdown("**More Quick Actions:**")
        
        col4, col5, col6 = st.columns(3)
        
        with col4:
            if st.button("💰 High Amount Invoices", use_container_width=True):
                self.ask_predefined_question("Show me invoices with amounts over ₹5000")
        
        with col5:
            if st.button("📅 Recent Invoices", use_container_width=True):
                self.ask_predefined_question("Show me the most recent invoices")
        
        with col6:
            if st.button("👥 Employee Breakdown", use_container_width=True):
                self.ask_predefined_question("Show me a breakdown of invoices by employee")
    
    def ask_predefined_question(self, question: str):
        """Ask a predefined question"""
        # Add question to chat history
        user_message = {
            'role': 'user',
            'content': question,
            'timestamp': datetime.now().isoformat()
        }
        st.session_state.chat_history.append(user_message)
        
        # Get AI response
        with st.spinner("🤖 Analyzing..."):
            response = self.get_ai_response(question)
        
        # Add assistant response to history
        assistant_message = {
            'role': 'assistant',
            'content': response,
            'timestamp': datetime.now().isoformat()
        }
        st.session_state.chat_history.append(assistant_message)
        
        # Refresh the page to show new messages
        st.rerun()
    
    def render_chat_controls(self):
        """Render chat control buttons"""
        st.subheader("🔧 Chat Controls")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.chat_history = []
                st.success("Chat history cleared!")
                st.rerun()
        
        with col2:
            if st.button("💾 Export Chat", use_container_width=True):
                self.export_chat_history()
    
    def export_chat_history(self):
        """Export chat history to a file"""
        if not st.session_state.chat_history:
            st.warning("No chat history to export")
            return
        
        # Prepare chat data for export
        chat_data = []
        for message in st.session_state.chat_history:
            chat_data.append({
                'Role': message['role'],
                'Content': message['content'],
                'Timestamp': message['timestamp']
            })
        
        # Create CSV
        import pandas as pd
        df = pd.DataFrame(chat_data)
        csv = df.to_csv(index=False)
        
        st.download_button(
            label="📥 Download Chat History",
            data=csv,
            file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    def render_sample_questions(self):
        """Render sample questions for users"""
        st.subheader("💡 Sample Questions")
        
        sample_questions = [
            "Show me all invoices by John",
            "Which invoices were declined and why?",
            "What's the total amount of approved invoices?",
            "Show me invoices with fraud detected",
            "Which employee has the most invoices?",
            "Show me travel invoices over ₹2000",
            "What are the common reasons for declining invoices?"
        ]
        
        for question in sample_questions:
            if st.button(f"💬 {question}", key=f"sample_{question}"):
                self.ask_predefined_question(question)
    
    def render_help_section(self):
        """Render help section"""
        with st.expander("ℹ️ How to Use the AI Assistant"):
            st.markdown("""
            ### How to Chat with Your Invoice Data
            
            **Natural Language Queries:**
            - Ask questions in plain English
            - Use employee names, dates, amounts, and statuses
            - The AI will search through your processed invoices
            
            **Example Questions:**
            - "Show me all invoices by John"
            - "Which invoices were declined?"
            - "What's the total amount of approved invoices?"
            - "Show me invoices with fraud detected"
            
            **Search Capabilities:**
            - Search by employee name
            - Filter by reimbursement status
            - Find invoices by amount range
            - Detect fraud patterns
            
            **Tips:**
            - Be specific in your questions
            - Use exact employee names when possible
            - Ask for summaries and breakdowns
            - The AI remembers the conversation context
            """)
