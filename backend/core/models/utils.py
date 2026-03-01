#!/usr/bin/env python3
"""Utilities models for the Silver HR application. (City, Branch, Department)"""
from django.db import models
from django.utils.translation import gettext_lazy as _

class Weekday(models.IntegerChoices):
    """Enumeration for weekday choices."""
    SATURDAY = 0, _('Saturday')
    SUNDAY = 1, _('Sunday')
    MONDAY = 2, _('Monday')
    TUESDAY = 3, _('Tuesday')
    WEDNESDAY = 4, _('Wednesday')
    THURSDAY = 5, _('Thursday')
    FRIDAY = 6, _('Friday')
