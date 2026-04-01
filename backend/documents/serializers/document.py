#!/usr/bin/env python3
"""Serializers for Document model."""

from rest_framework import serializers
from ..models import Document, DocumentType
from employees.models import Employee


class DocumentSerializer(serializers.ModelSerializer):
    """Full serializer for Document."""
    
    document_type_detail = serializers.SerializerMethodField()
    employee_name = serializers.SerializerMethodField()
    uploaded_by_name = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = [
            'id',
            'employee',
            'employee_name',
            'document_type',
            'document_type_detail',
            'file_name',
            'file_format',
            'file_size',
            'file_path',
            'description',
            'expiration_date',
            'is_expired',
            'notes',
            'is_active',
            'uploaded_by',
            'uploaded_by_name',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'employee_name', 'document_type_detail', 
            'is_expired', 'uploaded_by_name', 'created_at', 'updated_at'
        ]
    
    def get_document_type_detail(self, obj):
        return {
            'id': obj.document_type.id,
            'name': obj.document_type.name,
        }
    
    def get_employee_name(self, obj):
        return obj.employee.full_name
    
    def get_uploaded_by_name(self, obj):
        return obj.uploaded_by.full_name if obj.uploaded_by else None
    
    def get_is_expired(self, obj):
        if not obj.expiration_date:
            return False
        from django.utils import timezone
        return obj.expiration_date < timezone.now().date()


class DocumentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for lists."""
    
    document_type_name = serializers.CharField(source='document_type.name', read_only=True)
    employee_name = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = [
            'id',
            'employee',
            'employee_name',
            'document_type',
            'document_type_name',
            'file_name',
            'file_format',
            'expiration_date',
            'is_expired',
            'is_active',
            'created_at',
        ]
    
    def get_employee_name(self, obj):
        return obj.employee.full_name
    
    def get_is_expired(self, obj):
        if not obj.expiration_date:
            return False
        from django.utils import timezone
        return obj.expiration_date < timezone.now().date()


class DocumentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating documents."""
    
    class Meta:
        model = Document
        fields = [
            'employee',
            'document_type',
            'file_name',
            'file_format',
            'file_size',
            'file_path',
            'description',
            'expiration_date',
            'notes',
        ]
        extra_kwargs = {
            'file_path': {'required': False, 'allow_null': True},
        }
    
    def validate_document_type(self, value):
        """Ensure document type is active."""
        if not value.is_active:
            raise serializers.ValidationError('Cannot use an inactive document type.')
        return value
    
    def validate_file_format(self, value):
        """Normalize file format to lowercase."""
        return value.lower()
    
    def create(self, validated_data):
        """Set uploaded_by to current user."""
        request = self.context.get('request')
        if request and request.user:
            validated_data['uploaded_by'] = request.user
        return super().create(validated_data)


class DocumentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating documents."""
    
    class Meta:
        model = Document
        fields = [
            'document_type',
            'file_name',
            'file_format',
            'file_size',
            'file_path',
            'description',
            'expiration_date',
            'notes',
            'is_active',
        ]
    
    def validate_document_type(self, value):
        """Ensure document type is active."""
        if not value.is_active:
            raise serializers.ValidationError('Cannot use an inactive document type.')
        return value
    
    def validate_file_format(self, value):
        """Normalize file format to lowercase."""
        return value.lower() if value else value


class EmployeeDocumentListSerializer(serializers.ModelSerializer):
    """Serializer for employee viewing their own documents."""
    
    document_type_name = serializers.CharField(source='document_type.name', read_only=True)
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = [
            'id',
            'document_type',
            'document_type_name',
            'file_name',
            'file_format',
            'file_size',
            'file_path',
            'description',
            'expiration_date',
            'is_expired',
            'created_at',
        ]
    
    def get_is_expired(self, obj):
        if not obj.expiration_date:
            return False
        from django.utils import timezone
        return obj.expiration_date < timezone.now().date()
