from django.shortcuts import render
from publications.models import Publication
from categories.models import Category
from dons.models import Don
from users.models import Association,User,Donor
from events.models import Event
from django.http import JsonResponse
from django.views.decorators.http import require_GET




# Create your views here.
def index(request):
    publications = Publication.objects.order_by('-date')[:3]  # Fetch all publications
    pub=Publication.objects.all()
    categories= Category.objects.all()
    dons = Don.objects.all()
    users=User.objects.all()
    associations=Association.objects.all()
    donors=Donor.objects.all()
    total_dons_all = Publication.calculate_total_dons_all()####total des dons  de tous les publications 

    events=Event.objects.order_by('-date')[:3]
    publication_data = []
    event_data = []

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
      
    
    for event in events:
        num_attendees = event.attendees.count()
        
        if event.max_attendees > 0:
            progress_percent = (num_attendees / event.max_attendees) * 100
        else:
            progress_percent = 0

        event_data.append({
            'event': event,
            'num_attendees': num_attendees,
            'progress_percent': progress_percent
        })

    

    context = {
        'events': events,
        'categories': categories,
        'publications': publications,
        'pub': pub,
        'dons': dons,
        'users' : users,
        'associations':associations,
        'donors' : donors,
        #'total_dons_all' : total_dons_all,
        'events': event_data,
        'publication_data': publication_data,
        #'totalDons':totalDons,
        #'Montant_rest':Montant_rest
    }
    #publications = Publication.objects.order_by('date')[:2]
     #######admin_user = User.objects.filter(is_superuser=True).first()
    #if admin_user:
        # Filtrer les publications créées par l'administrateur
        #publications = Publication.objects.filter(user=admin_user)
    #else:
        #publications = []  # Aucun administrateur trouvé, donc aucune publication à afficher

    #children_category = Category.objects.filter(id="1").first()

    #if children_category:
        # Filtrer les publications appartenant à la catégorie "children"
        #publications = Publication.objects.filter(category_id=children_category)
    #else:
        #publications = []  # Aucune catégorie "children" trouvée, donc aucune publication à afficher

    return render(request, 'pages/index.html', context)


def latest_publications(request):
    # Retrieve latest publications ordered by date (newest first)
    latest_publications = Publication.objects.order_by('-date')[:3]  # Get latest 3 publications

    context = {
        'publications': latest_publications
    }
    return render(request, 'pages/index.html', context)


def association_list (request):
    association_list=Association.objects.all()
    return render (request,'users/association_list.html',{'association_list': association_list})
