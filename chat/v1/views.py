from django.utils.translation import gettext_lazy as _

from rest_framework import generics, status, permissions

from chat.v1 import res_msg
from base.helpers.response import APIResponse

from chat.models import Conversation, Message

from chat.v1.serializers import (
    MessageCreateSerializer, 
    ConversationSerializer, 
    MessageSerializer,
)


class CreateMessage(generics.CreateAPIView):
    """API View to create new message"""
    RES_LANG = 'en'
    permission_classes = [permissions.AllowAny]
    serializer_class = MessageCreateSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['conversation_id'] = self.request.query_params.get('conversation_id')
        return context
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        
        response_data = {
            'conversation_id': str(result['conversation_id']),
            'response': result['ai_response'].content,
            'created_at': result['ai_response'].created_at
        }
        
        return APIResponse.success(
            data=response_data, 
            message=res_msg.CHAT_MESSAGE_CREATED[self.RES_LANG], 
            status=status.HTTP_201_CREATED
        )


class ConversationList(generics.ListAPIView):
    """API View to get all conversation list"""
    RES_LANG = 'en'
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Conversation.objects.all()
        
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
    
        # Paginate if necessary (optional)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        
        return APIResponse.success(
            data=serializer.data, 
            message=res_msg.CHAT_CONVERSATION_LIST[self.RES_LANG]
        )
    
    
class SingleConversation(generics.RetrieveAPIView):
    """API View to get all messages from a conversation"""
    RES_LANG = 'en'
    serializer_class = MessageSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'conversation_id'
    
    def get_queryset(self):
        # Get conversation_id from URL parameters
        conversation_id = self.kwargs.get('conversation_id')
        
        if not conversation_id:
            return Message.objects.none()
    
        return Message.objects.filter(conversation_id=conversation_id).order_by('-created_at')
    
    def retrieve(self, request, *args, **kwargs):
        conversation_id = self.kwargs.get('conversation_id')
        
        try:
            # Get the conversation object
            conversation = Conversation.objects.get(id=conversation_id)
            
            # Get all messages for this conversation
            messages = self.get_queryset()
            
            # Serialize messages
            messages_serializer = self.get_serializer(messages, many=True)
            
            response_data = {
                'conversation': {
                    'id': conversation.id,
                    'title': conversation.title,
                    'created_at': conversation.created_at
                },
                'messages': messages_serializer.data
            }
            
            return APIResponse.success(
                data=response_data, 
                message=res_msg.CHAT_SINGLE_CONVERSATION[self.RES_LANG]
            )
        
        except Conversation.DoesNotExist:
            return APIResponse.error(message=_("Conversation not found"))
        

class DeleteConversation(generics.DestroyAPIView):
    """API View to delete conversation with conversation id"""
    RES_LANG = 'en'
    permission_classes = [permissions.IsAuthenticated]
    queryset = Conversation.objects.all()
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return APIResponse.success(
            message=res_msg.CHAT_DELETE_CONVERSATION[self.RES_LANG], 
            status=status.HTTP_204_NO_CONTENT
        )
