#!/usr/bin/env python3
"""Views for the core app (City, Branch, Department)."""

from .city import CityListCreateView, CityDetailView, ActiveCityListView
from .branch import BranchListCreateView, BranchDetailView, ActiveBranchListView
from .department import DepartmentListCreateView, DepartmentDetailView, ActiveDepartmentListView
