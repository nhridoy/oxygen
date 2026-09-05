from rest_framework import permissions, viewsets

from core.permissions import IsAdminOrReadOnly
from support.models import Notice
from support.serializers import NoticeSerializer


class NoticeViewSet(viewsets.ModelViewSet):
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer
    permission_classes = (
        IsAdminOrReadOnly,
        permissions.IsAuthenticated,
    )
    lookup_field = "id"
    # http_method_names = ["get"]
