from django.shortcuts import render,redirect,get_object_or_404
from . models import Don
from publications.models import Publication
from users.models import Association
from .forms import PaiementForm
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid
from django.urls import reverse
from django.http import HttpResponse
from django.template.loader import get_template
from django.shortcuts import render
from django.conf import settings
from xhtml2pdf import pisa
import os
from io import BytesIO
from django.views import View
from django.utils import timezone
from django.db.models import F
from django.contrib.auth.decorators import login_required
from .decorators import donor_required 



def don(request):
    return render(request, 'dons/don.html')
def dons(request):
    dn=Don.objects.all().order_by(F('date').desc())
    return render(request, 'dons/dons.html',{'dn':dn})

@login_required
@donor_required 
def faire_don(request,  publication_id=None, association_id=None):
    publication = None
    association = None
    if publication_id:
        publication = get_object_or_404(Publication, pk=publication_id)
        montant_obj = publication.montant
        totalDons=publication.calculate_total_dons()  
        Montant_rest= (montant_obj - totalDons )
        publication.Montant_rest = Montant_rest
    elif association_id:
        association = get_object_or_404(Association, pk=association_id)
        
    if request.method == 'POST':
        form = PaiementForm(request.POST)
        if form.is_valid():
            montantDons = form.cleaned_data['montantDons']
            is_anonymous = form.cleaned_data['is_anonymous']
            
            if request.user.is_authenticated:  
                donateur = request.user    
            else:
                donateur = None

            if publication:
                don = Don.objects.create(
                    user=donateur,
                    date=timezone.now(),
                    montantDons=montantDons,
                    est_paye=False,
                    publication=publication,
                    is_anonymous=is_anonymous
                )
            elif association:
                don = Don.objects.create(
                    user=donateur,
                    date=timezone.now(),
                    montantDons=montantDons,
                    est_paye=False,
                    association=association,
                    is_anonymous=is_anonymous
                )
            return CheckOut(request, don.id)
    else:
        form = PaiementForm()

    context = {'form': form}
    if publication:
            context['publication'] = publication
            context['Montant_rest'] = Montant_rest
            context['totalDons'] = totalDons
    elif association:
            context['association'] = association
    return render(request, 'dons/faire_don.html',context)



def viewDons(request):
    dons = Don.objects.filter(user=request.user).order_by(F('date').desc())
    if hasattr(request.user, 'dashboard_donor'):
        donor = request.user.dashboard_donor
    return render(request, 'dons/viewDons.html', {'dons': dons,'donor':donor})

def DonsAssociation(request):
    association=request.user
    if hasattr(request.user, 'dashboard_association'):
        association = request.user.dashboard_association
    direct_donations = Don.objects.filter(publication__isnull=True,association=association,).order_by(F('date').desc())
    publication_donations = Don.objects.filter(publication__isnull=False,publication__association=association).order_by(F('date').desc())
    
    don_tab = list(direct_donations) + list(publication_donations)
    don_tab.sort(key=lambda x: x.date, reverse=True)

    context = {
        'association':association,
        'direct_donations': direct_donations,
        'publication_donations': publication_donations,
        'don_tab':don_tab
    }
    return render(request, 'dons/DonsAssociation.html', context)

def delete_don(request, don_id):
    reclamation = get_object_or_404(Don, id=don_id)
    reclamation.delete()
    return redirect('viewDons')



def CheckOut(request, don_id):

    don = get_object_or_404(Don, id=don_id)
    if don.publication:
        association = don.publication.association
        publication = don.publication
        montant_obj = publication.montant
        totalDons=publication.calculate_total_dons()  
        Montant_rest= (montant_obj - totalDons )
        publication.Montant_rest = Montant_rest

    if don.association:
        association=don.association

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
        'paypal': paypal_payment,
        'association': association,
    }
    if don.publication:
            context['publication'] = publication
            context['Montant_rest'] = Montant_rest
            context['totalDons'] = totalDons
    elif don.association:
            context['association'] = association

    return render(request, 'dons/checkout.html', context)

