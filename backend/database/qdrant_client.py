import os
from qdrant_client import QdrantClient as QdrantClientLib
from qdrant_client.models import VectorParams, Distance, PointStruct, Filter, FieldCondition, MatchValue, Range
from typing import List, Dict, Any, Optional
import uuid

class QdrantClient:
    """Client for interacting with Qdrant vector database"""
    
    def __init__(self):
        self.client = None
        self.url = os.getenv("QDRANT_URL")
        self.api_key = os.getenv("QDRANT_API_KEY")
    
    async def initialize(self):
        """Initialize Qdrant client connection"""
        try:
            self.client = QdrantClientLib(
                url=self.url,
                api_key=self.api_key,
                timeout=30
            )
            
            # Test connection
            collections = self.client.get_collections()
            print(f"Connected to Qdrant. Collections: {len(collections.collections)}")
            
        except Exception as e:
            raise Exception(f"Failed to initialize Qdrant client: {str(e)}")
    
    async def create_collection(self, collection_name: str, vector_size: int):
        """Create a new collection in Qdrant"""
        try:
            # Check if collection already exists
            try:
                self.client.get_collection(collection_name)
                print(f"Collection '{collection_name}' already exists")
                return
            except:
                pass
            
            # Create collection
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )
            
            print(f"Created collection '{collection_name}' with vector size {vector_size}")
            
        except Exception as e:
            raise Exception(f"Failed to create collection: {str(e)}")
    
    async def upsert_vector(self, collection_name: str, vector_id: str, vector: List[float], 
                          metadata: Dict[str, Any], content: str):
        """Insert or update a vector in the collection"""
        try:
            # Prepare payload
            payload = {
                "content": content,
                **metadata
            }
            
            # Create point
            point = PointStruct(
                id=vector_id,
                vector=vector,
                payload=payload
            )
            
            # Upsert point
            self.client.upsert(
                collection_name=collection_name,
                points=[point]
            )
            
        except Exception as e:
            raise Exception(f"Failed to upsert vector: {str(e)}")
    
    async def search_vectors(self, collection_name: str, query_vector: List[float], 
                           filters: Optional[Dict[str, Any]] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for similar vectors in the collection"""
        try:
            # Build filter conditions
            filter_conditions = None
            if filters:
                filter_conditions = self._build_filter_conditions(filters)
            
            # Search
            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                query_filter=filter_conditions,
                limit=limit,
                with_payload=True
            )
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_result = {
                    "id": result.id,
                    "score": result.score,
                    "metadata": result.payload,
                    "content": result.payload.get("content", "")
                }
                formatted_results.append(formatted_result)
            
            return formatted_results
            
        except Exception as e:
            raise Exception(f"Vector search failed: {str(e)}")
    
    def _build_filter_conditions(self, filters: Dict[str, Any]) -> Filter:
        """Build Qdrant filter conditions from filters dictionary"""
        conditions = []
        
        for key, value in filters.items():
            if key.endswith("_min"):
                # Range filter (minimum)
                field_name = key[:-4]  # Remove "_min" suffix
                conditions.append(
                    FieldCondition(
                        key=field_name,
                        range=Range(gte=value)
                    )
                )
            elif key.endswith("_max"):
                # Range filter (maximum)
                field_name = key[:-4]  # Remove "_max" suffix
                conditions.append(
                    FieldCondition(
                        key=field_name,
                        range=Range(lte=value)
                    )
                )
            else:
                # Exact match filter
                conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value)
                    )
                )
        
        return Filter(must=conditions) if conditions else None
    
    async def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get information about a collection"""
        try:
            info = self.client.get_collection(collection_name)
            return {
                "name": collection_name,
                "vectors_count": info.vectors_count,
                "status": info.status,
                "vector_size": info.config.params.vectors.size if info.config.params.vectors else None
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def delete_collection(self, collection_name: str):
        """Delete a collection"""
        try:
            self.client.delete_collection(collection_name)
            print(f"Deleted collection '{collection_name}'")
        except Exception as e:
            raise Exception(f"Failed to delete collection: {str(e)}")
