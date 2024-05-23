from django.shortcuts import render,redirect,get_object_or_404
from . models import Don
from publications.models import Publication
from users.models import Association
from .forms import PaiementForm
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid
from django.urls import reverse

def don(request):
    return render(request, 'dons/don.html')
def dons(request):
    return render(request, 'dons/dons.html',{'dn':Don.objects.all()})

def faire_don(request, publication_id):
    publication = get_object_or_404(Publication, pk=publication_id)
    #if request.user.has_perm('your_app_name.can_make_donation'):#
    if request.method == 'POST':
        form = PaiementForm(request.POST)
        if form.is_valid():
            montantDons = form.cleaned_data['montantDons']
            don = Don.objects.create(user=request.user, montantDons = montantDons, publication=publication)
            return CheckOut(request, don.id)
    else:
        form = PaiementForm()
    return render(request, 'dons/faire_don.html', {'form': form,'publication':publication})




def viewDons(request):
    dons = Don.objects.filter(user=request.user)
    if hasattr(request.user, 'dashboard_donor'):
        donor = request.user.dashboard_donor
    return render(request, 'dons/viewDons.html', {'dons': dons,'donor':donor})

def delete_don(request, don_id):
    reclamation = get_object_or_404(Don, id=don_id)
    reclamation.delete()
    return redirect('viewDons')


def CheckOut(request, don_id):

    don = Don.objects.get(id=don_id)
     # Récupérer l'association associée à la publication du don
    association = don.publication.association
    paypal_email = association.paypal_email
    host = request.get_host()

    paypal_checkout = {
        'business': paypal_email,
        'amount': don.montantDons,
        'item_name': don.id,
        'invoice': uuid.uuid4(),
        'currency_code': 'EUR',
        'notify_url': f"http://{host}{reverse('paypal-ipn')}",
        'return_url': f"http://{host}{reverse('payment-success', kwargs = {'don_id': don.id})}",
        'cancel_url': f"http://{host}{reverse('payment-failed', kwargs = {'don_id': don.id})}",
    }

    paypal_payment = PayPalPaymentsForm(initial=paypal_checkout)

    context = {
        'don': don,
        'paypal': paypal_payment
    }

    return render(request, 'dons/checkout.html', context)

def PaymentSuccessful(request, don_id):

    don = Don.objects.get(id=don_id)
    donor = request.user
     # Mettre à jour l'attribut est_paye à True
    don.est_paye = True
    don.save()

 # Enregistrement des détails de paiement dans un fichier
    with open('donsTrue.txt', 'a') as file:
        file.write(f"Id_Don: {don.id} , Donor:{donor.username}, Titre: {don.date}, Montant: {don.montantDons}\n")
        
    return render(request, 'dons/payment-success.html', {'don': don,'user': donor})

def paymentFailed(request, don_id):

    don = Don.objects.get(id=don_id)

    return render(request, 'dons/payment-failed.html', {'don': don})


