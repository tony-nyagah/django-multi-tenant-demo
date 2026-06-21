"""API views — isolation is automatic because the DB connection
is already scoped to the current tenant's schema by django-tenants
middleware.  These views only see the tenant's own documents."""

from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Document
from .serializers import DocumentSerializer


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Only the creator can edit/delete."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.created_by == request.user


class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        # The connection is already scoped to the current tenant's schema,
        # so this only returns documents belonging to that tenant.
        qs = Document.objects.select_related("created_by").all()

        # Optional filtering
        status = self.request.query_params.get("status")
        if status:
            qs = qs.filter(status=status)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        """GET /api/documents/stats/ — summary counts per status."""
        qs = self.get_queryset()
        return Response({
            "total": qs.count(),
            "draft": qs.filter(status="draft").count(),
            "review": qs.filter(status="review").count(),
            "published": qs.filter(status="published").count(),
            "archived": qs.filter(status="archived").count(),
        })
