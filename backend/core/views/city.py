#!/usr/bin/env python3
"""
Views for City management.

Permission Structure:
- Users with core.view: Can view cities
- Users with core.manage: Can create, update, delete cities
- Superusers: Full access
"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from permissions.utils import has_permission

from ..models import City
from ..serializers import (
    CitySerializer,
    CityListSerializer,
    CityCreateUpdateSerializer,
)


class HasCorePermission(permissions.BasePermission):
    """
    Permission class for core endpoints (cities, branches, departments).
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        # Safe methods require view permission
        if request.method in permissions.SAFE_METHODS:
            return has_permission(request.user, 'core.view')
        
        # Unsafe methods require manage permission
        return has_permission(request.user, 'core.manage')


class CityListCreateView(generics.ListCreateAPIView):
    """
    View for listing and creating cities.

    GET: List all cities (requires core.view)
    POST: Create a new city (requires core.manage)
    """
    queryset = City.objects.all().order_by('name')
    permission_classes = [HasCorePermission]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CityCreateUpdateSerializer
        return CityListSerializer


class CityDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for managing individual cities.

    GET: Retrieve city details (requires core.view)
    PUT/PATCH: Update city data (requires core.manage)
    DELETE: Deactivate city (requires core.manage)
    """
    queryset = City.objects.all()
    permission_classes = [HasCorePermission]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return CityCreateUpdateSerializer
        return CitySerializer

    def destroy(self, request, *args, **kwargs):
        """Soft delete: set is_active to False instead of deleting."""
        city = self.get_object()
        city.is_active = False
        city.save()
        return Response(
            {'detail': 'City deactivated successfully.'},
            status=status.HTTP_200_OK
        )


class ActiveCityListView(generics.ListAPIView):
    """
    View for listing active cities.

    GET: List only active cities (requires core.view)
    """
    queryset = City.objects.filter(is_active=True).order_by('name')
    permission_classes = [HasCorePermission]
    serializer_class = CityListSerializer