def PaymentSuccessful(request, don_id):

    don = Don.objects.get(id=don_id)
    donor = request.user
    if don.publication:
        association = don.publication.association
    if don.association:
        association = don.association

    don.est_paye = True
    don.save()

 # Enregistrement des détails de paiement dans un fichier
    with open('donsTrue.txt', 'a') as file:
        file.write(f"Id_Don: {don.id} , Donor:{donor.username}, Date: {don.date}, Montant: {don.montantDons}\n")
        
    return render(request, 'dons/payment-success.html', {'don': don,'user': donor, 'association':association})


def paymentFailed(request, don_id):

    don = Don.objects.get(id=don_id)

    return render(request, 'dons/payment-failed.html', {'don': don})

def fetch_resources(uri, rel):
    # Function to fetch external resources such as images and CSS
    if uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
    else:
        path = os.path.join(settings.BASE_DIR, uri)
    return path

def generate_pdf(request, don_id):
    try:
        # Retrieve the donation object
        don = Don.objects.get(id=don_id)
        donor = request.user
        association=None
        if don.publication:
            association = don.publication.association
        if don.association:
            association = don.association
        # Pass the donation object to the template context
        context = {'don': don, 'user': donor, 'association': association}

        # Render the template
        template = get_template('dons/payment-success.html')
        html = template.render(context)
        #css_=os.path.join(settings.STATIC_URL, 'assets/css/receipt.css')
        #bootstrap_css=os.path.join(settings.STATIC_URL, 'css/bootstrap.min.css')
        css = '''
        .receipt-content { background: #ECEEF4; font-family: Arial, sans-serif; }
        .container { width: 100%; max-width: 900px; margin: auto; padding: 20px; }
        .invoice-wrapper { background: #FFF; border: 1px solid #CDD3E2; padding: 40px; border-radius: 4px; }
        .intro { font-size: 16px; color: #444; }
        .payment-info { margin-top: 25px; padding-top: 15px; }
        .payment-info span, .payment-details span { color: #A9B0BB; }
        .payment-details { border-top: 2px solid #EBECEE; margin-top: 30px; padding-top: 20px; }
        .line-items { margin-top: 40px; }
        .headers { color: #A9B0BB; font-size: 13px; border-bottom: 2px solid #EBECEE; padding-bottom: 4px; }
        .items .item { padding: 10px 0; color: #696969; font-size: 15px; }
        .item { padding: 10px 0; color: #696969; font-size: 15px; }
        .item .amount { color: #84868A; font-size: 16px; }
        .total { margin-top: 30px; }
        .extra-notes { float: left; width: 40%; font-size: 13px; color: #7A7A7A; }
        .print { text-align: center; margin-top: 50px; }
        .print a { color: #708DC0; font-size: 13px; text-decoration: none; border: 1px solid #9CB5D6; padding: 10px 20px; border-radius: 5px; }
        .print a:hover { border-color: #333; color: #333; }
        .footer { margin-top: 40px; text-align: center; font-size: 12px; color: #969CAD; }
        
        .receipt-content .logo a:hover { text-decoration: none; color: #7793C4; }
        .receipt-content .invoice-wrapper { background: #FFF; border: 1px solid #CDD3E2; box-shadow: 0px 0px 1px #CCC; padding: 40px 40px 60px; margin-top: 40px; border-radius: 4px; }
        .receipt-content .invoice-wrapper .payment-details span { color: #A9B0BB; display: block; }
        .receipt-content .invoice-wrapper .payment-details a { display: inline-block; margin-top: 5px; }
        .receipt-content .invoice-wrapper .line-items .print a { display: inline-block; border: 1px solid #9CB5D6; padding: 13px 13px; border-radius: 5px; color: #708DC0; font-size: 13px; transition: all 0.2s linear; }
        .receipt-content .invoice-wrapper .line-items .print a:hover { text-decoration: none; border-color: #333; color: #333; }
        .receipt-content { background: #ECEEF4; }
        .receipt-content .container { width: 900px; }
        .receipt-content .logo { text-align: center; margin-top: 50px; }
        .receipt-content .logo a { font-family: Myriad Pro, Lato, Helvetica Neue, Arial; font-size: 36px; letter-spacing: .1px; color: #555; font-weight: 300; transition: all 0.2s linear; }
        .receipt-content .invoice-wrapper .intro { line-height: 25px; color: #444; }
        .receipt-content .invoice-wrapper .payment-info { margin-top: 25px; padding-top: 15px; }
        .receipt-content .invoice-wrapper .payment-info span { color: #A9B0BB; }
        .receipt-content .invoice-wrapper .payment-info strong { display: block; color: #444; margin-top: 3px; }
        .receipt-content .invoice-wrapper .payment-details { border-top: 2px solid #EBECEE; margin-top: 30px; padding-top: 20px; line-height: 22px; }
        .receipt-content .invoice-wrapper .line-items { margin-top: 40px; }
        .receipt-content .invoice-wrapper .line-items .headers { color: #A9B0BB; font-size: 13px; letter-spacing: .3px; border-bottom: 2px solid #EBECEE; padding-bottom: 4px; }
        .receipt-content .invoice-wrapper .line-items .items { margin-top: 8px; border-bottom: 2px solid #EBECEE; padding-bottom: 8px; }
        .receipt-content .invoice-wrapper .line-items .items .item { padding: 10px 0; color: #696969; font-size: 15px; }
        .receipt-content .invoice-wrapper .line-items .items .item .amount { letter-spacing: 0.1px; color: #84868A; font-size: 16px; }
        .receipt-content .invoice-wrapper .line-items .total { margin-top: 30px; }
        .receipt-content .invoice-wrapper .line-items .total .extra-notes { float: left; width: 40%; text-align: left; font-size: 13px; color: #7A7A7A; line-height: 20px; }
        .receipt-content .invoice-wrapper .line-items .total .extra-notes strong { display: block; margin-bottom: 5px; color: #454545; }
        .receipt-content .invoice-wrapper .line-items .total .field { margin-bottom: 7px; font-size: 14px; color: #555; }
        .receipt-content .invoice-wrapper .line-items .total .field.grand-total { margin-top: 10px; font-size: 16px; font-weight: 500; }
        .receipt-content .invoice-wrapper .line-items .total .field.grand-total span { color: #20A720; font-size: 16px; }
        .receipt-content .invoice-wrapper .line-items .total .field span { display: inline-block; margin-left: 20px; min-width: 85px; color: #84868A; font-size: 15px; }
        .receipt-content .invoice-wrapper .line-items .print { margin-top: 50px; text-align: center; }
        .receipt-content .invoice-wrapper .line-items .print a i { margin-right: 3px; font-size: 14px; }
        .receipt-content .footer { margin-top: 40px; margin-bottom: 110px; text-align: center; font-size: 12px; color: #969CAD; }
        
        '''
        #html_with_css = f'<link rel="stylesheet" href="{bootstrap_css}"><style>{css}</style>{html}'
        html_with_css = f'<style>{css}</style>{html}'

        # Create a PDF file
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="receipt_{don_id}.pdf"'

        # Define CSS path if needed
        # css_path = '/path/to/your/css/file.css'

        # Create PDF
        pisa_status = pisa.CreatePDF(
            src=html_with_css,
            dest=response,
            #encoding='UTF-8',  # Uncomment this line if you have encoding issues
            # css=css_path,      # Uncomment this line if you have an external CSS file
            link_callback=fetch_resources
        )

        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')

        return response
    except Don.DoesNotExist:
        return HttpResponse('Donation not found')
    except Exception as e:
        return HttpResponse(f'An error occurred: {str(e)}')
 
     
