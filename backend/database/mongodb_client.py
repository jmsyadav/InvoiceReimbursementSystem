import os
from pymongo import MongoClient
from typing import List, Dict, Any, Optional
from datetime import datetime

class MongoDBClient:
    """Client for interacting with MongoDB"""
    
    def __init__(self):
        self.client = None
        self.database = None
        self.collection = None
        self.url = os.getenv("MONGODB_URL")
        self.db_name = "invoice_reimbursement"
        self.collection_name = "invoices"
    
    async def initialize(self):
        """Initialize MongoDB client connection"""
        try:
            if not self.url:
                print("MongoDB URL not provided, skipping MongoDB initialization")
                return
                
            self.client = MongoClient(self.url, serverSelectionTimeoutMS=5000)
            self.database = self.client[self.db_name]
            self.collection = self.database[self.collection_name]
            
            # Test connection with timeout
            self.client.server_info()
            print("Connected to MongoDB")
            
            # Create indexes for better performance
            self.collection.create_index("employee_name")
            self.collection.create_index("invoice_date")
            self.collection.create_index("reimbursement_status")
            self.collection.create_index("fraud_detected")
            
        except Exception as e:
            print(f"MongoDB connection failed: {str(e)}")
            # Don't raise exception - allow app to continue without MongoDB
            self.client = None
    
    async def store_invoice_metadata(self, invoices: List[Dict[str, Any]]):
        """Store invoice metadata in MongoDB"""
        if not self.client:
            print("MongoDB not connected, skipping metadata storage")
            return
            
        try:
            documents = []
            
            for invoice in invoices:
                document = {
                    "invoice_id": invoice["invoice_id"],
                    "employee_name": invoice["employee_name"],
                    "invoice_date": invoice["invoice_date"],
                    "amount": invoice["amount"],
                    "reimbursement_status": invoice["reimbursement_status"],
                    "reason": invoice["reason"],
                    "fraud_detected": invoice["fraud_detected"],
                    "fraud_reason": invoice["fraud_reason"],
                    "invoice_type": invoice["invoice_data"].get("invoice_type", "general"),
                    "description": invoice["invoice_data"].get("description", ""),
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                # Add type-specific fields
                if invoice["invoice_data"].get("invoice_type") == "travel":
                    document.update({
                        "reporting_date": invoice["invoice_data"].get("reporting_date"),
                        "dropping_date": invoice["invoice_data"].get("dropping_date"),
                        "boarding_point": invoice["invoice_data"].get("boarding_point"),
                        "destination": invoice["invoice_data"].get("destination")
                    })
                elif invoice["invoice_data"].get("invoice_type") == "meal":
                    document.update({
                        "restaurant": invoice["invoice_data"].get("restaurant"),
                        "items": invoice["invoice_data"].get("items", [])
                    })
                elif invoice["invoice_data"].get("invoice_type") == "cab":
                    document.update({
                        "pickup_address": invoice["invoice_data"].get("pickup_address"),
                        "ride_fee": invoice["invoice_data"].get("ride_fee")
                    })
                
                documents.append(document)
            
            # Insert documents
            if documents and self.collection is not None:
                result = self.collection.insert_many(documents)
                print(f"Inserted {len(result.inserted_ids)} invoice records")
                
        except Exception as e:
            raise Exception(f"Failed to store invoice metadata: {str(e)}")
    
    async def get_all_invoices(self) -> List[Dict[str, Any]]:
        """Get all invoices from MongoDB"""
        if not self.client:
            return []
            
        try:
            invoices = list(self.collection.find({}, {"_id": 0}).sort("created_at", -1))
            return invoices
        except Exception as e:
            print(f"Failed to retrieve invoices: {str(e)}")
            return []
    
    async def get_invoices_by_employee(self, employee_name: str) -> List[Dict[str, Any]]:
        """Get invoices for a specific employee"""
        try:
            invoices = list(self.collection.find(
                {"employee_name": employee_name}, 
                {"_id": 0}
            ).sort("created_at", -1))
            return invoices
        except Exception as e:
            raise Exception(f"Failed to retrieve invoices for employee: {str(e)}")
    
    async def get_invoices_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get invoices by reimbursement status"""
        try:
            invoices = list(self.collection.find(
                {"reimbursement_status": status}, 
                {"_id": 0}
            ).sort("created_at", -1))
            return invoices
        except Exception as e:
            raise Exception(f"Failed to retrieve invoices by status: {str(e)}")
    
    async def get_fraud_invoices(self) -> List[Dict[str, Any]]:
        """Get all invoices with fraud detected"""
        try:
            invoices = list(self.collection.find(
                {"fraud_detected": True}, 
                {"_id": 0}
            ).sort("created_at", -1))
            return invoices
        except Exception as e:
            raise Exception(f"Failed to retrieve fraud invoices: {str(e)}")
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            total_count = self.collection.count_documents({})
            
            # Status distribution
            status_stats = list(self.collection.aggregate([
                {"$group": {"_id": "$reimbursement_status", "count": {"$sum": 1}}}
            ]))
            
            # Fraud statistics
            fraud_count = self.collection.count_documents({"fraud_detected": True})
            
            # Employee statistics
            employee_stats = list(self.collection.aggregate([
                {"$group": {"_id": "$employee_name", "count": {"$sum": 1}, "total_amount": {"$sum": "$amount"}}}
            ]))
            
            return {
                "total_invoices": total_count,
                "status_distribution": {stat["_id"]: stat["count"] for stat in status_stats},
                "fraud_count": fraud_count,
                "employee_statistics": employee_stats
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def update_invoice(self, invoice_id: str, updates: Dict[str, Any]):
        """Update an invoice record"""
        try:
            updates["updated_at"] = datetime.utcnow()
            result = self.collection.update_one(
                {"invoice_id": invoice_id},
                {"$set": updates}
            )
            return result.modified_count > 0
        except Exception as e:
            raise Exception(f"Failed to update invoice: {str(e)}")
    
    async def delete_invoice(self, invoice_id: str):
        """Delete an invoice record"""
        try:
            result = self.collection.delete_one({"invoice_id": invoice_id})
            return result.deleted_count > 0
        except Exception as e:
            raise Exception(f"Failed to delete invoice: {str(e)}")
