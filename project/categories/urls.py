from django.urls import path
from . import views

urlpatterns = [
    path('category/',views.category,name='category'),
    path('categories/',views.categories,name='categories'),
    path('Health/',views.health,name='Health'),
    path('Education/',views.education,name='Education'),
    path('Environment/',views.environment,name='Environment'),
    path('Children/',views.children,name='Children'),
    path('Urgent/',views.urgent,name='Urgent'),    
    
]
