# API Contract and Routing Instructions

## Define the Contract

Identify the resource, methods, authentication/authorization policy, request fields, response fields, status codes, and pagination/filter behavior before implementation. Inspect neighboring endpoints and consumers. Explain breaking changes rather than silently renaming fields or changing response shapes.

Read [models](models.md), [serializers](serializers.md), [views](views.md), and [testing](testing.md) whenever the endpoint affects those layers.

## Register Routes

Place routes in `<app>/urls.py`; use routers for ViewSets and `path()` for individual views. Supply meaningful route names/basenames. Follow trailing-slash conventions and use lookup types matching the resource, such as UUID IDs or article slugs.

Register new app prefixes in [core/urls.py](../../core/urls.py). Existing prefixes include `api/auth/`, `api/articles/`, `api/forum/`, `api/options/`, `api/support/`, and `api/settings/`. An app's existence does not make its URLs reachable. Check static routes against dynamic lookup routes for collisions.

## Shared Response Behavior

Read `core/settings/drf_settings.py`, `core/renderers.py`, and `core/pagination.py`. The custom JSON renderer produces `message`, `errors`, `status`, `status_code`, `links`, `count`, `total_pages`, and `data`. Let it construct the envelope; do not duplicate the envelope inside views.

The current renderer uses mapping operations. Test the selected payload, especially custom responses and unpaginated lists, instead of assuming standard DRF rendering works unchanged. Preserve pagination contracts and enforce bounds for new collection endpoints.

Use appropriate HTTP status codes and keep new GET endpoints read-only. Inspect authentication and throttle settings before adding sensitive operations; avoid changing global defaults for one endpoint.

## Schema and Verification

Use drf-spectacular annotations when introspection cannot describe custom actions or serializer selection. Debug mode exposes Swagger at `/api/`, schema at `/api/schema/`, and ReDoc at `/api/schema/redoc/`.

For schema changes, run `uv run python manage.py spectacular --file /tmp/oxygen-schema.yml --validate` and inspect affected paths and warnings. Test routing, methods, access boundaries, invalid inputs, pagination, and rendered success/error responses.

For WebSockets, also inspect `chat/routing.py`, its consumers, and `core/asgi.py`; HTTP URL registration alone is insufficient.

## Example: Register and Request the Category Catalog

These examples illustrate a new read-only catalog; they do not describe an endpoint already implemented. After adding the serializer and view examples, extend the existing `article/urls.py` router:

```python
from article.views import ArticleCategoryCatalogViewSet

# Register on the existing router before its empty-prefix ArticleView entry.
router.register(
    "category-catalog",
    ArticleCategoryCatalogViewSet,
    basename="article-category-catalog",
)
```

Keep existing imports, routes, and `urlpatterns += router.urls`. `core/urls.py` already mounts the article app at `/api/articles/`, so no second include is needed.

```bash
curl -H 'Accept: application/json' \
  'http://127.0.0.1:8000/api/articles/category-catalog/?size=20'
```

For an empty database, the paginated JSON response is:

```json
{
  "message": "",
  "errors": null,
  "status": "success",
  "status_code": 200,
  "links": {"next": null, "previous": null},
  "count": 0,
  "total_pages": 1,
  "data": []
}
```

The detail route is `/api/articles/category-catalog/<id>/`; its reverse name is `article-category-catalog-detail`. The list reverse name is `article-category-catalog-list`. POST, PUT, PATCH, and DELETE are unavailable because the view is read-only. Test these contracts using the examples in [Testing](testing.md).
