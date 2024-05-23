from django.urls import path
from . import views

urlpatterns = [
    path('comments/create/<str:model_name>/<int:object_id>/', views.create_comment, name='create_comment'),
    path('comments/update/<int:comment_id>/', views.update_comment, name='update_comment'),
    path('comments/delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),

    
]   