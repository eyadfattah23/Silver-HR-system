#!/usr/bin/env python3
"""Tests for the core app (City, Branch, Department)."""

from .base import BaseTestCase
from .test_city import (
    CityListTests,
    CityCreateTests,
    CityDetailTests,
    CityModelTests,
)
from .test_branch import (
    BranchListTests,
    BranchCreateTests,
    BranchDetailTests,
    BranchModelTests,
)
from .test_department import (
    DepartmentListTests,
    DepartmentCreateTests,
    DepartmentDetailTests,
    DepartmentModelTests,
)
