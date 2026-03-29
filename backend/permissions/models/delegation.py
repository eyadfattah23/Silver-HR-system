#!/usr/bin/python3
"""Permission delegation models for the Silver HR application."""
import uuid

from django.db import models


class DelegationRight(models.Model):
    """
    Controls which permissions an employee can delegate to others.
    An employee must have a DelegationRight for a permission to delegate it.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='delegation_rights'
    )
    can_delegate_permission = models.ForeignKey(
        'permissions.Permission',
        on_delete=models.CASCADE,
        related_name='delegation_rights',
        help_text='Which permission can this employee delegate?'
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Audit fields
    granted_by = models.ForeignKey(
        'employees.Employee',
        on_delete=models.PROTECT,
        related_name='delegation_rights_granted'
    )
    granted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Delegation Right'
        verbose_name_plural = 'Delegation Rights'
        unique_together = ('employee', 'can_delegate_permission')
        indexes = [
            models.Index(fields=['employee']),
            models.Index(fields=['can_delegate_permission']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.employee} can delegate {self.can_delegate_permission.code}"


class PermissionDelegation(models.Model):
    """
    Permission delegation - allows an employee to give their permission to another.
    Requires:
    - The delegator must have the permission (via role or extra permission)
    - The permission must be delegatable (Permission.is_delegatable=True)
    - The delegator must have DelegationRight for this permission
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    delegator = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='delegations_given',
        help_text='Employee giving the permission'
    )
    delegate = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='delegations_received',
        help_text='Employee receiving the permission'
    )
    permission = models.ForeignKey(
        'permissions.Permission',
        on_delete=models.CASCADE,
        related_name='delegations'
    )
    
    # Scope limiters (inherited from delegator or more restricted)
    city = models.ForeignKey(
        'core.City',
        on_delete=models.CASCADE,
        related_name='permission_delegations',
        null=True,
        blank=True,
        help_text='If set, delegation applies only to this city'
    )
    branch = models.ForeignKey(
        'core.Branch',
        on_delete=models.CASCADE,
        related_name='permission_delegations',
        null=True,
        blank=True,
        help_text='If set, delegation applies only to this branch'
    )
    department = models.ForeignKey(
        'core.Department',
        on_delete=models.CASCADE,
        related_name='permission_delegations',
        null=True,
        blank=True,
        help_text='If set, delegation applies only to this department'
    )
    
    # Reason and status
    reason = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    delegated_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Optional expiration for temporary delegation'
    )
    revoked_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Permission Delegation'
        verbose_name_plural = 'Permission Delegations'
        unique_together = ('delegator', 'delegate', 'permission')
        indexes = [
            models.Index(fields=['delegator']),
            models.Index(fields=['delegate']),
            models.Index(fields=['permission']),
            models.Index(fields=['is_active']),
            models.Index(fields=['delegate', 'is_active']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        scope = self._get_scope_description()
        return f"{self.delegator} -> {self.delegate}: {self.permission.code}{scope}"
    
    def _get_scope_description(self):
        """Return human-readable scope description."""
        if self.department:
            return f" (Department: {self.department.name})"
        if self.branch:
            return f" (Branch: {self.branch.name})"
        if self.city:
            return f" (City: {self.city.name})"
        return " (Global)"
    
    def revoke(self):
        """Revoke this delegation."""
        from django.utils import timezone
        self.is_active = False
        self.revoked_at = timezone.now()
        self.save()
    
    @property
    def is_expired(self):
        """Check if this delegation has expired."""
        if not self.expires_at:
            return False
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    @property
    def is_effective(self):
        """Check if this delegation is currently effective (active and not expired)."""
        return self.is_active and not self.is_expired
    
    @property
    def scope_level(self):
        """Return the scope level: 'global', 'city', 'branch', or 'department'."""
        if self.department:
            return 'department'
        if self.branch:
            return 'branch'
        if self.city:
            return 'city'
        return 'global'
    
    def applies_to(self, city=None, branch=None, department=None):
        """
        Check if this delegation applies to the given scope.
        Same logic as EmployeeRole.applies_to().
        """
        # Global delegation applies everywhere
        if not self.city and not self.branch and not self.department:
            return True
        
        # Department-scoped delegation
        if self.department:
            return department and self.department_id == department.id
        
        # Branch-scoped delegation
        if self.branch:
            if department:
                return department.branch_id == self.branch_id
            return branch and self.branch_id == branch.id
        
        # City-scoped delegation
        if self.city:
            if department:
                return department.branch.city_id == self.city_id
            if branch:
                return branch.city_id == self.city_id
            return city and self.city_id == city.id
        
        return False
    
    @classmethod
    def can_delegate(cls, delegator, permission, city=None, branch=None, department=None):
        """
        Check if an employee can delegate a specific permission.
        Requirements:
        1. The permission must be delegatable
        2. The delegator must have a DelegationRight for this permission
        3. The delegator must have the permission themselves
        """
        # Check if permission is delegatable
        if not permission.is_delegatable:
            return False
        
        # Check if delegator has delegation right for this permission
        has_delegation_right = DelegationRight.objects.filter(
            employee=delegator,
            can_delegate_permission=permission,
            is_active=True
        ).exists()
        
        if not has_delegation_right:
            return False
        
        # Check if delegator has the permission themselves
        return delegator.has_permission(
            permission.code,
            city=city,
            branch=branch,
            department=department
        )
