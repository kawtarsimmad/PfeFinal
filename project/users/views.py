from django.shortcuts import render
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.views.generic import TemplateView 
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login,logout,authenticate
from django.shortcuts import redirect,render,HttpResponseRedirect
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
#from paypal.standard.forms import PayPalPaymentsForm
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode 
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes
import codecs
from django.contrib.auth.password_validation import validate_password
from django.http import HttpResponseForbidden
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import PasswordResetView, PasswordChangeView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import PasswordResetDoneView
from django.core.mail import EmailMessage, send_mail
from project import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import authenticate, login, logout
from . tokens import generate_token
from django.contrib import messages
from .models import User,Admin, Donor, Association, Alert , PendingEmail###########
from publications.models import Publication
from categories.models import Category
from reclamations.models import Reclamation
from dons.models import Don
from django.core.exceptions import ValidationError
from django.http import HttpResponseBadRequest
from django.contrib.auth import update_session_auth_hash
from functools import wraps
from django.db.models import Count, Sum, Q,F
from django.db.models.functions import ExtractMonth,ExtractYear
from django.db.models.functions import TruncMonth
from publications.utils import get_funding_statistics 
from events.models import Event
#
class HomeView(TemplateView):
    template_name = 'users/home.html'

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and getattr(request.user, 'is_admin', False):
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("You do not have permission to access this page.")
    return _wrapped_view

def activate(request,uidb64,token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active = True
        # user.profile.signup_confirmation = True
        myuser.save()
        login(request,myuser)
        messages.success(request, "Your Account has been activated!!")
        if myuser.is_donor:
            return redirect('dashboard_donor')
        if myuser.is_association:
            return redirect('dashboard_association')
        
    else:
        return render(request,'users/activation_failed.html')


def send_activation_email(user):
    subject = "Welcome to HopeBloom Sign up!!"
    message = f"Hello {user.first_name}!\nWelcome to HopeBloom.\nPlease confirm your email address."
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])

def send_confirmation_email(user, request):
    current_site = get_current_site(request)
    email_subject = "Confirm your Email @ HopeBloom - Sign up!!"
    message = render_to_string('users/confirm_email.html', {
        'name': user.first_name,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': generate_token.make_token(user)
    })
    send_mail(email_subject, message, settings.EMAIL_HOST_USER, [user.email])
  

    
#register en tant que Donor
def DonorSignup(request):
    if request.method == 'POST':
        name = request.POST.get('name', None)
        email = request.POST.get('email', None)
        photo = request.FILES.get('image', None)
        password = request.POST.get('password', None)
        repassword = request.POST.get('repassword', None)
        telephone = request.POST.get('telephone', None)
        adresse=request.POST.get('adresse',None)

        try:
            validate_email(email)
        except ValidationError:
            return render(request, 'users/registerdonor.html', {'error': True, 'message': 'Enter a valid email !'})

        if password != repassword:
            return render(request, 'users/registerdonor.html', {'error': True, 'message': 'Passwords do not match or are too short !'})

        if not name or not email or not password or not repassword:
            return render(request, 'users/registerdonor.html', {'error': True, 'message': 'Please fill in all necessary fields !'})
        
        if User.objects.filter(email=email).exists():
            return render(request, 'users/registerdonor.html', {'error': True, 'message': 'A user with this email already exists !'})
        
        # Hash the password and create a new user
        utilisateur = User.objects.create_user(username=email, email=email, password=password, first_name=name)
        utilisateur.is_donor = True
        utilisateur.is_association = False
        utilisateur.is_admin=False
        utilisateur.is_active = False
        utilisateur.save()
        
        # Create a donor associated with the user
        donor = Donor.objects.create(
            user=utilisateur,
            phone_number=telephone,
        )
        donor.image=photo
        donor.save()
        # Welcome Email
        send_activation_email(utilisateur)
        
        # Email Address Confirmation Email
        send_confirmation_email(utilisateur, request)
        
        messages.success(request, "Your account was successfully created. Please check your email for activation.")
        
        return render(request, 'users/registerdonor.html', {'error': False, 'success': True, 'message': 'Account created successfully. Please check your email for activation'})
        

    return render(request, 'users/registerdonor.html', {'error': False, 'message': ''})

