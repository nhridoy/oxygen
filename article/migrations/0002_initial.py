# Generated by Django 5.1.7 on 2025-03-29 08:35

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("article", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="article",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="articles",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Article Author",
            ),
        ),
        migrations.AddField(
            model_name="article",
            name="category",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="articles",
                to="article.articlecategory",
            ),
        ),
        migrations.AddField(
            model_name="articlecomment",
            name="article",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="article_comments",
                to="article.article",
            ),
        ),
        migrations.AddField(
            model_name="articlecomment",
            name="parent_comment",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="replies",
                to="article.articlecomment",
            ),
        ),
        migrations.AddField(
            model_name="articlecomment",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="article_comments",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Comment by",
            ),
        ),
        migrations.AddField(
            model_name="articlelike",
            name="article",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="article_like",
                to="article.article",
            ),
        ),
        migrations.AddField(
            model_name="articlelike",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="article_likes",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Liked by",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="articlelike",
            unique_together={("article", "user")},
        ),
    ]
