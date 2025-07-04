import os
from groq import Groq
from typing import Dict, Any
import json

class LLMService:
    """Service for interacting with LLM via Groq API"""
    
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama3-8b-8192"  # Free tier model
    
    async def analyze_invoice(self, invoice_text: str, policy_text: str, invoice_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Analyze invoice against reimbursement policy
        
        Args:
            invoice_text: Raw text from invoice
            policy_text: HR reimbursement policy text
            invoice_data: Structured invoice data
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Construct analysis prompt
            prompt = self._build_analysis_prompt(invoice_text, policy_text, invoice_data)
            
            # Call LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert financial analyst specializing in expense reimbursement analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            # Parse response
            result = self._parse_analysis_response(response.choices[0].message.content)
            return result
            
        except Exception as e:
            return {
                "status": "Error",
                "reason": f"LLM analysis failed: {str(e)}"
            }
    
    def _build_analysis_prompt(self, invoice_text: str, policy_text: str, invoice_data: Dict[str, Any]) -> str:
        """Build the analysis prompt for the LLM"""
        return f"""
        You are analyzing an employee expense invoice against a company reimbursement policy.
        
        **REIMBURSEMENT POLICY:**
        {policy_text}
        
        **INVOICE TEXT:**
        {invoice_text}
        
        **STRUCTURED INVOICE DATA:**
        Employee: {invoice_data.get('employee_name', 'Unknown')}
        Date: {invoice_data.get('date', 'Unknown')}
        Amount: ₹{invoice_data.get('amount', 0)}
        Type: {invoice_data.get('invoice_type', 'general')}
        Description: {invoice_data.get('description', 'N/A')}
        
        **ANALYSIS INSTRUCTIONS:**
        1. Carefully review the invoice against the reimbursement policy
        2. Determine if the expense is eligible for reimbursement
        3. Consider factors like:
           - Expense category and limits
           - Required documentation
           - Business purpose
           - Approval requirements
           - Date validity
        
        **REQUIRED OUTPUT FORMAT:**
        Provide your analysis in the following JSON format:
        {{
            "status": "[Fully Reimbursed|Partially Reimbursed|Declined]",
            "reason": "Detailed explanation of the decision with specific policy references"
        }}
        
        **REIMBURSEMENT CATEGORIES:**
        - "Fully Reimbursed": The entire invoice amount is reimbursable according to policy
        - "Partially Reimbursed": Only a portion meets policy requirements (specify amount/percentage)
        - "Declined": The invoice does not meet policy requirements
        
        Provide a thorough analysis with specific policy references and clear reasoning.
        """
    
    def _parse_analysis_response(self, response_text: str) -> Dict[str, str]:
        """Parse LLM response and extract structured data"""
        try:
            # Try to extract JSON from response
            json_match = response_text.find('{')
            if json_match != -1:
                json_end = response_text.rfind('}') + 1
                json_str = response_text[json_match:json_end]
                parsed = json.loads(json_str)
                
                # Validate required fields
                if "status" in parsed and "reason" in parsed:
                    # Ensure status is valid
                    valid_statuses = ["Fully Reimbursed", "Partially Reimbursed", "Declined"]
                    if parsed["status"] in valid_statuses:
                        return parsed
            
            # Fallback parsing if JSON extraction fails
            status = "Declined"
            reason = response_text
            
            # Look for status indicators
            if "fully reimbursed" in response_text.lower():
                status = "Fully Reimbursed"
            elif "partially reimbursed" in response_text.lower():
                status = "Partially Reimbursed"
            elif "declined" in response_text.lower():
                status = "Declined"
            
            return {
                "status": status,
                "reason": reason
            }
            
        except Exception as e:
            return {
                "status": "Error",
                "reason": f"Failed to parse LLM response: {str(e)}"
            }
    
    async def generate_chatbot_response(self, query: str, context: str, conversation_history: list = None) -> str:
        """
        Generate chatbot response using retrieved context
        
        Args:
            query: User's question
            context: Retrieved context from vector search
            conversation_history: Previous conversation turns
            
        Returns:
            Generated response in markdown format
        """
        try:
            # Build conversation context
            conversation_context = ""
            if conversation_history:
                for turn in conversation_history[-5:]:  # Last 5 turns
                    conversation_context += f"User: {turn.get('user', '')}\nAssistant: {turn.get('assistant', '')}\n\n"
            
            # Construct chatbot prompt
            prompt = f"""
            You are an AI assistant specializing in invoice reimbursement analysis. Answer the user's question based on the provided context from processed invoice data.
            
            **CONVERSATION HISTORY:**
            {conversation_context}
            
            **CURRENT QUESTION:**
            {query}
            
            **RELEVANT INVOICE DATA:**
            {context}
            
            **INSTRUCTIONS:**
            1. Answer the user's question based on the provided invoice data
            2. Be specific and cite relevant details from the invoices
            3. If the question cannot be answered from the provided data, say so clearly
            4. Format your response in markdown for better readability
            5. Include relevant invoice IDs, employee names, dates, and amounts when applicable
            6. Provide actionable insights when possible
            
            **RESPONSE FORMAT:**
            Use markdown formatting with:
            - Headers for different sections
            - Bullet points for lists
            - Tables for structured data
            - Bold text for important information
            
            Provide a helpful, accurate response based on the invoice data.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert AI assistant for invoice reimbursement analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"I apologize, but I encountered an error while processing your question: {str(e)}"
