
from django.urls import path
from . import views

urlpatterns = [
    path('messages/', views.messages, name='messages'),
    path('inbox/', views.inbox, name='inbox'),
    path('send_message/', views.send_message, name='send_message'),
    path('reply_message/<int:message_id>/', views.reply_message, name='reply_message'),
    path('chat_page/', views.chat_page, name='chat_page'),
    path('delete_conversation/<int:conversation_id>/', views.delete_conversation, name='delete_conversation'),
    path('delete_message/<int:message_id>/', views.delete_message, name='delete_message'),

    
]
