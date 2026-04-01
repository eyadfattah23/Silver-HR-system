#!/usr/bin/env python3
"""Serializers for DocumentType model."""

from rest_framework import serializers
from ..models import DocumentType


class DocumentTypeSerializer(serializers.ModelSerializer):
    """Full serializer for DocumentType."""
    
    document_count = serializers.SerializerMethodField()
    
    class Meta:
        model = DocumentType
        fields = [
            'id',
            'name',
            'description',
            'is_active',
            'document_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'document_count', 'created_at', 'updated_at']
    
    def get_document_count(self, obj):
        """Return count of documents using this type."""
        return obj.documents.filter(is_active=True).count()


class DocumentTypeListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for lists."""
    
    document_count = serializers.SerializerMethodField()
    
    class Meta:
        model = DocumentType
        fields = ['id', 'name', 'is_active', 'document_count']
    
    def get_document_count(self, obj):
        return obj.documents.filter(is_active=True).count()


class DocumentTypeCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating DocumentType."""
    
    class Meta:
        model = DocumentType
        fields = ['name', 'description', 'is_active']
    
    def validate_name(self, value):
        """Ensure name is unique (case-insensitive)."""
        qs = DocumentType.objects.filter(name__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('Document type with this name already exists.')
        return value
