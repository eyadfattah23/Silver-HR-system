#!/usr/bin/env python3
"""
Views for City management.

Permission Structure:
- Only superusers can manage cities (CRUD)
"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from ..models import City
from ..serializers import (
    CitySerializer,
    CityListSerializer,
    CityCreateUpdateSerializer,
)


class IsSuperUser(permissions.BasePermission):
    """Permission class that only allows superusers."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_superuser


class CityListCreateView(generics.ListCreateAPIView):
    """
    Super admin-only view.

    GET: List all cities
    POST: Create a new city
    """
    queryset = City.objects.all().order_by('name')
    permission_classes = [IsSuperUser]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CityCreateUpdateSerializer
        return CityListSerializer


class CityDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Super admin-only view for managing individual cities.

    GET: Retrieve city details
    PUT/PATCH: Update city data
    DELETE: Deactivate city (soft delete by setting is_active=False)
    """
    queryset = City.objects.all()
    permission_classes = [IsSuperUser]

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
    Super admin-only view.

    GET: List only active cities
    """
    queryset = City.objects.filter(is_active=True).order_by('name')
    permission_classes = [IsSuperUser]
    serializer_class = CityListSerializer
