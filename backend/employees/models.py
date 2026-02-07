#!/usr/bin/env python3
"""
Custom User model (employee) and manager using phone number as primary login field.
Supports global phone numbers via `phonenumbers`.
"""
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from cloudinary.models import CloudinaryField
from django.db import models
import phonenumbers
import uuid
import re
from datetime import date


def validate_egyptian_phone_number(value):
    """Validate that the phone number is a valid Egyptian phone number with +20 country code."""
    if not value:
        return
    
    # Egyptian phone numbers should start with +20
    if not value.startswith('+20'):
        raise ValidationError(
            'Phone number must be an Egyptian number starting with +20 country code.'
        )
    
    try:
        parsed_number = phonenumbers.parse(value, None)
        if not phonenumbers.is_valid_number(parsed_number):
            raise ValidationError('Invalid phone number format.')
        if parsed_number.country_code != 20:
            raise ValidationError('Phone number must be an Egyptian number (+20).')
    except phonenumbers.NumberParseException:
        raise ValidationError('Invalid phone number format.')


def validate_egyptian_national_id(value):
    """Validate Egyptian National ID format (14 digits with valid structure)."""
    if not value:
        return
    
    # Egyptian NID is exactly 14 digits
    if not re.match(r'^\d{14}$', value):
        raise ValidationError(
            'Egyptian National ID must be exactly 14 digits.'
        )
    
    # First digit must be 2 (1900s) or 3 (2000s)
    century_digit = value[0]
    if century_digit not in ('2', '3'):
        raise ValidationError(
            'Invalid Egyptian National ID: first digit must be 2 or 3.'
        )
    
    # Validate birth date components
    year = int(value[1:3])
    month = int(value[3:5])
    day = int(value[5:7])
    
    if month < 1 or month > 12:
        raise ValidationError('Invalid Egyptian National ID: invalid month.')
    
    if day < 1 or day > 31:
        raise ValidationError('Invalid Egyptian National ID: invalid day.')
    
    # Try to create a valid date
    full_year = 1900 + year if century_digit == '2' else 2000 + year
    try:
        date(full_year, month, day)
    except ValueError:
        raise ValidationError('Invalid Egyptian National ID: invalid birth date.')


def extract_dob_from_nid(nid):
    """Extract date of birth from Egyptian National ID."""
    if not nid or len(nid) != 14:
        return None
    
    century_digit = nid[0]
    if century_digit not in ('2', '3'):
        return None
    
    year = int(nid[1:3])
    month = int(nid[3:5])
    day = int(nid[5:7])
    
    full_year = 1900 + year if century_digit == '2' else 2000 + year
    
    try:
        return date(full_year, month, day)
    except ValueError:
        return None


def extract_gender_from_nid(nid):
    """Extract gender from Egyptian National ID (13th digit: odd = male, even = female)."""
    if not nid or len(nid) != 14:
        return None
    
    gender_digit = int(nid[12])  # 13th digit (0-indexed: 12)
    return 'male' if gender_digit % 2 == 1 else 'female'


class Employee(AbstractUser):
    """Custom User model that uses phone number as the primary login field.
    """
    # Remove username and email fields from AbstractUser
    username = None

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=30)
    rest_of_name = models.CharField(max_length=150)
    
    date_joined = models.DateTimeField(verbose_name="Date Joined")
    dob = models.DateField(verbose_name="Date of Birth", null=True, blank=True)
    # Add phone number fields
    phone_number1 = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Primary Phone Number",
        validators=[validate_egyptian_phone_number]
    )
    phone_number2 = models.CharField(max_length=20, blank=True, null=True, verbose_name="Secondary Phone Number")

    
    is_verified = models.BooleanField(default=False, verbose_name="Is Verified")
    
    identity_type = models.CharField(
        max_length=20,
        choices=[("nid", "National ID"),
                 ("passport", "Passport"),
                 ("driving_license", "Driving License"),
                 ("other", "Other")],
        default="nid",
    )
    identity_number = models.CharField(("Government ID, Passport, etc..."), max_length=20, unique=True)
    # Additional fields
    
      
    gender = models.CharField(
        max_length=10,
        choices=[("male", "Male"), ("female", "Female")],
        blank=True,
        null=True
    )
    address = models.TextField(null=True, blank=True)
     # front end can split it into multiple fields if needed, front end only validates it, backend just stores it as text
    location = models.URLField(max_length=512, null=True, blank=True)
    
    role = models.CharField(max_length=50, blank=True, null=True) ## later
    profile_picture = CloudinaryField('profile_pictures', blank=True, null=True)
    fingerprint_id = models.CharField(max_length=50, blank=True, null=True) 
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = 'phone_number1'
    REQUIRED_FIELDS = ['first_name', 'rest_of_name', 'date_joined', 'identity_type', 'identity_number', 'gender']  # No additional required fields

    def clean(self):
        """Validate identity_number and extract dob/gender from Egyptian NID if applicable."""
        super().clean()
        
        # Validate Egyptian National ID format if identity_type is 'nid'
        if self.identity_type == 'nid':
            validate_egyptian_national_id(self.identity_number)
            
            # Extract date of birth from NID if not provided
            if not self.dob:
                extracted_dob = extract_dob_from_nid(self.identity_number)
                if extracted_dob:
                    self.dob = extracted_dob
            
            # Extract gender from NID if not provided
            if not self.gender:
                extracted_gender = extract_gender_from_nid(self.identity_number)
                if extracted_gender:
                    self.gender = extracted_gender

    def save(self, *args, **kwargs):
        """Override save to ensure clean() is called and data is extracted."""
        # Extract data from NID before saving if identity_type is 'nid'
        if self.identity_type == 'nid' and self.identity_number:
            if not self.dob:
                extracted_dob = extract_dob_from_nid(self.identity_number)
                if extracted_dob:
                    self.dob = extracted_dob
            
            if not self.gender:
                extracted_gender = extract_gender_from_nid(self.identity_number)
                if extracted_gender:
                    self.gender = extracted_gender
        
        self.full_clean()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.first_name} {self.rest_of_name} ({self.phone_number1})"
