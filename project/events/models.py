from django.db import models
from users.models import Association,User
# Create your models here.

class Event(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    image=models.ImageField(upload_to='photos/%y/%m/%d', blank=True)
    location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    max_attendees = models.PositiveIntegerField(default=0)  # Maximum number of attendees
    attendees = models.ManyToManyField(User, related_name='attended_events', blank=True)
    
    def __str__(self):
        return self.title