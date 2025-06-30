from django.db import transaction
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from chat.models import Message, Conversation
from base.models import Visitor

from chat.choices import MessageSenderChoice
from chat.helpers.ai_response import process_portfolio_chat

import logging
logger = logging.getLogger(__name__)

MAX_TITLE_LENGTH = 40

class MessageCreateSerializer(serializers.Serializer):
    """Serializer for Create Message and save conversation summary"""
    
    visitor_id = serializers.UUIDField(required=True)
    query = serializers.CharField(required=True, max_length=1000)
    
    def validate_visitor_id(self, value):
        try:
            visitor = Visitor.objects.get(id=value)
            return visitor
        except Visitor.DoesNotExist:
            raise serializers.ValidationError(_("Visitor not found"))
    
    def validate_query(self, value):
        if not value.strip():
            raise serializers.ValidationError(_("Query cannot be empty"))
        return value.strip()
    
    def create(self, validated_data):
        visitor = validated_data.get('visitor_id')
        query = validated_data.get('query')
        conversation_id = self.context.get('conversation_id')

        with transaction.atomic():
            # Prepare conversation title
            title = query if len(query) <= MAX_TITLE_LENGTH else f"{query[:MAX_TITLE_LENGTH-3]}..."

            # Get existing or create new conversation
            conversation = None
            if conversation_id:
                try:
                    conversation = Conversation.objects.get(id=conversation_id, user=visitor)
                except Conversation.DoesNotExist:
                    # Invalid conversation_id provided, create new conversation
                    pass
            
            if not conversation:
                conversation = Conversation.objects.create(user=visitor, title=title)

            # Create user message
            user_message = Message.objects.create(
                conversation=conversation,
                sender=MessageSenderChoice.VISITOR,
                content=query
            )

            try:
                # Process chat using the new agent
                chat_result = process_portfolio_chat(
                    user_query=query, 
                    conversation_summary=conversation.summary or ""
                )

                if chat_result['success']:
                    ai_response_text = chat_result['user_response']
                    updated_summary = chat_result['conversation_summary']
                    
                    # Create AI response message
                    ai_message = Message.objects.create(
                        conversation=conversation,
                        sender=MessageSenderChoice.AI,
                        content=ai_response_text
                    )

                    # Update conversation summary
                    conversation.summary = updated_summary
                    conversation.save(update_fields=['summary'])

                    # Return in the format expected by your API view
                    return {
                        'conversation_id': conversation.id,
                        'user_message': user_message,
                        'ai_response': ai_message,
                        'success': True
                    }
                else:
                    # AI processing failed, create error response
                    error_response = chat_result.get('user_response', 'I apologize, but I encountered an issue processing your request. Please try again.')
                    
                    ai_message = Message.objects.create(
                        conversation=conversation,
                        sender=MessageSenderChoice.AI,
                        content=error_response
                    )

                    # Still return success=True since we created messages successfully
                    # The error is handled gracefully with a user-friendly message
                    return {
                        'conversation_id': conversation.id,
                        'user_message': user_message,
                        'ai_response': ai_message,
                        'success': True,
                        'ai_error': chat_result.get('error')  # Optional field for logging
                    }

            except Exception as e:
                # Critical error handling - this should rarely happen
                logger.exception(f"Critical error in message creation: {e}")
                
                # Try to create a fallback response
                try:
                    fallback_response = "I'm sorry, I'm experiencing technical difficulties. Please try again later."
                    ai_message = Message.objects.create(
                        conversation=conversation,
                        sender=MessageSenderChoice.AI,
                        content=fallback_response
                    )
                    
                    return {
                        'conversation_id': conversation.id,
                        'user_message': user_message,
                        'ai_response': ai_message,
                        'success': True,
                        'critical_error': str(e)  # For logging purposes
                    }
                except Exception as fallback_error:
                    # If even fallback fails, raise the original exception
                    logger.critical(f"Fallback message creation failed: {fallback_error}")
                    raise serializers.ValidationError(_("Unable to process your message. Please try again."))
                
class ConversationSerializer(serializers.ModelSerializer):
    """Serializer to return conversation list with conversation id"""
    last_message = serializers.SerializerMethodField()
    total_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['id', 'title', 'created_at', 'last_message', 'total_message']
    
    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-created_at').first()
        if last_msg:
            return {
                'content': last_msg.content[:100],
                'sender': last_msg.sender
            }
        return None
    
    def get_total_message(self, obj):
        return obj.messages.count()


class MessageSerializer(serializers.ModelSerializer):
    """Serializer to return conversation list with conversation id"""
    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'created_at']
        