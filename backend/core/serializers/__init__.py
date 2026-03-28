#!/usr/bin/env python3
"""Serializers for the core app (City, Branch, Department)."""

from .city import CitySerializer, CityListSerializer, CityCreateUpdateSerializer
from .branch import BranchSerializer, BranchListSerializer, BranchCreateUpdateSerializer
from .department import DepartmentSerializer, DepartmentListSerializer, DepartmentCreateUpdateSerializer
