from django.db import models
from django.utils import timezone
from users.models import Donor,User
from publications.models import Publication
class Don(models.Model): 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id=models.AutoField(primary_key=True)
    date=models.DateTimeField(default=timezone.now)
    montantDons=models.DecimalField(max_digits=10,decimal_places=4)
    est_paye = models.BooleanField(default=False)
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name='dons', null=True)

    
    objects = models.Manager() 
    
    def __str__(self) :
        return f"Don de {self.user.first_name} - Montant: {self.montantDons} - Payé: {self.est_paye}"  