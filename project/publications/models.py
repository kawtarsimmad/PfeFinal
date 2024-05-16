from django.db import models
from django.utils import timezone
from users.models import Association
from categories.models import Category

# Create your models here.

class Publication(models.Model):
    id=models.AutoField(primary_key=True)
    titre=models.CharField(max_length=150)
    contenu=models.TextField()
    date=models.DateTimeField(default=timezone.now)
    image=models.ImageField(upload_to='photos/%y/%m/%d', blank=True)
    montant=models.DecimalField(max_digits=20,decimal_places=2)
    association=models.ForeignKey(Association,on_delete=models.CASCADE,null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,null=True,blank=True)
    objects = models.Manager() 

    def __str__(self) :
        return self.titre 
    
    
    def calculate_total_dons(self):
        total_dons = sum(d.montantDons for d in self.dons.filter(est_paye=True))
        return total_dons
    
    @classmethod
    def calculate_total_dons_all(cls):
        total_dons_all = sum(publication.calculate_total_dons() for publication in cls.objects.all())
        return total_dons_all
