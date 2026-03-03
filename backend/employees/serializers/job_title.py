#!/usr/bin/env python3
"""Serializers for JobTitle model."""
from rest_framework import serializers
from ..models import JobTitle


class JobTitleSerializer(serializers.ModelSerializer):
    """Full serializer for JobTitle model."""

    class Meta:
        model = JobTitle
        fields = (
            'id',
            'name',
            'description',
            'is_active',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class JobTitleListSerializer(serializers.ModelSerializer):
    """Compact serializer for JobTitle list view."""

    class Meta:
        model = JobTitle
        fields = ('id', 'name', 'is_active')
        read_only_fields = fields


class JobTitleCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating JobTitle."""

    class Meta:
        model = JobTitle
        fields = ('id', 'name', 'description', 'is_active')
        read_only_fields = ('id',)
