"""
Chat service for handling RAG-powered conversations about invoice analyses
"""

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from models import ChatRequest, ChatMessage
from services.llm_service import LLMService
from services.vector_service import VectorService

class ChatService:
    """Service for handling chat interactions with RAG capabilities"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.vector_service = VectorService()
        
        # In-memory conversation storage (in production, use Redis or database)
        self.conversations: Dict[str, List[ChatMessage]] = {}
    
    async def process_chat_request(self, request: ChatRequest) -> str:
        """
        Process a chat request using RAG (Retrieval-Augmented Generation)
        
        Args:
            request: ChatRequest containing user query and conversation history
            
        Returns:
            Generated response string
        """
        try:
            # Extract search parameters from the query
            search_filters = self._extract_search_filters(request.query)
            
            # Search for relevant invoice analyses
            context = await self.vector_service.search_for_chat(
                query=request.query,
                filters=search_filters,
                limit=5
            )
            
            # Generate response using LLM with context
            response = await self.llm_service.generate_chat_response(
                query=request.query,
                context=context,
                conversation_history=request.conversation_history
            )
            
            return response
            
        except Exception as e:
            print(f"❌ Error processing chat request: {e}")
            return f"I apologize, but I encountered an error while processing your request: {str(e)}"
    
    def _extract_search_filters(self, query: str) -> Dict[str, Any]:
        """
        Extract search filters from user query using keyword matching
        
        Args:
            query: User's natural language query
            
        Returns:
            Dictionary of extracted filters
        """
        filters = {}
        query_lower = query.lower()
        
        # Extract employee name patterns
        employee_patterns = [
            r"employee\s+(\w+)",
            r"person\s+(\w+)",
            r"invoices?\s+by\s+(\w+)",
            r"(\w+)'s\s+invoices?",
            r"invoices?\s+from\s+(\w+)"
        ]
        
        import re
        for pattern in employee_patterns:
            match = re.search(pattern, query_lower)
            if match:
                filters["employee_name"] = match.group(1).title()
                break
        
        # Extract status filters
        if "fully reimbursed" in query_lower:
            filters["status"] = "Fully Reimbursed"
        elif "partially reimbursed" in query_lower:
            filters["status"] = "Partially Reimbursed"
        elif "declined" in query_lower:
            filters["status"] = "Declined"
        
        # Extract fraud-related filters
        if "fraud" in query_lower or "fraudulent" in query_lower:
            filters["is_fraudulent"] = True
        
        return filters
    
    async def get_conversation_history(self, conversation_id: str) -> List[ChatMessage]:
        """
        Get conversation history for a specific conversation
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            List of chat messages
        """
        return self.conversations.get(conversation_id, [])
    
    async def save_conversation_message(
        self, 
        conversation_id: str, 
        message: ChatMessage
    ):
        """
        Save a message to conversation history
        
        Args:
            conversation_id: Unique identifier for the conversation
            message: ChatMessage to save
        """
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        
        self.conversations[conversation_id].append(message)
        
        # Keep only last 20 messages to prevent memory issues
        if len(self.conversations[conversation_id]) > 20:
            self.conversations[conversation_id] = self.conversations[conversation_id][-20:]
    
    async def clear_conversation(self, conversation_id: str):
        """
        Clear conversation history for a specific conversation
        
        Args:
            conversation_id: Unique identifier for the conversation
        """
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
    
    def _format_invoice_context(self, search_results: List[Dict[str, Any]]) -> str:
        """
        Format search results into a readable context for the LLM
        
        Args:
            search_results: List of search results from vector database
            
        Returns:
            Formatted context string
        """
        if not search_results:
            return "No relevant invoice analyses found."
        
        context = "### Relevant Invoice Analyses:\n\n"
        
        for i, result in enumerate(search_results, 1):
            metadata = result.get('metadata', {})
            
            context += f"""
**Invoice {i}:**
- **ID:** {metadata.get('invoice_id', 'N/A')}
- **Employee:** {metadata.get('employee_name', 'N/A')}
- **Date:** {metadata.get('invoice_date', 'N/A')}
- **Amount:** ₹{metadata.get('amount', 'N/A')}
- **Status:** {metadata.get('status', 'N/A')}
- **Reason:** {metadata.get('reason', 'N/A')}
- **Fraud Detected:** {metadata.get('is_fraudulent', False)}
- **Relevance Score:** {result.get('score', 'N/A')}

"""
        
        return context
    
    def _is_greeting(self, query: str) -> bool:
        """Check if the query is a greeting"""
        greetings = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]
        return any(greeting in query.lower() for greeting in greetings)
    
    def _is_help_request(self, query: str) -> bool:
        """Check if the query is asking for help"""
        help_keywords = ["help", "how to", "what can you do", "capabilities", "commands"]
        return any(keyword in query.lower() for keyword in help_keywords)
    
    def _get_help_response(self) -> str:
        """Generate a help response"""
        return """
# Invoice Analysis Assistant Help

I can help you query and analyze invoice reimbursement data. Here are some example queries:

## Search by Employee
- "Show me invoices by John"
- "What are John's invoice statuses?"

## Search by Status
- "Show me all declined invoices"
- "Which invoices were fully reimbursed?"

## Search by Amount
- "Show me invoices over ₹1000"
- "What are the highest amount invoices?"

## Fraud Detection
- "Show me fraudulent invoices"
- "Which invoices have fraud detected?"

## General Queries
- "What's the summary of all invoices?"
- "Show me recent invoice analyses"

Feel free to ask questions in natural language, and I'll search through the processed invoice data to provide you with relevant information!
"""
    
    async def handle_special_queries(self, query: str) -> Optional[str]:
        """
        Handle special queries like greetings or help requests
        
        Args:
            query: User query
            
        Returns:
            Special response if applicable, None otherwise
        """
        if self._is_greeting(query):
            return "Hello! I'm your Invoice Analysis Assistant. I can help you search and analyze processed invoices. What would you like to know?"
        
        if self._is_help_request(query):
            return self._get_help_response()
        
        return None
