from django.urls import path
from . import views

urlpatterns = [
    # Add other URL patterns here
    path('create/', views.create_event, name='create_event'),
    path('events/', views.events, name='events'),
    path('event_list', views.event_list, name='event_list'),
    path('events/<int:event_id>/participate/', views.participate_event, name='participate_event'),
    path('donor_event_list/', views.donor_event_list, name='donor_event_list'),
    path('eventIndex/', views.eventIndex, name='eventIndex'),
    path('events/detail/<int:pk>/',views.EventDetail,name='detail_events'),
    path('delete/<int:event_id>/', views.EventDelete, name='delete'),
    path('update/<int:event_id>/', views.update_event, name='update_event'),



]