#!/usr/bin/env python3
"""Serializers for Employee and JobTitle models."""

from .employee import (
    EmployeeSerializer,
    EmployeeListSerializer,
    EmployeeCreateSerializer,
    EmployeeAdminUpdateSerializer,
)
from .job_title import (
    JobTitleSerializer,
    JobTitleListSerializer,
    JobTitleCreateUpdateSerializer,
)
