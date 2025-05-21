from django.urls import path, include
from .views import (
    CreateMessage, 
    ConversationList, 
    SingleConversation, 
    DeleteConversation,
)

chat_urls = [
    path("create-message/", CreateMessage.as_view(), name="create-message"),
]

conversation_urls = [
    path("list/", ConversationList.as_view(), name="conversation-list"),
    path("<conversation_id>/", SingleConversation.as_view(), name="single-conversation"),
    path("delete/<id>/", DeleteConversation.as_view(), name="delete-conversation"),
]

urlpatterns = chat_urls + [path('conversation/', include(conversation_urls))]
