# View and Queryset Instructions

## Choose and Connect the View

Inspect nearby views, URLs, and serializers. Use `<app>/views/<domain>_views.py` and package exports where established. Prefer DRF generic views for standard operations, ViewSets for resource actions, and APIView for custom workflows. Expose only required methods/actions.

Set `serializer_class` or implement `get_serializer_class()` for list/detail/write contracts. Align `lookup_field` with URL parameters. Follow [API routing instructions](apis.md) when registering the view.

## Permissions and Querysets

Declare the intended permission policy explicitly. Read [core/permissions.py](../../core/permissions.py); names do not fully describe behavior. `IsAdminOrReadOnly` allows safe methods and requires a superuser for writes, not merely `is_staff`.

Scope `get_queryset()` to visible objects: object permissions do not filter lists. Use generic `get_object()` or call `check_object_permissions()` after custom retrieval. Protect creation separately because there is no existing object to check. Handle anonymous users before ownership filters.

Use `select_related()` for single-valued relations and `prefetch_related()` for collections read by serializers. Whitelist filtering, search, and ordering fields and maintain deterministic pagination ordering. Avoid per-object queries and unbounded nested replies.

## Writes and Responses

Validate inputs through serializers. Assign trusted fields in `perform_create()`/`perform_update()` where appropriate, for example `serializer.save(user=self.request.user)`. Use transactions for dependent writes and concurrency-safe database operations for shared counters. Keep external integrations in the appropriate service layer and handle failures explicitly.

Use DRF exceptions and status constants. GET must not mutate state in new APIs; legacy toggle views are not a safe template. A 204 response should have no body. Coordinate existing contract changes through [the API guide](apis.md).

## Verification

Follow [testing instructions](testing.md). Cover anonymous, owner, other-user, and privileged access where relevant, plus missing objects, forbidden writes, methods, and validation errors. Test list visibility separately from detail permissions. Render JSON responses to detect incompatibility with the custom renderer.

## Example: Public Read-Only Category Catalog

This illustrative view belongs in `article/views/article_views.py` and uses the serializer from [the serializer example](serializers.md). It offers public list/detail access without exposing writes:

```python
from rest_framework import permissions, viewsets

from article.models import ArticleCategory
from article.serializers import ArticleCategoryCatalogSerializer


class ArticleCategoryCatalogViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.AllowAny,)
    serializer_class = ArticleCategoryCatalogSerializer
    queryset = ArticleCategory.objects.order_by("-created_at", "id")
    lookup_field = "id"
    filterset_fields = ("name",)
    search_fields = ("name", "description")
    ordering_fields = ("created_at", "id")
    ordering = ("-created_at", "id")
```

Export the class from `article/views/__init__.py`. The UUID tie-breaker makes default ordering deterministic. No related-object loading is needed because this serializer reads only category fields. Shared pagination and rendering remain active.

This is an additional catalog example, not a replacement for the existing category management ViewSet. For a protected resource, replace `AllowAny` with the intended permission policy and scope the queryset; copying public access would be inappropriate.
