from django import forms

class PaiementForm(forms.Form):
    montantDons = forms.DecimalField(label='Montant du don', max_digits=10, decimal_places=2)