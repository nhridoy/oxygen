from django.db import models

from core import settings
from core.models import BaseModel
from utils.helpers import content_file_path


class ChatSession(BaseModel):
    name = models.CharField(max_length=256)
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="chat_rooms_participants"
    )
    room_id = models.CharField(max_length=256, unique=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "chat_sessions"
        verbose_name = "Chat Session"
        verbose_name_plural = "Chat Sessions"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["-created_at"])]

    def __str__(self):
        return str(self.room_id)


class ChatLog(BaseModel):
    room = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE, related_name="chat_messages_session"
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    content = models.CharField(max_length=1024, blank=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        db_table = "chat_logs"
        verbose_name = "Chat Log"
        verbose_name_plural = "Chat Logs"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["room", "created_at"]),
            models.Index(fields=["room", "is_read"]),
        ]

    def __str__(self):
        return str(self.room)


class ChatImage(BaseModel):
    room = models.ForeignKey(
        ChatLog, on_delete=models.CASCADE, related_name="chat_images_log"
    )
    attachment = models.FileField(upload_to=content_file_path)

    class Meta:
        db_table = "chat_images"
        verbose_name = "Chat Image"
        verbose_name_plural = "Chat Images"

    def __str__(self):
        return str(self.room)
