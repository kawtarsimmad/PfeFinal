from django.db import models
from django.utils import timezone
from users.models import Donor, Association, User

# Create your models here.


class Reclamation(models.Model):
    RECLAMATION_TYPES = [
        ('Payment', 'Payment Issue'),
        ('Posts', 'Posts Issue'),
        ('Other', 'Other Issue')
        # Add more types as needed
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Resolved', 'Resolved'),
        ('Refused', 'Refused'),
        # Add more statuses as needed
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recl_type = models.CharField(max_length=100, choices=RECLAMATION_TYPES,default="Other")
    description = models.TextField(max_length=100, default="Your default description here")
    status = models.CharField(max_length=100, default='Pending')  # Status as a regular field
    created_at = models.DateTimeField(default=timezone.now)
    objects = models.Manager() 

    