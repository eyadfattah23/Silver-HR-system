#!/usr/bin/env python3
"""Views for employees app."""

from .employee import (
    EmployeeMeView,
    EmployeeListCreateView,
    EmployeeDetailView,
    EmployeeActivateView,
    EmployeeSetPasswordView,
)
from .job_title import (
    JobTitleListCreateView,
    JobTitleDetailView,
    ActiveJobTitleListView,
)
