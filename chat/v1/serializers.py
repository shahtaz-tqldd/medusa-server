from django.db import transaction
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from chat.models import Message, Conversation
from base.models import Visitor

from chat.choices import MessageSenderChoice
from chat.helpers.ai_response import generate_ai_response
from chat.helpers.summarize import summarize_conversation

MAX_TITLE_LENGTH = 40

class MessageCreateSerializer(serializers.Serializer):
    """Serializer to create a new message and AI response within a conversation."""
    
    visitor_id = serializers.UUIDField(required=True)
    query = serializers.CharField(required=True)
    
    def validate_visitor_id(self, value):
        try:
            visitor = Visitor.objects.get(id=value)
            return visitor
        except Visitor.DoesNotExist:
            raise serializers.ValidationError(_("Visitor not found"))
    
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
                conversation = Conversation.objects.filter(id=conversation_id, user=visitor).first()
            
            if not conversation:
                conversation = Conversation.objects.create(user=visitor, title=title)

            # Create user message
            user_message = Message.objects.create(
                conversation=conversation,
                sender=MessageSenderChoice.VISITOR,
                content=query
            )

            # Generate AI response
            ai_response_text = generate_ai_response(
                user_query=query, 
                previous_history=conversation.summary
            )

            # Create AI response message
            ai_message = Message.objects.create(
                conversation=conversation,
                sender=MessageSenderChoice.AI,
                content=ai_response_text
            )

            # Summarize conversation asynchronously
            summarize_conversation.delay(
                conversation_id=conversation.id, 
                user_query=query, 
                ai_response=ai_response_text, 
                previous_history=conversation.summary
            )

            return {
                'conversation_id': conversation.id,
                'user_message': user_message,
                'ai_response': ai_message
            }
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
        