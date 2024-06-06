from django.db import models
from django.utils import timezone
from users.models import Donor,User,Association
from publications.models import Publication
class Don(models.Model): 
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    id=models.AutoField(primary_key=True)
    date=models.DateTimeField(default=timezone.now)
    montantDons=models.DecimalField(max_digits=10,decimal_places=4)
    est_paye = models.BooleanField(default=False)
    publication = models.ForeignKey(Publication, on_delete=models.SET_NULL, related_name='dons', null=True, blank=True)
    association = models.ForeignKey(Association, on_delete=models.SET_NULL, related_name='dons', null=True, blank=True)
    is_anonymous = models.BooleanField(default=False)

    
    objects = models.Manager() 
    
    def __str__(self) :
        user_display = "Anonyme" if self.is_anonymous else self.user.first_name
        return f"Don de {user_display} - Montant: {self.montantDons} - Payé: {self.est_paye}"
