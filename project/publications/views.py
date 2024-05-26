from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse,reverse_lazy
from . models import Publication
from dons.models import Don
from .forms import PublicationForm
from django.http import HttpResponse
from django.http import JsonResponse
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid
from django.urls import reverse
from django.core.mail import send_mail
from categories.models import Category
from users.models import Donor,Association
from commentaires.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages



def publication(request):
    if request.method == "POST":
            form=PublicationForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('publications')
    else:
        form = PublicationForm()        
    return render(request, 'publications/publication.html', {'form': form})

def publications(request):
    publications = Publication.objects.all()
    dons = Don.objects.all()
    for publication in publications:
            total_dons = publication.calculate_total_dons()
            if   total_dons >= publication.montant  :
                if 'notified_publications' not in request.session:
                    request.session['notified_publications'] = []
                
                if publication.id not in request.session['notified_publications']:
                    messages.info(request, f"Votre publication {publication.id}. \"{publication.titre}\" a atteint son objectif de financement.")
                    # Ajouter l'ID de la publication à la liste des publications notifiées
                    request.session['notified_publications'].append(publication.id)
                    request.session.modified = True   

    return render(request, 'publications/publications.html', {'publications': publications,'dons':dons,'nombre_publications_total_dons':nombre_publications_total_dons})

def publicationIndex(request):
    publications = Publication.objects.order_by('-date')
    publication_data = []
    
    for publication in publications:
        montant_obj = publication.montant
        totalDons=publication.calculate_total_dons()
        Montant_rest= (montant_obj - totalDons )
        publication.Montant_rest = Montant_rest
        if totalDons > 0:
            progress_percent = (totalDons / montant_obj) * 100
        else:
            progress_percent = 0
        publication.progress_percent = progress_percent  # Add progress_percent
      
    context = {
        'publications': publications,
        'publication_data': publication_data,
        'totalDons':totalDons,
        'Montant_rest':Montant_rest
    }

    return render(request, 'publications/publicationIndex.html',context)




def PubDetail(request, pk):
    publication = get_object_or_404(Publication, pk=pk)
    dons = publication.dons.filter(est_paye=True) # Récupérer tous les dons associés à cette publication
    content_type = ContentType.objects.get_for_model(publication)
    comments = Comment.objects.filter(content_type=content_type, object_id=publication.id)
    association = publication.association
    montant_obj = publication.montant
    totalDons=publication.calculate_total_dons()  
    Montant_rest= (montant_obj - totalDons )
    publication.Montant_rest = Montant_rest

    if totalDons > 0:
        progress_percent = (totalDons / montant_obj) * 100
    else:
        progress_percent = 0
    publication.progress_percent = progress_percent  # Add progress_percent

        
    context={
        'publication': publication,
        'dons': dons,
        'totalDons':totalDons,
        'Montant_rest':Montant_rest,
        'progress_percent':progress_percent,
        'comments': comments,
        'association':association,
    }

    return render(request, 'publications/detail.html', context)
 


def PubCreate(request):
    if hasattr(request.user, 'dashboard_association'):
        association = request.user.dashboard_association
    if request.method == "POST":
        form=PublicationForm(request.POST, request.FILES)
        user=request.user
        if form.is_valid():
            publication=form.save(commit=False)
            association_instance = get_object_or_404(Association, user=request.user)
            publication.association = association_instance            
            urgent_category = Category.objects.get(name='Urgent')

            if publication.category == urgent_category:
                publication.save()  # Save the publication first
                send_email_alert(publication)  # Then send email alert
            else:
                publication.save()  # Save the publication
                
            if user.is_admin:
                  return redirect('publications')
            elif user.is_association:
                 return redirect('PubList')
            
    else:
        form = PublicationForm()
    return render(request, 'publications/form.html', {'form': form,'association':association})

#################### send an alert email ############################
def send_email_alert(publication):
    # Retrieve all donors with valid email addresses
    donors = Donor.objects.filter(user__is_donor=True, user__email__isnull=False).exclude(user__email='')
    recipient_list = [donor.user.email for donor in donors]
    site_domain = "http://127.0.0.1:8000/categories/Urgent/"
    # Send email to donors if there are recipients
    if recipient_list:
        subject = f"Urgent Publication: {publication.titre}"
        message = f"Dear donor, a new urgent publication '{publication.titre}' has been posted on our platform. Visit {site_domain} to learn more."
        from_email = settings.EMAIL_HOST_USER

        try:
            send_mail(subject, message, from_email, recipient_list)
            return True
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False    
    else:
        return False  
##############################################################

  

@login_required
def PubUpdate(request, pk):
    if hasattr(request.user, 'dashboard_association'):
        association = request.user.dashboard_association
    publication = get_object_or_404(Publication, pk=pk)
    if request.method == 'POST':
        form = PublicationForm(request.POST, request.FILES, instance=publication)
        user=request.user
        if form.is_valid():
            form.save()
            if user.is_admin:
                  return redirect('publications')
            elif user.is_association:
                 return redirect('PubList')
               
    else:
        form = PublicationForm(instance=publication)
    return render(request, 'publications/form.html', {'form': form,'association':association})


@login_required
def PubDelete(request, publication_id):
    publication = get_object_or_404(Publication, pk=publication_id)
    user=request.user
    publication.delete()
    if user.is_admin:
            return redirect('publications')
    elif user.is_association:
            return redirect('PubList')
    



#PubList retourne pubs de user connecté
@login_required
def PubList(request):
    if hasattr(request.user, 'dashboard_association'):
        association = request.user.dashboard_association
        publications = Publication.objects.filter(association=association)
        for publication in publications:
            total_dons = publication.calculate_total_dons()
            if   total_dons >= publication.montant  :
                if 'notified_publications' not in request.session:
                    request.session['notified_publications'] = []
                
                if publication.id not in request.session['notified_publications']:
                    messages.info(request, f"Votre publication {publication.id}. \"{publication.titre}\" a atteint son objectif de financement.")
                    # Ajouter l'ID de la publication à la liste des publications notifiées
                    request.session['notified_publications'].append(publication.id)
                    request.session.modified = True    
        return render(request, 'publications/list.html', {'association':association,'publications': publications})
    else:
        messages.error(request, "Vous n'avez pas de droits d'accès à cette page.")
        return render(request, 'publications/list.html', {'publications': []})

def dons_associes(request, publication_id):

    publication = Publication.objects.get(id=publication_id)
    dons = Don.objects.filter(publication=publication)
    total_dons = publication.calculate_total_dons()
    total_dons_all = Publication.calculate_total_dons_all()
    
    return render(request, 'publications/dons_associes.html', {'publication': publication, 'dons': dons,'total_dons_all': total_dons_all})
#######################################################""
def nombre_publications_total_dons():
    publications = Publication.objects.all()
    count = 0
    for publication in publications:
        montant_voulu=publication.montant
        total_dons = publication.calculate_total_dons()
        if total_dons >= montant_voulu:
            count += 1
    return count

