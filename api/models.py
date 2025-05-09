import uuid
from django.db import models

# Create your models here.


class Conversation(models.Model):
    class State(models.TextChoices):
        OPEN = 'OPEN', 'Open'
        CLOSED = 'CLOSED', 'Closed'
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    state = models.CharField(max_length=6, choices=State.choices, default="OPEN")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} - {self.state}"


class Message(models.Model):
    class Direction(models.TextChoices):
        SENT = "SENT", "Sent"
        RECEIVED = "RECEIVED", "Received"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, verbose_name="conversation", related_name="messages", on_delete=models.CASCADE)
    direction = models.CharField(max_length=8, choices=Direction.choices)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.state} message in Conversation #{self.conversation.id}"
