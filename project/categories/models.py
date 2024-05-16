from django.db import models

# Create your models here.
class Category(models.Model):

    id=models.AutoField(primary_key=True, unique=True)
    name=models.CharField(max_length=50)
    objects = models.Manager() 

    def __str__(self) :
        return self.name
  
        