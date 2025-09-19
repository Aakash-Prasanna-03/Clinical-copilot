import os
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

class GeminiCopilot:
    def __init__(self):
        """Initialize the Gemini Copilot with API key and model configuration"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not found. Please set your Gemini API key.")
        
        genai.configure(api_key=api_key)
        
        # Initialize the model with specific configuration for medical contexts
        self.model = genai.GenerativeModel(
            model_name='gemini-2.0-flash',
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,  # Lower temperature for more consistent medical advice
                top_p=0.8,
                max_output_tokens=2048,
            )
        )
    
    def generate_copilot_response(self, query: str, context_results: List[Dict[str, Any]], patient_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a copilot-style response using Gemini API with retrieved context and citations
        
        Args:
            query: User's query
            context_results: List of relevant documents from vector search
            patient_data: Additional patient data for context
            
        Returns:
            Dictionary containing response, citations, and metadata
        """
        try:
            # Format the context from search results
            context_text = self._format_context(context_results)
            
            # Build the prompt with context and instructions
            prompt = self._build_prompt(query, context_text, patient_data)
            
            # Generate response using Gemini
            response = self.model.generate_content(prompt)
            
            # Extract citations from the context
            citations = self._extract_citations(context_results)
            
            # Parse the response to separate answer from any structured information
            parsed_response = self._parse_response(response.text)
            
            return {
                "query": query,
                "answer": parsed_response["answer"],
                "citations": citations,
                "context_used": len(context_results),
                "confidence": self._calculate_confidence(context_results),
                "response_metadata": {
                    "model": "gemini-2.0-flash",
                    "temperature": 0.3,
                    "context_sources": [result["type"] for result in context_results]
                }
            }
            
        except Exception as e:
            return {
                "query": query,
                "error": f"Error generating response: {str(e)}",
                "answer": "I apologize, but I encountered an error while processing your query. Please try again or rephrase your question.",
                "citations": [],
                "context_used": 0,
                "confidence": 0.0
            }
    
    def _format_context(self, context_results: List[Dict[str, Any]]) -> str:
        """Format the search results into readable context for the prompt"""
        if not context_results:
            return "No specific patient data found for this query."
        
        context_sections = []
        context_sections.append("=== RELEVANT PATIENT DATA ===")
        
        # Group by type for better organization
        grouped_context = {}
        for result in context_results:
            result_type = result.get("type", "unknown")
            if result_type not in grouped_context:
                grouped_context[result_type] = []
            grouped_context[result_type].append(result)
        
        # Format each type section
        for data_type, results in grouped_context.items():
            context_sections.append(f"\n{data_type.upper()}:")
            for i, result in enumerate(results, 1):
                relevance = result.get("relevance", 0)
                context_sections.append(f"  {i}. {result['text']} (relevance: {relevance:.2f})")
        
        return "\n".join(context_sections)
    
    def _build_prompt(self, query: str, context_text: str, patient_data: Dict[str, Any] = None) -> str:
        """Build the complete prompt for Gemini"""
        prompt_parts = [
            "You are a Clinical AI Copilot assistant helping healthcare professionals analyze patient data.",
            "Your role is to provide helpful, accurate, and evidence-based responses based on the available patient information.",
            "",
            "IMPORTANT GUIDELINES:",
            "- Base your response primarily on the provided patient data context",
            "- Always indicate when you're referencing specific patient data",
            "- Be clear about limitations and when more information might be needed",
            "- Use medical terminology appropriately but explain complex concepts",
            "- Never provide definitive diagnoses - suggest considerations and recommendations for healthcare providers",
            "- If the context doesn't contain relevant information, clearly state this limitation",
            "",
            "PATIENT DATA CONTEXT:",
            context_text,
            "",
            f"USER QUERY: {query}",
            "",
            "Please provide a comprehensive response that:",
            "1. Directly addresses the user's query",
            "2. References specific patient data when relevant",
            "3. Provides clinical insights and considerations",
            "4. Suggests next steps or additional information that might be helpful",
            "5. Clearly indicates the source of information (patient data vs. general medical knowledge)",
            "",
            "Response:"
        ]
        
        return "\n".join(prompt_parts)
    
    def _extract_citations(self, context_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract citation information from context results"""
        citations = []
        
        for i, result in enumerate(context_results, 1):
            citation = {
                "id": i,
                "text": result["text"],
                "type": result["type"],
                "relevance": result["relevance"],
                "source": f"Patient Data - {result['type'].title()}"
            }
            
            # Add any additional metadata
            if "metadata" in result and result["metadata"]:
                citation["metadata"] = result["metadata"]
            
            citations.append(citation)
        
        return citations
    
    def _parse_response(self, response_text: str) -> Dict[str, str]:
        """Parse the response text to extract structured information"""
        # For now, return the response as-is, but this could be enhanced
        # to parse structured responses, extract key points, etc.
        return {
            "answer": response_text.strip()
        }
    
    def _calculate_confidence(self, context_results: List[Dict[str, Any]]) -> float:
        """Calculate a confidence score based on the quality of context results"""
        if not context_results:
            return 0.0
        
        # Calculate confidence based on relevance scores
        relevance_scores = [result.get("relevance", 0) for result in context_results]
        avg_relevance = sum(relevance_scores) / len(relevance_scores)
        
        # Factor in the number of results (more context generally means higher confidence)
        context_factor = min(len(context_results) / 5.0, 1.0)  # Cap at 5 results
        
        # Combined confidence score
        confidence = (avg_relevance * 0.7) + (context_factor * 0.3)
        
        return round(confidence, 2)

    def generate_simple_response(self, query: str, patient_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a simple response without vector search context (fallback method)
        
        Args:
            query: User's query
            patient_data: Patient data dictionary
            
        Returns:
            Dictionary containing response and metadata
        """
        try:
            # Create a simple context from patient data if available
            context_text = ""
            if patient_data:
                context_sections = []
                context_sections.append("=== AVAILABLE PATIENT DATA ===")
                
                if patient_data.get('conditions'):
                    context_sections.append(f"\nCONDITIONS: {', '.join(patient_data['conditions'])}")
                
                if patient_data.get('medications'):
                    context_sections.append(f"\nMEDICATIONS: {', '.join(patient_data['medications'])}")
                
                if patient_data.get('allergies'):
                    context_sections.append(f"\nALLERGIES: {', '.join(patient_data['allergies'])}")
                
                if patient_data.get('observations'):
                    context_sections.append(f"\nOBSERVATIONS: {', '.join(patient_data['observations'][:5])}")  # Limit to first 5
                
                context_text = "\n".join(context_sections)
            
            # Build simplified prompt
            prompt = self._build_prompt(query, context_text or "No specific patient data available.", patient_data)
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            return {
                "query": query,
                "answer": response.text.strip(),
                "citations": [],
                "context_used": 0,
                "confidence": 0.5,  # Medium confidence for general responses
                "response_metadata": {
                    "model": "gemini-2.0-flash",
                    "temperature": 0.3,
                    "fallback_mode": True
                }
            }
            
        except Exception as e:
            return {
                "query": query,
                "error": f"Error generating response: {str(e)}",
                "answer": "I apologize, but I encountered an error while processing your query. Please try again or rephrase your question.",
                "citations": [],
                "context_used": 0,
                "confidence": 0.0
            }
