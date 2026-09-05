# Testing and Verification Instructions

## Framework and Placement

Use pytest and pytest-django configured in `pyproject.toml` with `DJANGO_SETTINGS_MODULE = "core.settings"`. Discovery includes the eight domain apps and files named `tests.py`, `test_*.py`, or `*_tests.py`. Classes use `Test*`; functions use `test_*`.

Place tests in the affected app. When converting `tests.py` into a package, move existing tests deliberately instead of leaving an ambiguous module/package pair. Use `@pytest.mark.django_db` or database fixtures for database access and DRF APIClient for endpoint behavior.

## Coverage of Behavior

- Models: constraints, defaults, validation entry points, and deletion behavior.
- Serializers: invalid input, partial updates, protected fields, and relationship scope.
- APIs: success, anonymous/owner/other-user access, list visibility, missing resources, methods, and rendered JSON errors.
- Integrations: mock email, SMS, payment, translation, and Firebase at the application boundary; avoid live requests and charges.
- Performance-sensitive changes: test query counts or result bounds for the actual regression risk.

For bug fixes, reproduce the failure in a regression test first when feasible. Avoid tests that merely mirror implementation details. Isolate Redis/cache when unrelated to the behavior under test; configure services intentionally for integration tests.

## Commands and Reporting

Run `uv run pytest <app>/tests.py` or the relevant test path during development, then `uv run pytest` for behavior changes. Run `uv run ruff check .` and `uv run ruff format --check .` for Python changes. Use `uv run python manage.py check` for Django wiring/configuration and [model migration checks](models.md) for schema changes.

No coverage percentage is configured. Test and type-check jobs in the code-quality workflow are currently commented out; successful CI does not establish that tests ran. Do not skip tests, weaken assertions, or suppress errors to get passing results. Report pre-existing failures separately with the command and cause.

For documentation-only changes, verify relative links, referenced files/commands, and `git diff --check`. Do not describe documentation checks as runtime verification.

## Example: Category Catalog API Tests

After implementing the illustrative serializer, view, and route from the other guides, add these tests to `article/tests.py`. They exercise database retrieval, the JSON renderer, and the read-only method contract:

```python
import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from article.models import ArticleCategory


@pytest.fixture
def api_client(settings):
    # Keep throttling's cache access local rather than requiring Redis.
    settings.CACHES = {
        "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}
    }
    return APIClient()


@pytest.mark.django_db
def test_category_catalog_detail_returns_rendered_data(api_client):
    category = ArticleCategory.objects.create(
        name_en="Research",
        name_ko="연구",
        description="Research articles",
        icon="",
    )
    url = reverse("article-category-catalog-detail", kwargs={"id": category.id})

    result = api_client.get(url, HTTP_ACCEPT="application/json")

    assert result.status_code == 200
    payload = result.json()
    assert payload["status"] == "success"
    assert payload["data"]["id"] == str(category.id)
    assert payload["data"]["description"] == "Research articles"


@pytest.mark.django_db
def test_category_catalog_rejects_creation(api_client):
    url = reverse("article-category-catalog-list")

    result = api_client.post(url, {"name": "Unexpected"}, format="json")

    assert result.status_code == 405
    assert result.json()["status"] == "failure"
    assert ArticleCategory.objects.count() == 0
```

The fixture uses an empty icon to avoid filesystem/image processing in retrieval tests; it does not demonstrate a valid image upload. Add separate upload validation tests when changing image behavior. These tests require the example endpoint to exist; they are not tests of the current category management route.

```bash
uv run pytest article/tests.py -k category_catalog
```
