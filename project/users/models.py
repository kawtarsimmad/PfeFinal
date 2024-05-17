from django.db import models
from django.contrib.auth.models import AbstractUser,User, Group, Permission
from PIL import Image
# Create your models here.



class User(AbstractUser):
    is_association= models.BooleanField(default=False)
    is_donor = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    groups = models.ManyToManyField(Group, related_name='user_groups')
    user_permissions = models.ManyToManyField(Permission, related_name='user_permissions')
    email_confirmed = models.BooleanField(default=False)
    confirmation_token = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.email
   
class Donor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True, related_name='dashboard_donor')
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    image = models.ImageField(upload_to='donor/profile', default='Default/user.png')

    objects = models.Manager() 
    
    def __str__(self):
        return "Donor Name : " + self.user.first_name
    
class Association(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True, related_name='dashboard_association')
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    stat_juridique = models.FileField(upload_to='documents/', null=True, blank=True)
    adresse=models.CharField(max_length=150,null=True,default=None,verbose_name='address')
    paypal_email=models.EmailField(max_length=254, default='sb-association@gmail.com',verbose_name='paypal address')
    image = models.ImageField(upload_to='admin/profile', default='Default/user.png')

    objects = models.Manager() 
    
    def __str__(self):
        return "Association Name : " + self.user.username
  


class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True, related_name='dashboard_admin')
    image = models.ImageField(upload_to='admin/profile', default='Default/user.png')
    objects = models.Manager() 
    
    def __str__(self):
        return "Admin Name : " + self.user.first_name
 
