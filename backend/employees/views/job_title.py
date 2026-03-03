#!/usr/bin/env python3
"""Views for JobTitle management (Admin only)."""

from rest_framework import generics, permissions

from ..models import JobTitle
from ..serializers import (
    JobTitleSerializer,
    JobTitleListSerializer,
    JobTitleCreateUpdateSerializer,
)


class JobTitleListCreateView(generics.ListCreateAPIView):
    """
    Admin-only view for listing and creating job titles.

    GET: List all job titles
    POST: Create a new job title
    """
    queryset = JobTitle.objects.all().order_by('name')
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return JobTitleCreateUpdateSerializer
        return JobTitleListSerializer


class JobTitleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Admin-only view for managing individual job titles.

    GET: Retrieve job title details
    PUT/PATCH: Update job title
    DELETE: Delete job title
    """
    queryset = JobTitle.objects.all()
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return JobTitleCreateUpdateSerializer
        return JobTitleSerializer


class ActiveJobTitleListView(generics.ListAPIView):
    """
    View for listing only active job titles (for dropdown selections).
    Available to all authenticated users.
    """
    queryset = JobTitle.objects.filter(is_active=True).order_by('name')
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = JobTitleListSerializer
