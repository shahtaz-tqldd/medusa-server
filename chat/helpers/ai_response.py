import logging
from django.conf import settings

from huggingface_hub import InferenceClient

from .summerize import summarize_conversation_task

logger = logging.getLogger(__name__)

class AIResponseGenerator:
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



# Function to use in api view
def generate_ai_response(user_query, conversation_id, conversation_summary):
    """Generate an AI response to a user query"""
    try:
        # generate the ai response
        generator = AIResponseGenerator()
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
    