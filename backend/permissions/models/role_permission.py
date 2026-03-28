#!/usr/bin/python3
"""RolePermission model for linking Roles to Permissions."""
import uuid

from django.db import models


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
