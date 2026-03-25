from django.db import models
from users.models import User


class Chat(models.Model):
    initiator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chats_started")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chats_received")

    is_typing = models.BooleanField(default=False)

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["initiator", "receiver"],
                name="unique_chat_pair"
            )
        ]

    def __str__(self):
        return f"{self.initiator.email} -> {self.receiver.email}"


class Message(models.Model):
    STATUS_CHOICES = (
        ("sent", "Sent"),
        ("delivered", "Delivered"),
        ("read", "Read"),
    )
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")

    content = models.TextField()

    is_read = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="sent")
    deleted_at = models.DateTimeField(blank=True, null=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.sender.email} -> {self.receiver.email}"