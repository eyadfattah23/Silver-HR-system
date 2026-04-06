#!/usr/bin/python3
"""Role model for the Silver HR application."""
import uuid

from django.db import models


class Role(models.Model):
    """Model representing a role that can be assigned to employees."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    
    # ManyToMany relationship to Permission through RolePermission
    permissions = models.ManyToManyField(
        'permissions.Permission',
        through='permissions.RolePermission',
        related_name='roles',
        blank=True
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    is_system_role = models.BooleanField(default=False)  # True for roles like super_admin that cannot be deleted
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_active_permissions(self):
        """Return all active permissions for this role."""
        return self.permissions.filter(
            role_permissions__is_active=True,
            is_active=True
        )
    
    def has_permission(self, permission_code):
        """Check if this role has a specific permission."""
        return self.get_active_permissions().filter(code=permission_code).exists()
    
    def has_resource_action(self, resource, action):
        """Check if this role has permission for a specific resource and action."""
        return self.get_active_permissions().filter(
            resource=resource,
            action=action
        ).exists()
        
        

class RolePermission(models.Model):
    """
    Through model for Role-Permission many-to-many relationship.
    Defines which permissions are granted to each role by default.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.ForeignKey(
        'permissions.Role',
        on_delete=models.CASCADE,
        related_name='role_permissions'
    )
    permission = models.ForeignKey(
        'permissions.Permission',
        on_delete=models.CASCADE,
        related_name='role_permissions'
    )
    
    # Metadata
    is_active = models.BooleanField(default=True)  # Can disable permission for a role without deleting
    granted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('role', 'permission')
        verbose_name = 'Role Permission'
        verbose_name_plural = 'Role Permissions'
        indexes = [
            models.Index(fields=['role', 'permission']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.role.name} -> {self.permission.code}"


class EmployeeRole(models.Model):
    """
    Assigns roles to employees with optional scope (city/branch/department).
    If scope limiters are null, the role applies globally.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='employee_roles'
    )
    role = models.ForeignKey(
        'permissions.Role',
        on_delete=models.CASCADE,
        related_name='employee_roles'
    )
    
    # Scope limiters (null means no restriction at that level)
    city = models.ForeignKey(
        'core.City',
        on_delete=models.CASCADE,
        related_name='employee_roles',
        null=True,
        blank=True,
        help_text='If set, role applies only to this city'
    )
    branch = models.ForeignKey(
        'core.Branch',
        on_delete=models.CASCADE,
        related_name='employee_roles',
        null=True,
        blank=True,
        help_text='If set, role applies only to this branch'
    )
    department = models.ForeignKey(
        'core.Department',
        on_delete=models.CASCADE,
        related_name='employee_roles',
        null=True,
        blank=True,
        help_text='If set, role applies only to this department'
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Audit fields
    granted_by = models.ForeignKey(
        'employees.Employee',
        on_delete=models.PROTECT,
        related_name='roles_granted'
    )
    granted_at = models.DateTimeField(auto_now_add=True)
    
    revoked_by = models.ForeignKey(
        'employees.Employee',
        on_delete=models.SET_NULL,
        related_name='roles_revoked',
        null=True,
        blank=True
    )
    revoked_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Employee Role'
        verbose_name_plural = 'Employee Roles'
        unique_together = ('employee', 'role', 'city', 'branch', 'department')
        indexes = [
            models.Index(fields=['employee']),
            models.Index(fields=['role']),
            models.Index(fields=['is_active']),
            models.Index(fields=['employee', 'is_active']),
        ]
    
    def __str__(self):
        scope = self._get_scope_description()
        return f"{self.employee} - {self.role.name}{scope}"
    
    def _get_scope_description(self):
        """Return human-readable scope description."""
        if self.department:
            return f" (Department: {self.department.name})"
        if self.branch:
            return f" (Branch: {self.branch.name})"
        if self.city:
            return f" (City: {self.city.name})"
        return " (Global)"
    
    def revoke(self, revoked_by):
        """Revoke this role assignment."""
        from django.utils import timezone
        self.is_active = False
        self.revoked_by = revoked_by
        self.revoked_at = timezone.now()
        self.save()
    
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
        Check if this role assignment applies to the given scope.
        
        If no scope is provided (all None), returns True since we're just 
        checking if the user has the permission at any scope level.
        
        A global role applies everywhere.
        A city role applies to all branches/departments in that city.
        A branch role applies to all departments in that branch.
        A department role applies only to that department.
        """
        # If no scope was requested, we're just checking if user has permission at any level
        if city is None and branch is None and department is None:
            return True
        
        # Global role applies everywhere
        if not self.city and not self.branch and not self.department:
            return True
        
        # Department-scoped role
        if self.department:
            return department and self.department_id == department.id
        
        # Branch-scoped role
        if self.branch:
            if department:
                return department.branch_id == self.branch_id
            return branch and self.branch_id == branch.id
        
        # City-scoped role
        if self.city:
            if department:
                return department.branch.city_id == self.city_id
            if branch:
                return branch.city_id == self.city_id
            return city and self.city_id == city.id
        
        return False


class EmployeeExtraPermission(models.Model):
    """
    Extra permissions granted to specific employees beyond their role's permissions.
    Allows granting individual permissions with optional scope (city/branch/department).
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='extra_permissions'
    )
    permission = models.ForeignKey(
        'permissions.Permission',
        on_delete=models.CASCADE,
        related_name='employee_extra_permissions'
    )
    
    # Scope limiters (null means no restriction at that level)
    city = models.ForeignKey(
        'core.City',
        on_delete=models.CASCADE,
        related_name='employee_extra_permissions',
        null=True,
        blank=True,
        help_text='If set, permission applies only to this city'
    )
    branch = models.ForeignKey(
        'core.Branch',
        on_delete=models.CASCADE,
        related_name='employee_extra_permissions',
        null=True,
        blank=True,
        help_text='If set, permission applies only to this branch'
    )
    department = models.ForeignKey(
        'core.Department',
        on_delete=models.CASCADE,
        related_name='employee_extra_permissions',
        null=True,
        blank=True,
        help_text='If set, permission applies only to this department'
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Audit fields
    granted_by = models.ForeignKey(
        'employees.Employee',
        on_delete=models.PROTECT,
        related_name='extra_permissions_granted',
        help_text='Employee who granted this permission (could be super admin or another employee with give_own permission)'
    )
    granted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Employee Extra Permission'
        verbose_name_plural = 'Employee Extra Permissions'
        unique_together = ('employee', 'permission')  # Only one record per employee-permission pair
        indexes = [
            models.Index(fields=['employee']),
            models.Index(fields=['permission']),
            models.Index(fields=['is_active']),
            models.Index(fields=['employee', 'is_active']),
        ]
    
    def __str__(self):
        scope = self._get_scope_description()
        return f"{self.employee} + {self.permission.code}{scope}"
    
    def _get_scope_description(self):
        """Return human-readable scope description."""
        if self.department:
            return f" (Department: {self.department.name})"
        if self.branch:
            return f" (Branch: {self.branch.name})"
        if self.city:
            return f" (City: {self.city.name})"
        return " (Global)"
    
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
        Check if this extra permission applies to the given scope.
        Same logic as EmployeeRole.applies_to().
        
        If no scope is provided (all None), returns True since we're just 
        checking if the user has the permission at any scope level.
        """
        # If no scope was requested, we're just checking if user has permission at any level
        if city is None and branch is None and department is None:
            return True
        
        # Global permission applies everywhere
        if not self.city and not self.branch and not self.department:
            return True
        
        # Department-scoped permission
        if self.department:
            return department and self.department_id == department.id
        
        # Branch-scoped permission
        if self.branch:
            if department:
                return department.branch_id == self.branch_id
            return branch and self.branch_id == branch.id
        
        # City-scoped permission
        if self.city:
            if department:
                return department.branch.city_id == self.city_id
            if branch:
                return branch.city_id == self.city_id
            return city and self.city_id == city.id
        
        return False
