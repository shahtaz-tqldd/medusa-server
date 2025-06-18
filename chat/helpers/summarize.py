from celery import shared_task
from .ai_response import GenAIService

import logging
logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def summarize_conversation(self, conversation_id, user_query: str, ai_response: str, previous_history: str) -> str:
    try:
        generator = GenAIService()
        summary = generator.summarize(previous_history, user_query, ai_response)
        # Save summary to database or cache (example)
        # Conversation.objects.update_summary(conversation_id, summary)
        return summary
    except Exception as e:
        logger.error(f"Error in summarize_conversation task: {e}")
        self.retry(countdown=60, exc=e)