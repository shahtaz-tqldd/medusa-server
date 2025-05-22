from django.conf import settings
from celery import shared_task
from huggingface_hub import InferenceClient
from chat.models import Conversation
import logging

logger = logging.getLogger(__name__)

class ConversationSummary:
    """Class to make summary of the conversation"""
    
    def __init__(self, model_id="meta-llama/Llama-3.1-8B-Instruct"):
        self.client = InferenceClient(
            provider="fireworks-ai",
            api_key=settings.HF_TOKEN,
            model=model_id
        )
        self.system_prompt = (
            "Summarize the conversation between a user and an AI assistant clearly and concisely. "
            "If a previous summary exists, update it to include the new exchange while keeping important context. "
            "Summary should be a single paragraph."
        )

    
    def perform_summarize(self, prev_summary, user_query, ai_response):
        # Build the text to summarize with better formatting
        if prev_summary:
            prompt = (
                f"Previous conversation summary: {prev_summary}\n\n"
                f"Latest exchange:\n"
                f"User: {user_query}\n"
                f"Assistant: {ai_response}\n\n"
            )
        else:
            prompt = (
                f"User: {user_query}\n"
                f"Assistant: {ai_response}\n\n"
            )
        
        messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
        ]
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
            logger.exception(f"Error generating response: {e}")
            return None
        

@shared_task
def summarize_conversation_task(conversation_id, prev_summary, user_query, ai_response):
    """Background task to summarize conversation"""
    summarizer = ConversationSummary()
    summary_text = summarizer.perform_summarize(
        prev_summary=prev_summary or "",
        user_query=user_query,
        ai_response=ai_response,
    )
    
    if summary_text:
        Conversation.objects.filter(id=conversation_id).update(summary=summary_text)
        logger.info(f"Conversation summary updated for ID {conversation_id}")
    
    else:
        logger.warning(f"No summary generated for conversation ID {conversation_id}")
    