from django.db import models

from core.models import BaseModel


class Notification(BaseModel):
    user = models.ForeignKey(
        "authentications.User", on_delete=models.CASCADE, related_name="notifications"
    )
    title = models.CharField(max_length=255)
    body = models.TextField()
    link = models.URLField(blank=True, null=True)
    notification_type = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)

    class Meta:
        db_table = "notifications"
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["user", "is_read"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.title}"