def account_activation_email (request):
    messages.success(request, "Account created successfully. Please check your email for activation.")
    return render(request, 'users/account_activation_email.html')


#Login as donor
def DonorSignIn(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        if user is not None and user.is_active:
            login(request, user)
            if user.is_donor:
                return redirect('dashboard_donor')
            elif user.is_association:
                return redirect('dashboard_association')
            else:
                return redirect('dashboardAdmin')
    return render(request, 'users/Logindonor.html', {'error': True, 'message': "Mot de passe incorrect ou Utilisateur n'existe pas!"})
 


from django.db.models import Sum, F ,Count
from django.db.models.functions import ExtractMonth, ExtractYear,TruncMonth
@login_required(login_url="")
def dashboard_donor(request):
    user = request.user
    donor = Donor.objects.filter(user=user).first()
    association = Association.objects.all()

    if user.is_authenticated:
        nombre_dons = Don.objects.filter(user=user, est_paye=True).count()
    else:
        nombre_dons = 0 

    somme_dons_effectues = Don.objects.filter(user=user, est_paye=True).aggregate(total=Sum('montantDons'))['total']
    pending_reclamations_count = Reclamation.objects.filter(status='Pending').count()
    resolu_reclamations_count = Reclamation.objects.exclude(status='Pending').count()
    nombre_evenements_participes = Event.objects.filter(attendees=user).count()
    nombre_reclamations_creees = Reclamation.objects.filter(user=user).count()

    # Agréger les dons par mois
    dons_mensuels = Don.objects.filter(user=user, est_paye=True) \
                        .annotate(month=ExtractMonth('date'), year=ExtractYear('date')) \
                        .values('year', 'month') \
                        .annotate(total=Sum('montantDons')) \
                        .order_by('year', 'month')
    
    nombre_dons_mensuels = Don.objects.filter(user=user, est_paye=True) \
                            .annotate(month=ExtractMonth('date'), year=ExtractYear('date')) \
                            .values('year', 'month') \
                            .annotate(count=Count('id')) \
                            .order_by('year', 'month')

    context = {
        'nombre_dons': nombre_dons,
        'somme_dons_effectues': somme_dons_effectues,
        'donor': donor,
        'pending_reclamations_count': pending_reclamations_count,
        'resolu_reclamations_count': resolu_reclamations_count,
        'nombre_evenements_participes': nombre_evenements_participes,
        'nombre_reclamations_creees': nombre_reclamations_creees,
        'association': association,
        'dons_mensuels': dons_mensuels,  
        'nombre_dons_mensuels':nombre_dons_mensuels,
    }
    return render(request, 'users/dashboard_donor.html', context)


def donors(request):
    user = request.user
    admin = Admin.objects.filter(user=user).first()
    donors=Donor.objects.all()
    context ={
        'admin': admin,
        'donors': donors,
        
    }
    return render (request,'users/donors.html',context)
 


#####################/ Donor /#############################

##################### Association #########################
#register en tant que Association
def AssociationSignup(request):
    if request.method == 'POST':
        name = request.POST.get('name', None)
        email = request.POST.get('email', None)
        photo = request.FILES.get('image', None)
        password = request.POST.get('password', None)
        repassword = request.POST.get('repassword', None)
        telephone = request.POST.get('telephone', None)
        stat_juridique=request.FILES.get('stat_juridique',None)
        adresse=request.POST.get('adresse',None)
        paypal_email=request.POST.get('paypal_email',None)


        try:
            validate_email(email)
        except ValidationError:
            return render(request, 'users/registerassociation.html', {'error': True, 'message': 'Entrez un email valide !'})

        if password != repassword:
            return render(request, 'users/registerassociation.html', {'error': True, 'message': 'Les mots de passe ne correspondent pas ou sont trop courts !'})

        if not name or not email or not password or not repassword:
            return render(request, 'users/registerassociation.html', {'error': True, 'message': 'Veuillez remplir tous les champs nécessaires !'})
        
        if User.objects.filter(email=email).exists():
            return render(request, 'users/registerassociation.html', {'error': True, 'message': 'Un utilisateur avec cet email existe déjà !'})
        # Hash the password and create a new user
        utilisateur = User.objects.create_user(username=email, email=email, password=password, first_name=name)
        utilisateur.is_association = True
        utilisateur.is_donor=False
        utilisateur.is_admin=False
        utilisateur.is_active = False
        utilisateur.save()

        # Create a association associated with the user
        association = Association.objects.create(
            user=utilisateur,
            phone_number=telephone,
            stat_juridique=stat_juridique, 
            paypal_email=paypal_email,
            adresse=adresse, 
        )
        association.image=photo
        association.save()
        # Welcome Email
        subject = "Welcome to HopeBloom Sign up!!"
        from_email = settings.EMAIL_HOST_USER
        to_list = [utilisateur.email]
        message = "Hello " + utilisateur.first_name + "!! \n" + "Welcome to HopeBloom!! \nThank you for visiting our website\n We have also sent you a confirmation email, please confirm your email address. \n\nThanking You"        
        send_mail(subject, message,from_email, to_list, fail_silently=True)
        
        
        # Email Address Confirmation Email
        current_site = get_current_site(request)
        email_subject = "Confirm your Email @ HopeBloom -  Sign up!!"
        message2 = render_to_string('users/confirm_email.html',{
            
            'name': utilisateur.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(utilisateur.pk)),
            'token': generate_token.make_token(utilisateur)
        })
        email = EmailMessage(
        email_subject,
        message2,
        settings.EMAIL_HOST_USER,
        [utilisateur.email],
        )
        send_mail(email_subject, message2, from_email, to_list, fail_silently=True)      

    return render(request, 'users/registerassociation.html', {'error': False, 'message': ''})

