from typing import List, Dict, Optional
from django.conf import settings

from google import genai
from huggingface_hub import InferenceClient

from .summerize import summarize_conversation_task
from base.helpers.vectorize import VectorService

import logging
logger = logging.getLogger(__name__)

class QueryPrompt:
    def __init__(self):
        self.vector_service = VectorService()
        self.system_prompt = (
            "You are Era, Shahtaz's AI assistant on his software development portfolio website. Introduce yourself when visitor’s message include a greeting, otherwise never starts your message with 'Hi There'"
            "Respond to visitor questions about Shahtaz's skills, projects, services, and expertise in a professional yet approachable tone. "
            "Use *only* the information provided in the context; do not invent or reference external knowledge. "
            "For project ideas or collaboration interest: Show enthusiasm, offer relevant suggestions based on Shahtaz’s expertise, and encourage further discussion or contact. "
            "If a visitor explicitly requests to schedule a meeting, share this Calendly link: https://example.calendly.com/shahtaz/. "
            "For questions unrelated to Shahtaz’s portfolio, politely redirect to relevant topics or suggest contacting Shahtaz directly."
        )

    def _format_context(self, contexts: List) -> str:
        """Format retrieved contexts into a readable string"""
        if not contexts:
            return "No specific context available."
        
        formatted_contexts = []
        for i, ctx in enumerate(contexts, 1):
            context_block = f"""Context {i}: Title: {ctx.title}\nContent: {ctx.content}\nType: {ctx.collection_type}"""
            formatted_contexts.append(context_block.strip())

        return "\n\n".join(formatted_contexts)

    
    def generate_prompt(self, user_query: str, collection_type: Optional[str] = None, max_context_items: int = 5) -> Dict:
        relevant_contexts = self.vector_service.similarity_search(
            query=user_query,
            collection_type=collection_type,
            limit=max_context_items
        )
            
        context = self._format_context(relevant_contexts)
        
        return f"""{self.system_prompt}\n\n*CONTEXT:* {context}\n\n*VISITOR QUERY:* {user_query}"""



class HuggingFaceService:
    """Class to handle AI response generation using Hugging Face InferenceClient with Fireworks AI"""
    
    def __init__(self, model_id="meta-llama/Llama-3.1-8B-Instruct"):
        self.client = InferenceClient(
            provider="fireworks-ai",
            api_key=settings.HF_TOKEN,
            model=model_id
        )
    
    def generate_response(self, user_query, conversation_summary):
        """Generate a response to a user query"""
        query_prompt = QueryPrompt()
        prompt = query_prompt.generate_prompt(user_query)
        try:
            completion = self.client.chat.completions.create(
                model=self.client.model,
                messages=prompt,
                max_tokens=100,  # Default max length, adjustable
                temperature=0.7,  # Default temperature, adjustable
                top_p=0.95,
            )
            return completion.choices[0].message.content.strip()
            
        except Exception as e:
            logger.exception(f"Error generating response: {e}")
            return "I apologize, but I encountered an error while processing your request."


class GenAIService:
    def __init__(self):
        self.vector_service = VectorService()
        self.gemini_client = genai.Client(api_key=settings.GEMINI_TOKEN)
        self.model = "gemma-3-1b-it"

    def generate_response(self, user_query: str, conversation_summary, collection_type: Optional[str] = None, max_context_items: int = 5) -> Dict:
        """Generate AI response using RAG approach"""
        try:
            # 1. Retrieve relevant context using vector similarity search
            prompt = QueryPrompt()
            full_prompt = prompt.generate_prompt(user_query)
            
            # 4. Generate response using Gemini
            response = self.gemini_client.models.generate_content(
                model = self.model,
                contents = full_prompt,
            )
            
            # 5. Return structured response
            return response.text
            
        except Exception as e:
            return "I apologize, but I encountered an error while processing your question. Please try again or contact Shahtaz directly for assistance."




# Function to use in api view
def generate_ai_response(user_query, conversation_id, conversation_summary):
    """Generate an AI response to a user query"""
    try:
        # # generate the ai response
        # generator = HuggingFaceService()
        # response = generator.generate_response(user_query, conversation_summary)

        # # send summarization task to background
        # summarize_conversation_task.delay(
        #     conversation_id=conversation_id,
        #     prev_summary=conversation_summary,
        #     user_query=user_query,
        #     ai_response=response
        # )

        generator = GenAIService()
        response = generator.generate_response(user_query, conversation_summary)

        # return the response
        return response
    
    except Exception as e:
        logger.exception(f"Unexpected error in generate_ai_response: {e}")
        return "I'm sorry, I'm having trouble understanding your question right now. Could you please try again?"
    