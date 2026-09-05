from rest_framework import viewsets

from core.permissions import IsAdminOrReadOnly
from site_settings.models import Page
from site_settings.serializers import PageSerializer


class PageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    lookup_field = "slug"
    permission_classes = [IsAdminOrReadOnly]
