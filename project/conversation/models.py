from django.db import models
from users.models import  User
from django.utils import timezone


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'Message from {self.sender} to {self.recipient} at {self.timestamp}'
    class Meta:
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['is_read']),
        ]
