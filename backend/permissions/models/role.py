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
    
    hierarchy_level = models.PositiveIntegerField(default=5)  # 1=highest (super_admin), 5=lowest (employee)
    is_system_role = models.BooleanField(default=False)  # True for roles like super_admin that cannot be deleted
    
    class Meta:
        ordering = ['hierarchy_level', 'name']
        indexes = [
            models.Index(fields=['hierarchy_level']),
        ]
    
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
