#!/usr/bin/env python3
"""City admin configuration for the Silver HR application."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from core.models.city import City
@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    """Admin configuration for the City model."""
    list_display = ('name', 'code', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')
    ordering = ('name',)
    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