#Login as association
def AssociationSignIn(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        if user is not None and user.is_active:
            login(request, user)
            if user.is_association:
                return redirect('dashboard_association')
            elif user.is_donor:
                return redirect('dashboard_donor')
            else:
                return redirect('dashboardAdmin')
            
        else:
            return redirect('/')  # Rediriger vers une page d'erreur personnalisée ou une autre page
    return render(request, 'users/Loginassociation.html', {'error': True, 'message': "Mot de passe incorrect ou Utilisateur n'existe pas!"})
 


@login_required(login_url="")
def dashboard_association(request):
    user = request.user
    association = Association.objects.filter(user=user).first()
    publications = Publication.objects.filter(association=association)

    stats =get_funding_statistics(publications)
    total_dons_all = Publication.calculate_total_dons_all()####total des dons  de tous les publications ou d'une pub 
    pending_reclamations_count = Reclamation.objects.filter(status='Pending').count()
    resolu_reclamations_count = Reclamation.objects.exclude(status='Pending').count()
    print(stats.keys())
    if 'number_of_funded_publications' in stats and 'number_of_publications' in stats:
        # Accédez aux valeurs de `number_of_funded_publications` et `number_of_publications`
        funded_publications = stats['number_of_funded_publications']
        total_publications = stats['number_of_publications']
    else:
        # Gérez le cas où les clés ne sont pas présentes dans `stats`
        funded_publications = 0
        total_publications = 0
    unfunded_publications=total_publications - funded_publications 

    donations_per_month = (
        Don.objects
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    months = [donation['month'].strftime("%B %Y") for donation in donations_per_month]
    counts = [donation['count'] for donation in donations_per_month]
    nombre_reclamations_creees = Reclamation.objects.filter(user=request.user).count()
    nombre_evenements = Event.objects.filter(user=user).count()
    nombre_dons_effectues = Don.objects.filter(association=association, est_paye=True).count()


    context = {
        'association': association,
        'publications': publications,
        'total_dons_all' : total_dons_all,
        'pending_reclamations_count': pending_reclamations_count,
        'resolu_reclamations_count':resolu_reclamations_count,
        'stats':stats,
        'unfunded_publications':unfunded_publications,
        'donations_per_month': donations_per_month,
        'months': months,
        'counts': counts,
        'nombre_reclamations_creees':nombre_reclamations_creees,
        'nombre_evenements':nombre_evenements,
        'nombre_dons_effectues':nombre_dons_effectues,
        'total_publications':total_publications,
    }
    return render(request, 'users/dashboard_association.html', context)


def associations(request):
    user = request.user
    admin = Admin.objects.filter(user=user).first()
    associations=Association.objects.all()
    context ={
        'admin': admin,
        'associations':associations,
        
    }
    return render (request,'users/associations.html',context)


#####################/ Association /#############################

###################  admin  ####################
def signupadmin(request):
    if request.method == 'POST':
        name = request.POST.get('name', None)
        email = request.POST.get('email', None)
        photo = request.FILES.get('image', None)
        password = request.POST.get('password', None)
        repassword = request.POST.get('repassword', None)
       

        try:
            validate_email(email)
        except ValidationError:
            return render(request, 'users/adminregister.html', {'error': True, 'message': 'Entrez un email valide !!!!!'})

        if password != repassword:
            return render(request, 'users/adminregister.html', {'error': True, 'message': 'Les mots de passe ne correspondent pas ou sont trop courts !'})

        if not name or not email or not password or not repassword:
            return render(request, 'users/adminregister.html', {'error': True, 'message': 'Veuillez remplir tous les champs nécessaires !'})
        
        if User.objects.filter(email=email).exists():
            return render(request, 'users/adminregister.html', {'error': True, 'message': 'Un utilisateur avec cet email existe déjà !'})

        # Hash the password and create a new user
        utilisateur = User.objects.create_user(username=email, email=email, password=password, first_name=name)
        utilisateur.is_donor = False
        utilisateur.is_association = False
        utilisateur.is_admin=True
        utilisateur.save()


         # Create a admin associated with the user
        admin = Admin.objects.create(
            user=utilisateur,
            
        )
        admin.image=photo
        admin.save()
        # Authenticate the user
        authenticated_user = authenticate(request, username=email, password=password)
        if authenticated_user is not None:
            login(request, authenticated_user)

        # Redirect to the dashboard
        return redirect('dashboardAdmin')

    return render(request, 'users/adminregister.html', {'error': False, 'message': ''})

@admin_required
@login_required(login_url="")
def dashboardAdmin(request):
    user = request.user
    admin = Admin.objects.filter(user=user).first()
    donors=Donor.objects.all()
    associations=Association.objects.all()
    pub=Publication.objects.all()
    categories= Category.objects.all()
    dons = Don.objects.all()
    users=User.objects.all()
    associations=Association.objects.all()
    donors=Donor.objects.all()
    categories= Category.objects.all()
    alert = Alert.objects.first()
    stats =get_funding_statistics(pub)
    total_dons_all = Publication.calculate_total_dons_all()####total des dons  de tous les publications ou d'une pub 
    pending_reclamations_count = Reclamation.objects.filter(status='Pending').count()
    print(stats.keys())
    if 'number_of_funded_publications' in stats and 'number_of_publications' in stats:
        # Accédez aux valeurs de `number_of_funded_publications` et `number_of_publications`
        funded_publications = stats['number_of_funded_publications']
        total_publications = stats['number_of_publications']
    else:
        # Gérez le cas où les clés ne sont pas présentes dans `stats`
        funded_publications = 0
        total_publications = 0
    unfunded_publications=total_publications - funded_publications 


    donations_per_month = (
        Don.objects
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    months = [donation['month'].strftime("%B %Y") for donation in donations_per_month]
    counts = [donation['count'] for donation in donations_per_month]

    total_reclamations = Reclamation.objects.count()
    responded_reclamations = Reclamation.objects.filter(status__in=['Resolved', 'Refused']).count()
    if total_reclamations > 0:
        responded_percentage = (responded_reclamations / total_reclamations) * 100
    else:
        responded_percentage = 0
    pending_reclamations = Reclamation.objects.filter(status__in=['Pending']).count()

    pending_emails = PendingEmail.objects.filter(processed=False)
    emails = PendingEmail.objects.filter(processed=True)
    pending_count = pending_emails.count()
    pending_emails_monthly = PendingEmail.objects.filter(processed=False) \
                            .annotate(month=ExtractMonth('created_at')) \
                            .annotate(year=ExtractYear('created_at')) \
                            .values('year', 'month') \
                            .annotate(count=Count('id')) \
                            .order_by('year', 'month')
    
      # Calcul des publications par mois
    publications_by_month = (
        Publication.objects
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    # Calcul des publications ayant atteint l'objectif par mois
    publications_achieved_by_month = (
        Publication.objects
        .annotate(month=TruncMonth('date'))
        .filter(montant__lte=Sum('dons__montantDons', filter=Q(dons__est_paye=True)))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    months_pub = [pub['month'].strftime("%B %Y") for pub in publications_by_month]
    counts_pub = [pub['count'] for pub in publications_by_month]
    counts_pub_achieved = [pub['count'] for pub in publications_achieved_by_month]

  
    context = {
        'admin': admin,
        'donors': donors,
        'associations': associations,
        'pub': pub,
        'dons': dons,
        'users' : users,
        'donors' : donors,
        'total_dons_all' : total_dons_all,
        'categories': categories,
        'pending_reclamations_count': pending_reclamations_count,
        'alert': alert,
        'stats':stats,
        'unfunded_publications':unfunded_publications,
        'donations_per_month': donations_per_month,
        'months': months,
        'counts': counts,
        'responded_percentage': responded_percentage,
        'total_reclamations': total_reclamations,
        'responded_reclamations': responded_reclamations,
        'pending_reclamations':pending_reclamations,
        'pending_emails': pending_emails, 
        'emails': emails,
        'pending_count': pending_count,
        'pending_emails_monthly': pending_emails_monthly,
        'months_pub': months_pub,
        'counts_pub': counts_pub,
        'counts_pub_achieved': counts_pub_achieved,
    }
    return render(request, 'users/dashboardAdmin.html', context)
###################### / admin  / ##################

#########  se déconnecter ##############
def custom_logout(request):
    print('Logging out {}'.format(request.user))
    logout(request)
    print(request.user)
    return HttpResponseRedirect('/')  #direction  home

####################### Ajouter et modifier users #####################
###### Donor ############
@admin_required
def add_donor(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')  # Retrieve the password from the form

        try:
            validate_email(email)
        except ValidationError:
            return render(request, 'users/registerdonor.html', {'error': True, 'message': 'Entrez un email valide !'})
        
        if not name or not email or not password :
            return render(request, 'users/registerdonor.html', {'error': True, 'message': 'Veuillez remplir tous les champs nécessaires !'})
        
        if User.objects.filter(email=email).exists():
            return render(request, 'users/registerdonor.html', {'error': True, 'message': 'Un utilisateur avec cet email existe déjà !'})
        
        # Hash the password and create a new user
        utilisateur = User.objects.create_user(username=email, email=email, password=password, first_name=name)
        utilisateur.is_donor = True
        utilisateur.is_association = False
        utilisateur.is_admin=False
        utilisateur.is_active = True
        utilisateur.save()
        
        # Create a donor associated with the user
        donor = Donor.objects.create(
            user=utilisateur,
            phone_number=phone_number,
        )
        donor.save()

        return redirect('donors')

    return render(request, 'users/add_donor.html',{'error': False, 'message': ''})

def update_donor(request, donor_id):
    donor = get_object_or_404(Donor, id=donor_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        image = request.FILES.get('image')
        phone_number = request.POST.get('phone_number')
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        try:
            # Update donor attributes if corresponding data is provided
            
            if name:
                donor.user.first_name = name
            if email:
                donor.user.email = email
            if phone_number:
                donor.phone_number = phone_number
            if image:
                donor.image = image
            
            if old_password and new_password1 and new_password2:
                if not donor.user.check_password(old_password):
                    raise ValidationError("Old password is incorrect")
                if new_password1 != new_password2:
                    raise ValidationError("New passwords do not match")
                donor.user.set_password(new_password1)
                update_session_auth_hash(request, donor.user)
                authenticated_user = authenticate(request, username=email, password=new_password1)
                if authenticated_user is not None:
                     login(request, authenticated_user)

            # Save donor and associated user
            donor.user.save()
            donor.save()
            messages.success(request, 'Your informations have been updated successfully.')


        except ValidationError as e:
            # Handle validation errors
            return HttpResponseBadRequest(e)

    return render(request, 'users/update_donor.html', {'donor': donor})

@login_required
def delete_donor(request, donor_id):
    user= request.user
    donor = get_object_or_404(Donor, pk=donor_id) 
    donor_user = donor.user
    if user == donor_user or user.is_admin:
        donor_user.delete()
        donor.delete()
        if user == donor_user:
            logout(request)
            return redirect('/')  # Redirect to homepage or any other appropriate page
        if user.is_admin:
            return redirect('donors')
    else:
        return redirect('/')
    
    return redirect('/')


##### Association ########################

@admin_required
def add_association(request):
    if request.method == 'POST':
        name = request.POST.get('name', None)
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)
        telephone = request.POST.get('telephone', None)
        stat_juridique=request.FILES.get('stat_juridique',None)
        adresse=request.POST.get('adresse',None)
        image=request.POST.get('image',None)
        paypal_email=request.POST.get('paypal_email',None)


        try:
            validate_email(email)
        except ValidationError:
            return render(request, 'users/registerassociation.html', {'error': True, 'message': 'Entrez un email valide !'})

        if not name or not email or not password :
            return render(request, 'users/registerassociation.html', {'error': True, 'message': 'Veuillez remplir tous les champs nécessaires !'})
        
        if User.objects.filter(email=email).exists():
            return render(request, 'users/registerassociation.html', {'error': True, 'message': 'Un utilisateur avec cet email existe déjà !'})
        # Hash the password and create a new user
        utilisateur = User.objects.create_user(username=email, email=email, password=password, first_name=name)
        utilisateur.is_association = True
        utilisateur.is_donor=False
        utilisateur.is_admin=False
        utilisateur.is_active = True
        utilisateur.save()
        # Create a association associated with the user
        association = Association.objects.create(
            user=utilisateur,
            phone_number=telephone,
            stat_juridique=stat_juridique,
            image=image,  
            paypal_email=paypal_email,
            adresse=adresse, 
        )
        association.save()

        return redirect('associations')

    return render(request, 'users/add_association.html')

def update_association(request, association_id):
    association = get_object_or_404(Association, id=association_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        adresse = request.POST.get('adresse')
        stat_juridique=request.FILES.get('stat_juridique')
        image = request.FILES.get('image')
        paypal_email = request.POST.get('paypal_email')
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        try:
                if name:
                    association.user.first_name=name
                if email:
                    association.user.email = email
                if phone_number:
                    association.phone_number=phone_number
                if adresse:
                    association.adresse=adresse
                if stat_juridique:
                    association.stat_juridique=stat_juridique
                if image:
                    association.image=image
                if paypal_email:
                    association.paypal_email=paypal_email
                    
                if old_password and new_password1 and new_password2:
                    if not association.user.check_password(old_password):
                        raise ValidationError("Old password is incorrect")
                    if new_password1 != new_password2:
                        raise ValidationError("New passwords do not match")
                    association.user.set_password(new_password1)
                    update_session_auth_hash(request, association.user)
                    authenticated_user = authenticate(request, username=email, password=new_password1)
                    if authenticated_user is not None:
                        login(request, authenticated_user)
                
                association.user.save()
                association.save()
                
        except ValidationError as e:
                # Handle validation errors
                return HttpResponseBadRequest(e)

    return render(request, 'users/update_association.html', {'association': association})
@admin_required
def delete_association(request, association_id):
    association = Association.objects.get(pk=association_id)
    association.user.delete()
    association.delete()

    return redirect('associations')



###################### Password ######################

class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject.txt'
    
    success_url = reverse_lazy('password-reset/done')




############# Contact Association ##################

def contact_association(request, association_id):
    if request.method == 'POST':
        subject = request.POST.get('subject')
        sender_name = request.POST.get('sender_name')
        sender_email = request.POST.get('sender_email')
        message_content = request.POST.get('message')

        # Get the association based on association_id
        association = Association.objects.get(id=association_id)
        
        # Store the email details in the PendingEmail model for validation
        PendingEmail.objects.create(
            association=association,
            subject=subject,
            sender_name=sender_name,
            sender_email=sender_email,
            message_content=message_content
        )

        return render(request, 'users/contact_association.html', {
            'association': association,
            'success': True
        })

    else:
        # Retrieve the association details
        association = Association.objects.get(id=association_id)

        return render(request, 'users/contact_association.html', {'association': association})
@admin_required   
def manage_pending_emails(request):
    pending_emails = PendingEmail.objects.filter(processed=False)
    emails=PendingEmail.objects.filter(processed=True)


    if request.method == 'POST':
        action = request.POST.get('action')
        email_id = request.POST.get('email_id')
        pending_email = get_object_or_404(PendingEmail, id=email_id)

        if action == 'approve':
            # Compose and send the email
            association = pending_email.association
            message = f"Hello {association.user.first_name},\n\n"
            message += f"This is to inform you that {pending_email.sender_name} ({pending_email.sender_email}) wants to contact you.\n\n"
            message += f"Message Content:\n{pending_email.message_content}\n\n"
            message += "Please respond to this email to follow up.\n\n"
            message += "Best regards,\nHopeBloom"

            send_mail(
                subject=pending_email.subject,
                message=message,
                from_email=pending_email.sender_email,
                recipient_list=[association.user.email],
                fail_silently=False,
            )
            pending_email.approved = True
        elif action == 'deny':
            pending_email.approved = False

        pending_email.processed = True
        pending_email.save()
    context={
            'pending_emails': pending_emails, 
            'emails': emails,
    }

    return render(request, 'users/manage_pending_emails.html', context)

def contact_success(request):
    return render(request, 'users/contact_success.html')

####################################### Activate/desactivat Alert ###################################################
@admin_required
def activate_alert(request):
    if request.method == "POST":
        alert = Alert.objects.first()
        associations = Association.objects.filter(user__is_association=True, user__email__isnull=False).exclude(user__email='')
        donors = Donor.objects.filter(user__is_donor=True, user__email__isnull=False).exclude(user__email='')
        recipient_list_donor = [donor.user.email for donor in donors]
        recipient_list_association = [association.user.email for association in associations]
        from_email= settings.EMAIL_HOST_USER
        site_domain="http://127.0.0.1:8000/"
        message1=f"An alert has been activated. Please post the urgent cases about this alert situation as soon as possible on the platforme. {site_domain}"
        message2=f"An alert has been activated. Please check the platforme {site_domain} for details."
        subject='Alert Mode Activated'

        # Assuming there is only one alert object
        if not alert:
            alert = Alert.objects.create(is_active=True)
        else:
            alert.is_active = True
            alert.save()
        
        # Send email to all users
        send_mail(subject, message1, from_email, recipient_list_association)

        send_mail(subject, message2, from_email, recipient_list_donor)
        
        return redirect('dashboardAdmin')
    return render(request, 'activate_alert')
@admin_required
def desactivate_alert(request):
    if request.method == "POST":
        alert = Alert.objects.first()
        if alert:
            alert.is_active = False
            alert.save()
        return redirect('dashboardAdmin')
    return render(request, 'deactivate_alert.html')
