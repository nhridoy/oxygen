from django.db import models

from core.models import BaseModel, CompressedImageField


class Notice(BaseModel):
    user = models.ForeignKey(
        "authentications.User", on_delete=models.CASCADE, related_name="notices"
    )
    title = models.CharField(max_length=255)
    body = models.TextField()
    image = CompressedImageField(quality=75, width=1920, blank=True, null=True)

    class Meta:
        db_table = "notices"
        verbose_name = "Notice"
        verbose_name_plural = "Notices"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "-created_at"])]

    def __str__(self):
        return self.title
