# Serializer Instructions

## Placement and Fields

Inspect the target app's serializers and consumers. Use `<app>/serializers/<domain>_serializers.py` where the app uses a package; update its `__init__.py` exports. Name classes by role, such as `ArticleListSerializer`, `ArticleDetailSerializer`, and `ArticleCategoryCreateSerializer`.

Use ModelSerializer for model representations and Serializer for independent command inputs. Enumerate `Meta.fields` explicitly rather than exposing every model field. Mark identifiers, timestamps, ownership, counters, and computed fields read-only as appropriate. Mark sensitive inputs write-only and use established authentication helpers for password hashing.

## Validation and Writes

1. Use `validate_<field>()` for individual values and `validate()` for cross-field rules. Raise `serializers.ValidationError` with actionable field errors.
2. Handle partial updates: missing fields may need values from `self.instance`; absence does not mean null or reset.
3. Validate relationships against the permitted user and parent resource. The parent-comment validator in `article/serializers/article_serializers.py` illustrates same-article validation; enforce equivalent rules on every relevant write path.
4. Assign ownership from the authenticated request in the view/service, not a submitted user ID. Scope writable relationship querysets where access is restricted.
5. Override `create()`/`update()` only when needed. Make dependent multi-record writes atomic and define nested-write behavior explicitly.

ModelSerializer does not automatically run model `clean()`. Coordinate domain invariants with [model instructions](models.md); request validation alone does not guarantee database integrity.

## Read Performance and Verification

Keep list payloads small; separate detail representations where useful. Coordinate nested fields and SerializerMethodField queries with the view's related-object loading. Bound recursive representations and preserve context when nested serializers need the request.

Follow [testing instructions](testing.md). Cover invalid inputs, partial updates, unauthorized relationships, protected fields, and sensitive-field exclusion. Verify actual rendered responses using [API instructions](apis.md), not only `serializer.data`.

## Example: Read-Only Category Representation

The following illustrative catalog serializer goes in `article/serializers/article_serializers.py`. It exposes a deliberate field list and keeps all catalog fields read-only:

```python
from rest_framework import serializers

from article.models import ArticleCategory


class ArticleCategoryCatalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleCategory
        fields = ("id", "name", "icon", "description", "created_at")
        read_only_fields = fields
```

Export `ArticleCategoryCatalogSerializer` from `article/serializers/__init__.py` alongside the existing exports. The `name` field follows the active language through the existing modeltranslation setup.

For a separate write serializer, this field validator illustrates rejecting whitespace-only English names. Add it to the existing category write serializer only when that requirement is part of the task:

```python
    def validate_name_en(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Enter an English category name.")
        return value
```

Declare `name_en` in that write serializer's fields. If it must always be supplied on creation, configure `required=True` and `allow_blank=False`; field validators do not run for omitted fields. Keep partial-update behavior intentional.
