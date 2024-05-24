from django.shortcuts import render
from publications.models import Publication
from categories.models import Category
from dons.models import Don
from users.models import Association,User,Donor
from events.models import Event
from users.models import Alert
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .forms import SearchForm
from django.db.models import Q



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
    alert = Alert.objects.first()


    events=Event.objects.order_by('-date')[:3]
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

    
    form = SearchForm()
    context = {
        'form': form,
        'events': events,
        'categories': categories,
        'publications': publications,
        'pub': pub,
        'dons': dons,
        'users' : users,
        'associations':associations,
        'donors' : donors,
        'total_dons_all' : total_dons_all,
        'events': event_data,
        'totalDons':totalDons,
        'Montant_rest':Montant_rest,
        'alert' : alert,

    }

    return render(request, 'pages/index.html', context)


def search(request):
    form = SearchForm()
    query = None
    publication_results = []
    event_results = []
    user_results = []
    association_results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            publication_results = Publication.objects.filter(titre__icontains=query)
            event_results = Event.objects.filter(title__icontains=query)
            user_results = User.objects.filter(username__icontains=query)
            user_results = User.objects.filter(first_name__icontains=query)
            association_results = Association.objects.filter(
                            Q(user__username__icontains=query) | 
                            Q(user__first_name__icontains=query)
            )
            if association_results.exists():
                association = association_results.first()
                publication_results = Publication.objects.filter(association=association)
                event_results=Event.objects.filter(user=association.user)

    return render(request, 'pages/search.html', {
        'form': form,
        'query': query,
        'publication_results': publication_results,
        'event_results': event_results,
        'user_results': user_results,
        'association_results': association_results,
     })

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
