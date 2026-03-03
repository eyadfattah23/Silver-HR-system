#!/usr/bin/env python3
"""Branch admin configuration for the Silver HR application."""
from django.contrib import admin

from ..models import Branch

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    """Admin configuration for the Branch model."""
    list_display = ('name', 'city', 'is_active')
    list_filter = ('city', 'is_active')
    search_fields = ('name', 'city__name')
    readonly_fields = ('created_at', 'updated_at')
    list_select_related =  ('city',)
    ordering = ('name',)
    fieldsets = (
        (None, {
            'fields': ('name', 'city', 'is_active', 'description', 'location')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
