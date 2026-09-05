# Model and Migration Instructions

## Read First

Inspect the target app's models, migrations, serializers, and signals. Read [core/models.py](../../core/models.py). `article/models.py` illustrates a module; `options/models/` illustrates a package. Follow the target app's existing layout.

## Define the Model

1. Use `core.models.BaseModel` for ordinary domain entities requiring UUID IDs and `created_at`/`updated_at` timestamps. Inspect special inheritance before changing authentication models; preserve their user-model base.
2. For packaged models, use `<app>/models/<domain>_models.py` and export the class in `<app>/models/__init__.py` so Django discovers it.
3. Choose lengths, defaults, `blank`, and `null` deliberately. Specify relationship deletion behavior and meaningful `related_name` values. Reference the configured user model for user relationships.
4. Enforce durable invariants with database constraints where possible. Add indexes for actual filters/orderings without duplicating primary-key or unique indexes.
5. Add a useful `__str__` without unnecessary relationship queries. Reuse `CompressedImageField` when the existing WebP conversion behavior is needed.

## Validation and Integration

Keep reusable domain validation near the model. Do not assume `save()` calls `full_clean()` or that ModelSerializer runs model `clean()`. Ensure write paths explicitly enforce required validation; coordinate with [serializers](serializers.md).

For localized fields, inspect the app's `translation.py` and language settings. `article/translation.py` demonstrates English/Korean category names. Update applicable admin registration, serializer fields, and exports. Register necessary signals through the app's existing `AppConfig.ready()` pattern.

## Migrations and Verification

Run `uv run python manage.py makemigrations <app>` and review generated operations. Include migrations with model changes. Do not delete or rewrite migration history to hide conflicts. Plan defaults/backfills for required fields and use historical models in data migrations.

Run `uv run python manage.py makemigrations --check --dry-run`. Apply migrations only to the intended development/test database; inspect destructive operations and data preservation first. Follow [testing instructions](testing.md) for constraints, validation, relationship deletion, and affected API behavior.

## Example: Article Category Model

In `article/models.py`, use this structure for the category model. This example specifies the table name, admin labels, default ordering, and indexes explicitly:

```python
from django.db import models

from core.models import BaseModel, CompressedImageField


class ArticleCategory(BaseModel):
    name = models.CharField(max_length=100, blank=True)
    icon = CompressedImageField(quality=75, width=1920)
    description = models.TextField()

    class Meta:
        db_table = "article_categories"
        verbose_name = "Article Category"
        verbose_name_plural = "Article Categories"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return self.name
```

`BaseModel` supplies the UUID and timestamps. `blank=True` permits an empty name at model validation level; API write serializers may apply stricter requirements. Existing translation registration adds localized name fields, so inspect `article/translation.py` when editing them.

For an existing model, changing `db_table` requires a migration; do not create a second model or manually rename the database table. Generate and inspect the migration before applying it to a development database:

```bash
uv run python manage.py makemigrations article
uv run python manage.py migrate --plan
uv run python manage.py migrate
uv run python manage.py makemigrations --check --dry-run
```
