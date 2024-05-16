from django.urls import path
from . import views

urlpatterns = [
    # Ajoutez vos patterns d'URL ici
    path('reclamation/',views.reclamation,name='reclamation'),
    path('reclamations/',views.reclamations,name='reclamations'),
    path('create/', views.create_reclamation, name='create_reclamation'),
    path('view_reclamations/', views.view_reclamations, name='view_reclamations'),
    path('view_reclamations/delete/<int:reclamation_id>/', views.delete_reclamation, name='delete_reclamation'),
    path('update/<int:reclamation_id>/', views.update_reclamation, name='update_reclamation'),
    path('update_reclamation_status/<int:reclamation_id>/', views.update_reclamation_status, name='update_reclamation_status'),

]