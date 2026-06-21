"""DRF serializers for the Document API."""

from rest_framework import serializers
from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source="created_by.username")

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "content",
            "status",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
