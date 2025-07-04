import os
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import numpy as np
from ..database.qdrant_client import QdrantClient

class VectorService:
    """Service for handling vector embeddings and similarity search"""
    
    def __init__(self):
        self.embedding_model = None
        self.qdrant_client = QdrantClient()
        self.collection_name = "invoice_analysis"
    
    async def initialize(self):
        """Initialize the embedding model and vector store"""
        try:
            # Use a lightweight, free embedding model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize Qdrant collection
            await self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vector_size=384  # Dimension of all-MiniLM-L6-v2
            )
            
        except Exception as e:
            raise Exception(f"Failed to initialize vector service: {str(e)}")
    
    async def store_analysis_results(self, results: List[Dict[str, Any]]):
        """
        Store invoice analysis results in vector database
        
        Args:
            results: List of invoice analysis results
        """
        try:
            for result in results:
                # Create content for embedding
                content = self._create_embedding_content(result)
                
                # Generate embedding
                embedding = self.embedding_model.encode(content).tolist()
                
                # Prepare metadata
                metadata = {
                    "invoice_id": result["invoice_id"],
                    "employee_name": result["employee_name"],
                    "invoice_date": result["invoice_date"],
                    "amount": result["amount"],
                    "reimbursement_status": result["reimbursement_status"],
                    "fraud_detected": result["fraud_detected"],
                    "invoice_type": result["invoice_data"].get("invoice_type", "general")
                }
                
                # Store in Qdrant
                await self.qdrant_client.upsert_vector(
                    collection_name=self.collection_name,
                    vector_id=f"invoice_{result['invoice_id']}_{hash(content)}",
                    vector=embedding,
                    metadata=metadata,
                    content=content
                )
                
        except Exception as e:
            raise Exception(f"Failed to store analysis results: {str(e)}")
    
    def _create_embedding_content(self, result: Dict[str, Any]) -> str:
        """Create text content for embedding generation"""
        content_parts = [
            f"Invoice ID: {result['invoice_id']}",
            f"Employee: {result['employee_name']}",
            f"Date: {result['invoice_date']}",
            f"Amount: ₹{result['amount']}",
            f"Status: {result['reimbursement_status']}",
            f"Reason: {result['reason']}",
            f"Type: {result['invoice_data'].get('invoice_type', 'general')}"
        ]
        
        if result['fraud_detected']:
            content_parts.append(f"Fraud detected: {result['fraud_reason']}")
        
        # Add invoice description if available
        if result['invoice_data'].get('description'):
            content_parts.append(f"Description: {result['invoice_data']['description']}")
        
        return " | ".join(content_parts)
    
    async def search_similar_invoices(self, query: str, filters: Dict[str, Any] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for similar invoices using vector similarity and metadata filters
        
        Args:
            query: Search query
            filters: Metadata filters
            limit: Maximum number of results
            
        Returns:
            List of similar invoice records
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Prepare Qdrant filters
            qdrant_filters = None
            if filters:
                qdrant_filters = self._build_qdrant_filters(filters)
            
            # Search in Qdrant
            results = await self.qdrant_client.search_vectors(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                filters=qdrant_filters,
                limit=limit
            )
            
            return results
            
        except Exception as e:
            raise Exception(f"Vector search failed: {str(e)}")
    
    def _build_qdrant_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Build Qdrant filter conditions from user filters"""
        conditions = []
        
        if "employee_name" in filters:
            conditions.append({
                "key": "employee_name",
                "match": {"value": filters["employee_name"]}
            })
        
        if "reimbursement_status" in filters:
            conditions.append({
                "key": "reimbursement_status",
                "match": {"value": filters["reimbursement_status"]}
            })
        
        if "fraud_detected" in filters:
            conditions.append({
                "key": "fraud_detected",
                "match": {"value": filters["fraud_detected"]}
            })
        
        if "invoice_type" in filters:
            conditions.append({
                "key": "invoice_type",
                "match": {"value": filters["invoice_type"]}
            })
        
        if "amount_min" in filters:
            conditions.append({
                "key": "amount",
                "range": {"gte": filters["amount_min"]}
            })
        
        if "amount_max" in filters:
            conditions.append({
                "key": "amount",
                "range": {"lte": filters["amount_max"]}
            })
        
        if conditions:
            return {"must": conditions}
        
        return None
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector collection"""
        try:
            stats = await self.qdrant_client.get_collection_info(self.collection_name)
            return stats
        except Exception as e:
            return {"error": str(e)}
