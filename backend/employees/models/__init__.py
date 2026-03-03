#!/usr/bin/env python3
"""Employee-related models for the Silver HR application. (Employee, JobTitle, etc.)"""
from .employee import (
    Employee,
    EmployeeManager,
    validate_egyptian_national_id,
    validate_egyptian_phone_number,
    extract_dob_from_nid,
    extract_gender_from_nid,
    Gender,
    MilitaryStatus,
    MaritalStatus,
    EmploymentType,
    EmploymentState,
)
from .job_title import JobTitle
