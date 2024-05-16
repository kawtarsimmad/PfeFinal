from django import forms
from .models import Publication,Category

class PublicationForm(forms.ModelForm):
    titre=forms.CharField(widget=forms.TextInput(attrs={"class":"form-control",'placeholder':'titre'}))
    contenu=forms.CharField(widget=forms.Textarea(attrs={"class":"form-control",'placeholder':'contenu'}))
    image=forms.ImageField()
    montant=forms.DecimalField(max_digits=20,decimal_places=2, widget=forms.TextInput(attrs={'placeholder': 'Enter amount'}))
    category = forms.ModelChoiceField(queryset=Category.objects.all())
    
    class Meta:
        model=Publication
        fields=['titre','contenu','image','montant', 'category']