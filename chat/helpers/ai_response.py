from google import genai
from django.conf import settings
from chat.v1.res_msg import CHAT_FAILED_MESSAGE

import logging
logger = logging.getLogger(__name__)

class QueryPrompt:
    def __init__(self):
        self.system_prompt = (
            "You are Era, a friendly and professional AI assistant for Shahtaz's portfolio. "
            "Shahtaz is a software developer with 2 years of experience in full-stack development, specializing in clean, scalable, user-centered applications. "
            "His skills include React.js, Next.js, Node.js, Python, Django, Docker, Socket.IO, vector databases (Pinecone, pgvector), and AI integrations. "
            "Projects include: "
            "- An HRM system with real-time payroll and attendance tracking (Django, Socket.IO, PostgreSQL). "
            "- An eCommerce platform with personalized recommendations (React.js, Node.js, MongoDB). "
            "- An AI-powered portfolio assistant chatbot (Python, Gemini API, Django). "
            "Answer visitor questions about Shahtaz’s skills, projects, services, or expertise based only on this context. "
            "Use a warm, engaging tone to attract potential clients. "
            "For meeting requests, share: https://example.calendly.com/shahtaz/. "
            "If a query is outside Shahtaz’s domain (e.g., unrelated technologies), politely redirect to his expertise or suggest contacting him. "
            "Example: 'I’m not sure about blockchain, but Shahtaz excels at building AI chatbots and scalable web apps. Want to learn more?'"
        )

        self.system_prompt_summarize = (
            "Summarize the conversation between the user and the AI assistant in 50–100 words. "
            "Focus on key topics discussed, user intent, and Shahtaz’s relevant skills or projects. "
            "If a previous summary exists, merge it with the current conversation, prioritizing new information and avoiding redundancy. "
            "Keep the summary concise, factual, and neutral. "
            "Example: 'User asked about Shahtaz’s experience with AI chatbots. Era highlighted his work on an AI-powered portfolio assistant using Python and Gemini API. User also inquired about scheduling a meeting; Era shared the Calendly link.'"
        )

    def generate_prompt(self, user_query: str, previous_history:str):
        return f"{self.system_prompt}\n\nVisitor Query: {user_query}\n\nPrevious Summary: {previous_history}"

    def generate_summarize_prompt(self, user_query: str, ai_response: str, previous_history: str):
        return (
            f"{self.system_prompt_summarize}\n\n"
            f"Visitor Query: {user_query}\n\n"
            f"AI Response: {ai_response}\n\n"
            f"Previous Summary: {previous_history}"
        )


class GenAIService:
    def __init__(self):
        try:
            self.gemini_client = genai.GenerativeModel(
                model_name=settings.GEMINI_MODEL,
                api_key=settings.GEMINI_TOKEN
            )
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            raise
        self.prompt = QueryPrompt()

    def generate_response(self, user_query: str, previous_history: str) -> str:
        try:
            prompt_text = self.prompt.generate_prompt(user_query, previous_history)
            response = self.gemini_client.generate_content(
                contents=[{"role": "user", "parts": [{"text": prompt_text}]}],
                generation_config={"temperature": 0.7, "max_output_tokens": 500}
            )
            return response.text
        except genai.exceptions.APIError as e:
            logger.error(f"Gemini API error: {e}")
            return CHAT_FAILED_MESSAGE["en"]
        except Exception as e:
            logger.error(f"Unexpected error generating response: {e}")
            return CHAT_FAILED_MESSAGE["en"]

    def summarize(self, previous_history: str, user_query: str, ai_response: str) -> str:
        try:
            prompt_text = self.prompt.generate_summarize_prompt(user_query, ai_response, previous_history)
            response = self.gemini_client.generate_content(
                contents=[{"role": "user", "parts": [{"text": prompt_text}]}],
                generation_config={"temperature": 0.5, "max_output_tokens": 200}
            )
            return response.text
        except genai.exceptions.APIError as e:
            logger.error(f"Gemini API error during summarization: {e}")
            return previous_history
        except Exception as e:
            logger.error(f"Unexpected error summarizing: {e}")
            return previous_history

# Singleton instance
_generator = None

def generate_ai_response(user_query: str, previous_history: str, conversation_id) -> str:
    global _generator
    try:
        if _generator is None:
            _generator = GenAIService()
        
        return _generator.generate_response(user_query, previous_history)
    except Exception as e:
        logger.exception(f"Unexpected error in generate_ai_response: {e}")
        return CHAT_FAILED_MESSAGE["en"]