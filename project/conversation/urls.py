
from django.urls import path
from . import views

urlpatterns = [
 
    path('chat_view/', views.chat_view, name='chat_view'),
    path('messages/', views.message_list, name='message_list'),
    path('messages/<int:user_id>/', views.conversation, name='conversation'),
    path('search_users/', views.search_users, name='search_users'),
    path('delete_message/<int:message_id>/', views.delete_message, name='delete_message'),

]
