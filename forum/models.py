from autoslug import AutoSlugField
from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseModel, CompressedImageField


class Tag(BaseModel):
    tag_name = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["tag_name"]
        indexes = [models.Index(fields=["tag_name"], name="idx_forum_tag_name")]

    def __str__(self):
        return self.tag_name


class Forum(BaseModel):
    slug = AutoSlugField(populate_from="title", unique=True)
    title = models.CharField(max_length=100)
    content = models.TextField()
    user = models.ForeignKey(
        "authentications.User",
        on_delete=models.PROTECT,
        related_name="forums",
        verbose_name="Forum Author",
    )
    tags = models.ManyToManyField(Tag, related_name="forums")
    total_like = models.PositiveIntegerField(default=0, editable=False)
    total_comment = models.PositiveIntegerField(default=0, editable=False)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["-total_like"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self):
        return self.title


class ForumImage(BaseModel):
    image = CompressedImageField(quality=75, width=1920)
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE, related_name="images")


class ForumComment(BaseModel):
    content = models.TextField()
    image = CompressedImageField(quality=75, width=1920, blank=True, null=True)
    forum = models.ForeignKey(
        Forum, on_delete=models.CASCADE, related_name="forum_comments"
    )
    parent_comment = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="replies",
        null=True,
        blank=True,
    )
    user = models.ForeignKey(
        "authentications.User",
        on_delete=models.PROTECT,
        related_name="forum_comments",
        verbose_name="Comment by",
    )

    def clean(self):
        errors = {}
        if self.parent_comment and self.parent_comment.forum_id != self.forum_id:
            errors.setdefault("parent_comment", []).append(
                "Parent comment must belong to the same forum."
            )
        if errors:
            raise ValidationError(errors)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["forum", "-created_at"]),
            models.Index(fields=["forum", "parent_comment"]),
        ]

    def get_replies(self):
        return ForumComment.objects.filter(comment=self)

    def __str__(self):
        return f"Comment by {self.user.user_information.full_name} on {self.forum}"


class ForumLike(BaseModel):
    forum = models.ForeignKey(
        Forum, on_delete=models.CASCADE, related_name="forum_likes"
    )
    user = models.ForeignKey(
        "authentications.User",
        on_delete=models.PROTECT,
        related_name="forum_likes",
    )

    class Meta:
        indexes = [models.Index(fields=["forum", "user"])]
