#!/usr/bin/env python3
"""Tests for the employees app."""

from .base import BaseTestCase
from .test_authentication import AuthenticationTests
from .test_employee_me import EmployeeMeViewTests, EmployeePasswordChangeTests
from .test_employee_admin import (
    AdminEmployeeListTests,
    AdminEmployeeCreateTests,
    AdminEmployeeDetailTests,
    AdminEmployeeUpdateTests,
    AdminEmployeeDeleteTests,
    AdminEmployeeActivateTests,
    AdminSetPasswordTests,
)
from .test_job_title import (
    JobTitleListTests,
    JobTitleCreateTests,
    JobTitleDetailTests,
)
from .test_models import (
    EmployeeModelTests,
    JobTitleModelTests,
)
