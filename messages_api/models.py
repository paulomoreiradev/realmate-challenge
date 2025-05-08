import uuid
from django.db import models

# Create your models here.


class Conversation(models.Model):
    STATE_CHOICES = [
        ("OPEN", "Open"),
        ("CLOSED", "Closed"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    state = models.CharField(max_length=6, choices=STATE_CHOICES, default="OPEN")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation #{self.id} ({self.state})"


class Message(models.Model):
    TYPE_CHOICES = [
        ('SENT', 'Sent'),
        ('RECEIVED', 'Received'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, verbose_name="conversation", related_name="messages", on_delete=models.CASCADE)
    state = models.CharField(max_length=8, choices=TYPE_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} message in Conversation #{self.conversation.id}"
