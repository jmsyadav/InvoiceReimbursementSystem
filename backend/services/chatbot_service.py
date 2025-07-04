import uuid
from typing import Dict, Any, List
from .vector_service import VectorService
from .llm_service import LLMService

class ChatbotService:
    """Service for handling chatbot interactions with RAG capabilities"""
    
    def __init__(self):
        self.vector_service = VectorService()
        self.llm_service = LLMService()
        self.conversation_store = {}  # In-memory store for conversations
    
    async def process_query(self, query: str, filters: Dict[str, Any] = None, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Process user query with RAG capabilities
        
        Args:
            query: User's natural language query
            filters: Optional metadata filters
            conversation_history: Previous conversation turns
            
        Returns:
            Dictionary with response and sources
        """
        try:
            # Generate conversation ID if not provided
            conversation_id = str(uuid.uuid4())
            
            # Parse query to extract potential filters
            extracted_filters = self._extract_filters_from_query(query)
            
            # Combine extracted filters with provided filters
            combined_filters = {**(filters or {}), **extracted_filters}
            
            # Search for relevant invoice data
            search_results = await self.vector_service.search_similar_invoices(
                query=query,
                filters=combined_filters,
                limit=5
            )
            
            # Build context from search results
            context = self._build_context_from_results(search_results)
            
            # Generate response using LLM
            response = await self.llm_service.generate_chatbot_response(
                query=query,
                context=context,
                conversation_history=conversation_history
            )
            
            # Store conversation
            self._store_conversation(conversation_id, query, response)
            
            # Prepare sources
            sources = self._prepare_sources(search_results)
            
            return {
                "answer": response,
                "sources": sources,
                "conversation_id": conversation_id,
                "filters_used": combined_filters
            }
            
        except Exception as e:
            return {
                "answer": f"I apologize, but I encountered an error while processing your query: {str(e)}",
                "sources": [],
                "conversation_id": str(uuid.uuid4()),
                "filters_used": {}
            }
    
    def _extract_filters_from_query(self, query: str) -> Dict[str, Any]:
        """Extract potential filters from natural language query"""
        filters = {}
        query_lower = query.lower()
        
        # Extract employee names (simple pattern matching)
        if "employee" in query_lower or "person" in query_lower:
            # Look for names after "by", "for", "from"
            import re
            name_patterns = [
                r'\b(?:by|for|from)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:invoice|expense|claim)'
            ]
            
            for pattern in name_patterns:
                matches = re.findall(pattern, query)
                if matches:
                    filters["employee_name"] = matches[0]
                    break
        
        # Extract status filters
        if "approved" in query_lower or "fully reimbursed" in query_lower:
            filters["reimbursement_status"] = "Fully Reimbursed"
        elif "rejected" in query_lower or "declined" in query_lower:
            filters["reimbursement_status"] = "Declined"
        elif "partial" in query_lower:
            filters["reimbursement_status"] = "Partially Reimbursed"
        
        # Extract fraud filters
        if "fraud" in query_lower or "suspicious" in query_lower:
            filters["fraud_detected"] = True
        
        # Extract invoice type filters
        if "travel" in query_lower or "trip" in query_lower:
            filters["invoice_type"] = "travel"
        elif "meal" in query_lower or "food" in query_lower:
            filters["invoice_type"] = "meal"
        elif "cab" in query_lower or "taxi" in query_lower:
            filters["invoice_type"] = "cab"
        
        # Extract amount filters
        import re
        amount_matches = re.findall(r'(?:above|over|more than|greater than)\s*₹?\s*(\d+)', query_lower)
        if amount_matches:
            filters["amount_min"] = int(amount_matches[0])
        
        amount_matches = re.findall(r'(?:below|under|less than)\s*₹?\s*(\d+)', query_lower)
        if amount_matches:
            filters["amount_max"] = int(amount_matches[0])
        
        return filters
    
    def _build_context_from_results(self, search_results: List[Dict[str, Any]]) -> str:
        """Build context string from search results"""
        if not search_results:
            return "No relevant invoice data found."
        
        context_parts = []
        
        for i, result in enumerate(search_results, 1):
            metadata = result.get("metadata", {})
            content = result.get("content", "")
            
            context_part = f"""
            **Invoice {i}:**
            - Invoice ID: {metadata.get('invoice_id', 'Unknown')}
            - Employee: {metadata.get('employee_name', 'Unknown')}
            - Date: {metadata.get('invoice_date', 'Unknown')}
            - Amount: ₹{metadata.get('amount', 0)}
            - Status: {metadata.get('reimbursement_status', 'Unknown')}
            - Fraud Detected: {metadata.get('fraud_detected', False)}
            - Content: {content}
            """
            
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    def _prepare_sources(self, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare source information for response"""
        sources = []
        
        for result in search_results:
            metadata = result.get("metadata", {})
            source = {
                "invoice_id": metadata.get("invoice_id", "Unknown"),
                "employee_name": metadata.get("employee_name", "Unknown"),
                "invoice_date": metadata.get("invoice_date", "Unknown"),
                "amount": metadata.get("amount", 0),
                "reimbursement_status": metadata.get("reimbursement_status", "Unknown"),
                "similarity_score": result.get("score", 0.0)
            }
            sources.append(source)
        
        return sources
    
    def _store_conversation(self, conversation_id: str, query: str, response: str):
        """Store conversation in memory"""
        if conversation_id not in self.conversation_store:
            self.conversation_store[conversation_id] = []
        
        self.conversation_store[conversation_id].append({
            "user": query,
            "assistant": response
        })
        
        # Keep only last 10 turns to prevent memory issues
        if len(self.conversation_store[conversation_id]) > 10:
            self.conversation_store[conversation_id] = self.conversation_store[conversation_id][-10:]
    
    def get_conversation_history(self, conversation_id: str) -> List[Dict[str, str]]:
        """Get conversation history for a given conversation ID"""
        return self.conversation_store.get(conversation_id, [])
