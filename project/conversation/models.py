from django.db import models
from users.models import  User

class Conversation(models.Model):
    subject = models.CharField(max_length=255)
    participants = models.ManyToManyField(User)



class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    reply_to = models.ForeignKey('self', related_name='replies', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'Message from {self.sender} to {self.recipient}'
    class Meta:
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['is_read']),
        ]
