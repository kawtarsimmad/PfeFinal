from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('association_list/',views.association_list,name='association_list'), 
    path('search/', views.search, name='search'),   
    
]