from django.urls import path, include, re_path
from .views import HomeView
from .views import custom_logout 
from django.conf.urls.static import static
from django.conf import settings
from . import views
from django.contrib.auth import views as auth_views
from users.views import ResetPasswordView, ChangePasswordView 
from django.contrib.auth.views import PasswordResetDoneView

urlpatterns = [
    # Ajoutez vos patterns d'URL ici
    path('home/', HomeView.as_view() , name="home"),
    path('logout/', custom_logout, name='logout'),


    path('DonorSignup/', views.DonorSignup, name='DonorSignup'),
    path('dashboard_donor/', views.dashboard_donor, name='dashboard_donor'),
    path('DonorSignIn/', views.DonorSignIn, name='DonorSignIn'),


    path('AssociationSignup/', views.AssociationSignup, name='AssociationSignup'),
    path('dashboard_association/', views.dashboard_association, name='dashboard_association'),
    path('AssociationSignIn/', views.AssociationSignIn, name='AssociationSignIn'),


    path('signupadmin/', views.signupadmin, name='signupadmin'),
    path('dashboardAdmin/',views.dashboardAdmin,name='dashboardAdmin'),

    path('donors/',views.donors,name='donors'),
    path('associations/',views.associations,name='associations'),
    
    path('add_donor/', views.add_donor, name='add_donor'),
    path('update_donor/<int:donor_id>/', views.update_donor, name='update_donor'),
    path('delete_donor/<int:donor_id>/', views.delete_donor, name='delete_donor'),
    
    path('add_association/', views.add_association, name='add_association'),
    path('update_association/<int:association_id>/', views.update_association, name='update_association'),
    path('delete_association/<int:association_id>/', views.delete_association, name='delete_association'),
  
    path('password-reset/', ResetPasswordView.as_view(), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'),
         name='password_reset_confirm'),

    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),

    path('password-change/', ChangePasswordView.as_view(), name='password_change'),

    #re_path(r'^oauth/', include('social_django.urls', namespace='social')),
    
    path('password-reset/done/', PasswordResetDoneView.as_view(template_name='users/password_success_message.html'), name='password-reset/done'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('DonorSignup/account-activation/', views.account_activation_email, name='account-activation'),
    path('AssociationSignup/account-activation/', views.account_activation_email, name='account-activation'),
    path('associations/<int:association_id>/contact/', views.contact_association, name='contact_association'),
    path('contact/success/', views.contact_success, name='contact_success'),


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)