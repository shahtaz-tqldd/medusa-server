from typing import List, Dict, Optional
from django.conf import settings

from google import genai
from huggingface_hub import InferenceClient

from .summerize import summarize_conversation_task
from base.helpers.vectorize import VectorService

import logging
logger = logging.getLogger(__name__)

class HuggingFaceService:
    """Class to handle AI response generation using Hugging Face InferenceClient with Fireworks AI"""
    
    def __init__(self, model_id="meta-llama/Llama-3.1-8B-Instruct"):
        self.client = InferenceClient(
            provider="fireworks-ai",
            api_key=settings.HF_TOKEN,
            model=model_id
        )

        # System prompt
        self.system_prompt = (
            "You are an AI assistant for Shahtaz Rahman, a skilled software developer specializing in "
            "React, Python, and Node.js. Shahtaz is passionate about building innovative projects and "
            "showcasing his expertise through his portfolio website. Your role is to assist visitors by "
            "answering questions about Shahtaz's skills, projects, or anything related to his portfolio. "
            "Provide friendly, professional, and concise responses, reflecting Shahtaz's expertise and enthusiasm."
        )
    
    def query(self, messages):
        try:
            completion = self.client.chat.completions.create(
                model=self.client.model,
                messages=messages,
                max_tokens=100,  # Default max length, adjustable
                temperature=0.7,  # Default temperature, adjustable
                top_p=0.95,
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error querying Fireworks AI via InferenceClient: {e}")
            return "Sorry, I'm having trouble connecting to my brain right now. Please try again later."
    
    def generate_response(self, user_query, conversation_summary):
        """Generate a response to a user query"""
        try:
            # Format the input with the system prompt and user query
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "system", "content": conversation_summary},
                {"role": "user", "content": user_query}
            ]
            
            response = self.query(messages)
            return response
            
        except Exception as e:
            logger.exception(f"Error generating response: {e}")
            return "I apologize, but I encountered an error while processing your request."


class GenAIService:
    def __init__(self):
        self.gemini_client = genai.Client(api_key=settings.GEMINI_TOKEN)
        self.model = "gemini-1.5-flash"
        
        self.vector_service = VectorService()
        
        self.system_prompt = f"""
            You are Era, Shahtaz's AI assistant for his software development portfolio. Your primary goals are:
                1.  **Answer visitor queries about Shahtaz's projects, skills, and expertise.** Provide concise, informative, and relevant answers based *only* on the provided context.
                2.  **Guide visitors interested in software development projects to become clients.** Explain the onboarding process clearly and encourage them to take the next step.
                3.  **Maintain a professional, helpful, and enthusiastic tone.**
                4.  **Never invent information or refer to external knowledge not explicitly provided in the context.** If you don't know the answer based on the provided context, politely state that you don't have that specific detail and offer to connect them with Shahtaz Rahman for more in-depth discussion.
                5.  **Always end your response by subtly guiding the user towards a call to action if appropriate**, such as "Would you like to schedule a discovery call to discuss your project?" or "Feel free to ask more questions, or if you're ready, I can explain how to get started with a new project.
            """

    def generate_response(self, user_query: str, collection_type: Optional[str] = None, max_context_items: int = 5) -> Dict:
        """Generate AI response using RAG approach"""
        try:
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
            
            # 4. Generate response using Gemini
            response = self.gemini_client.models.generate_content(
                model = self.model,
                contents = full_prompt,
            )
            
            # 5. Return structured response
            return response.text
            
        except Exception as e:
            return "I apologize, but I encountered an error while processing your question. Please try again or contact Shahtaz directly for assistance."

    def _format_context(self, contexts: List) -> str:
        """Format retrieved contexts into a readable string"""
        if not contexts:
            return "No specific context available."
        
        formatted_contexts = []
        for i, ctx in enumerate(contexts, 1):
            context_block = f"""
                Context {i}:
                Title: {ctx.title}
                Type: {ctx.collection_type}
                Content: {ctx.content}
                """
            if ctx.metadata:
                context_block += f"Additional Info: {ctx.metadata}\n"
            
            formatted_contexts.append(context_block.strip())
        
        return "\n\n".join(formatted_contexts)

    def _create_prompt(self, user_query: str, context: str) -> str:
        """Create the complete prompt for the AI model"""
        return f"""{self.system_prompt}
            CONTEXT INFORMATION:
            {context}
            USER QUERY: {user_query}
            Please provide a helpful response based on the context information about Shahtaz's portfolio. If the context doesn't contain enough information to fully answer the question, acknowledge this and provide what information you can while suggesting the visitor contact Shahtaz directly for more details."""

    def generate_simple_response(self, user_query: str) -> Dict:
        """Generate a response without RAG (useful for general questions)"""
        try:
            full_prompt = f"""{self.system_prompt}
                USER QUERY: {user_query}"""

            response = self.gemini_client.models.generate_content(
                model = self.model,
                contents = full_prompt,
            )
            return response.text
            
        except Exception as e:
            return "I apologize, but I encountered an error while processing your question. Please try again or contact Shahtaz directly for assistance."



# Function to use in api view
def generate_ai_response(user_query, conversation_id, conversation_summary):
    """Generate an AI response to a user query"""
    try:
        # generate the ai response
        generator = HuggingFaceService()
        response = generator.generate_response(user_query, conversation_summary)

        # send summarization task to background
        summarize_conversation_task.delay(
            conversation_id=conversation_id,
            prev_summary=conversation_summary,
            user_query=user_query,
            ai_response=response
        )

        # return the response
        return response
    
    except Exception as e:
        logger.exception(f"Unexpected error in generate_ai_response: {e}")
        return "I'm sorry, I'm having trouble understanding your question right now. Could you please try again?"
    