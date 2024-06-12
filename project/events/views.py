from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from commentaires.models import Comment
from users.models import Association, User
from django.contrib.contenttypes.models import ContentType
from .models import Event
from .forms import EventForm
from publications.models import Publication
from django.utils import timezone
from .decorators import donor_required 



@login_required
def event_list(request):
    if hasattr(request.user, 'dashboard_association'):
        association = request.user.dashboard_association
    events = Event.objects.filter(user=request.user)
    return render(request, 'events/event_list.html', {'events': events,'association': association})

def events(request):
    events = Event.objects.all() # Retrieve all events from the database
    return render(request, 'events/events.html', {'events': events})

def donor_event_list(request):
    donor = request.user
    events_attended = donor.attended_events.all()
    return render(request, 'events/donor_event_list.html', {'events_attended': events_attended,'donor':donor})

def eventIndex (request):
    events = Event.objects.all()
    for event in events:
        num_attendees = event.attendees.count()
        if event.max_attendees > 0:
            progress_percent = (num_attendees / event.max_attendees) * 100
        else:
            progress_percent = 0
        event.progress_percent = progress_percent  # Add progress_percent to each event object
    
    return render(request, 'events/eventIndex.html', {'events': events})

def create_event(request):
    association = None
    donor=None
    if hasattr(request.user, 'dashboard_association'):
            association = request.user.dashboard_association
    elif hasattr(request.user, 'dashboard_donor'):
            donor = request.user.dashboard_donor
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            user=request.user
            # Save the event with the current authenticated user
            event = form.save(commit=False)
            event.user = request.user  # Set the event's user to the current authenticated user
            event.save()
            if user.is_admin:
                  return redirect('events')
            elif user.is_association:
                 return redirect('event_list')
    else:
        form = EventForm()
    
    return render(request, 'events/create_event.html', {'form': form,'association':association,'donor':donor})
@donor_required 
def participate_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    
    if request.user.is_authenticated and request.user.is_donor:
        if request.user not in event.attendees.all():
            # Add the current user (donor) to the event's attendees
            event.attendees.add(request.user)
            event.save()

    return redirect('detail_events', pk=event.pk)

@login_required
def cancel_participation(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    
    if request.user.is_authenticated and request.user.is_donor:
        if request.user in event.attendees.all():
            # Remove the current user (donor) from the event's attendees
            event.attendees.remove(request.user)
            event.save()
    
    return redirect('donor_event_list')

def EventDetail(request, pk):
    events = get_object_or_404(Event, pk=pk)
    num_attendees = events.attendees.count()
    content_type = ContentType.objects.get_for_model(events)
    comments = Comment.objects.filter(content_type=content_type, object_id=events.id)
    publications = Publication.objects.order_by('-date')[:3]  # Filter by 'association' field
    association = Association.objects.get(user=events.user)  # Get the association related to the event
    current_datetime = timezone.now()

    
    if events.max_attendees > 0:
        progress_percent = (num_attendees / events.max_attendees) * 100
    else:
        progress_percent = 0

    return render(request, 'events/event_detail.html', {'events': events, 'progress_percent': progress_percent,'comments': comments, 'publications': publications, 'association': association,  'current_datetime': current_datetime})
 

@login_required
def EventDelete(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    user=request.user
    event.delete()
    if user.is_admin:
            return redirect('events')
    elif user.is_association:
            return redirect('event_list')

@login_required
def update_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    association = None
    donor = None

    if hasattr(request.user, 'dashboard_association'):
        association = request.user.dashboard_association
    elif hasattr(request.user, 'dashboard_donor'):
        donor = request.user.dashboard_donor

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            user = request.user
            if user.is_admin:
                return redirect('events')
            elif user.is_association:
                return redirect('event_list')
    else:
        form = EventForm(instance=event)
    
    return render(request, 'events/update_event.html', {'form': form, 'association': association, 'donor': donor, 'event': event})


@login_required
def attendees_list(request, event_id):
    association=None
    if hasattr(request.user, 'dashboard_association'):
        association = request.user.dashboard_association
    event = get_object_or_404(Event, id=event_id)
    attendees = event.attendees.all()  # Assuming `attendees` is a many-to-many relationship field in the Event model
    context = {
        'event': event,
        'attendees': attendees,
        'association': association,
    }
    return render(request, 'events/attendees_list.html', context)
