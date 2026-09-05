from autoslug import AutoSlugField
from django.db import models

from core.models import BaseModel


class Page(BaseModel):
    title = models.CharField(max_length=255)
    content = models.TextField()
    slug = AutoSlugField(populate_from="title", unique=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "pages"
        verbose_name = "Page"
        verbose_name_plural = "Pages"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["-created_at"]),
        ]
