from django.urls import path
from . import views
from .views import generate_pdf


urlpatterns = [
    path('don/',views.don,name='don'),
    path('dons/',views.dons,name='dons'),
    path('faire_don/<int:publication_id>/', views.faire_don, name='faire_don'),
    path('faire_don/association/<int:association_id>/', views.faire_don, name='faire_don_association'),
    path('viewDons/', views.viewDons, name='viewDons'),
    path('delete_don/<int:don_id>/', views.delete_don, name='delete_don'),
    path('checkout/<int:don_id>/', views.CheckOut, name='checkout'),
    path('payment-success/<int:don_id>/', views.PaymentSuccessful, name='payment-success'),
    path('payment-failed/<int:don_id>/', views.paymentFailed, name='payment-failed'),
    path('dons/generate_pdf/<int:don_id>/', generate_pdf, name='generate_pdf'),

    
]
