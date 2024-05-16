from django.urls import path
from . import views



urlpatterns = [
    path('publication/',views.publication,name='publication'),
    path('publications/',views.publications,name='publications'),
    path('PubList/',views.PubList,name='PubList'),
    path('detail/<int:pk>/',views.PubDetail,name='detail'),
    path('create/',views.PubCreate,name='create'),
    path('update/<int:pk>/',views.PubUpdate,name='update'),
    path('delete/<int:publication_id>/', views.PubDelete, name='delete'),
    path('publicationIndex/',views.publicationIndex,name='publicationIndex'),
    path('dons_associes/<int:publication_id>/', views.dons_associes, name='dons_associes'),


]
