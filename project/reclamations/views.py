from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Reclamation
from .forms import ReclamationForm

# Create your views here.

def reclamation(request):
    if request.method == "POST":
        form = ReclamationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('reclamations')
    else:
        form = ReclamationForm()
    return render(request, 'reclamations/reclamation.html', {'form': form})


def reclamations(request):
    reclamations = Reclamation.objects.order_by('-created_at')
    return render(request, 'reclamations/reclamations.html', {'rc': reclamations})

@login_required
def create_reclamation(request):
    association = None
    donor=None
    if hasattr(request.user, 'dashboard_association'):
            association = request.user.dashboard_association
    elif hasattr(request.user, 'dashboard_donor'):
            donor = request.user.dashboard_donor
    if request.method == "POST":
        # Handle form submission to create a new reclamation
        form = ReclamationForm(request.POST)
        if form.is_valid():
            reclamation = form.save(commit=False)
            reclamation.user = request.user
            reclamation.status = 'Pending'  # Set default status for admin-created reclamations
            reclamation.save()
            return redirect('view_reclamations')
    else:
        # Render the reclamation creation form
        form = ReclamationForm()
    return render(request, 'reclamations/create_reclamation.html', {'form': form,'association':association,'donor':donor})


@login_required
def view_reclamations(request):
    association = None
    donor=None
    reclamations = Reclamation.objects.filter(user=request.user)
    if hasattr(request.user, 'dashboard_association'):
            association = request.user.dashboard_association
    elif hasattr(request.user, 'dashboard_donor'):
            donor = request.user.dashboard_donor
    context={
         'reclamations': reclamations,
         'association': association,
         'donor':donor,
    }
    return render(request, 'reclamations/view_reclamations.html',context)


@login_required
def delete_reclamation(request, reclamation_id):
    reclamation = get_object_or_404(Reclamation, id=reclamation_id)
    reclamation.delete()
    return redirect('view_reclamations')


@login_required
def update_reclamation(request, reclamation_id):
    association = None
    donor=None
    if hasattr(request.user, 'dashboard_association'):
            association = request.user.dashboard_association
    elif hasattr(request.user, 'dashboard_donor'):
            donor = request.user.dashboard_donor        
    reclamation = get_object_or_404(Reclamation, id=reclamation_id)
    if request.method == 'POST':
        form = ReclamationForm(request.POST, instance=reclamation)
        if form.is_valid():
            form.save()
            return redirect('view_reclamations')
    else:
        form = ReclamationForm(instance=reclamation)
    return render(request, 'reclamations/update_reclamation.html', {'form': form,'association':association,'donor':donor})

@login_required
def update_reclamation_status(request, reclamation_id):
    reclamation = get_object_or_404(Reclamation, id=reclamation_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        reclamation.status = new_status
        reclamation.save()
        return redirect('reclamations')
    return render(request, 'reclamations/update_reclamation_status.html', {'reclamation': reclamation})
