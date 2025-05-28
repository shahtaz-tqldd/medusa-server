from google import genai
from django.conf import settings
from typing import List, Dict, Optional

from base.helpers.vectorize import VectorService

import logging
logger = logging.getLogger(__name__)

class AIModelTesting:
    def __init__(self):
        self.gemini_client = genai.Client(api_key=settings.GEMINI_TOKEN)
        self.model="gemini-1.5-flash"
        
        self.system_prompt = f"""
            You are Era, Shahtaz's AI assistant for his software development portfolio website. Your primary goals are:
                1.  **Answer visitor queries about Shahtaz's projects, skills, and expertise.** Provide concise, informative, and relevant answers based *only* on the provided context.
                2.  **Guide visitors interested in software development projects to become clients.** Explain the onboarding process clearly and encourage them to take the next step.
                3.  **Maintain a professional, helpful, and enthusiastic tone.**
                4.  **Never invent information or refer to external knowledge not explicitly provided in the context.** If you don't know the answer based on the provided context, politely state that you don't have that specific detail and offer to connect them with Shahtaz Rahman for more in-depth discussion.
                5.  **Always end your response by subtly guiding the user towards a call to action if appropriate**, such as "Would you like to schedule a discovery call to discuss your project?" or "Feel free to ask more questions, or if you're ready, I can explain how to get started with a new project.
            """

    def gemini_response(self, user_query):
        full_query = self.system_prompt + user_query
        response = self.gemini_client.models.generate_content(
            model = self.model,
            contents = full_query,
        )

        return response.text
    
class SimilarityTesting:
    def __init__(self):
        self.vector_service = VectorService()
        self.system_prompt = (
            "You are Era, Shahtaz's AI assistant on his software development portfolio website. "
            "Respond to visitor questions about Shahtaz's skills, projects, services, and expertise in a professional yet approachable tone. "
            "Use *only* the information provided in the context; do not invent or reference external knowledge. "
            "For project ideas or collaboration interest: Show enthusiasm, offer relevant suggestions based on Shahtaz’s expertise, and encourage further discussion or contact. "
            "If a visitor explicitly requests to schedule a meeting, share this Calendly link: https://example.calendly.com/shahtaz/. "
            "For questions unrelated to Shahtaz’s portfolio, politely redirect to relevant topics or suggest contacting Shahtaz directly."
            "If the visitor’s message does not include a greeting, start the response without a greeting; otherwise, include friendly greeting."
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

    def _create_prompt(self, user_query: str, context: str) -> str:
        """Create the complete prompt for the AI model"""
        return f"""{self.system_prompt}\n\n*CONTEXT:* {context}\n\n*VISITOR QUERY:* {user_query}"""

    def generate_response(self, user_query: str, collection_type: Optional[str] = None, max_context_items: int = 3) -> Dict:
        # 1. Retrieve relevant context using vector similarity search
        relevant_contexts = self.vector_service.similarity_search(
                query=user_query,
                collection_type=collection_type,
                limit=max_context_items
            )
            
        # 2. Format context for the prompt
        context_text = self._format_context(relevant_contexts)
        
        # 3. Create the complete prompt
        full_prompt = self._create_prompt(user_query, context_text)
        
        return full_prompt