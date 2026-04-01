from django.contrib import admin
from .models import (
    Permission,
    Role,
    RolePermission,
    EmployeeRole,
    EmployeeExtraPermission,
    DelegationRight,
    PermissionDelegation,
)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'name', 'resource', 'action', 'is_active']
    list_filter = ['resource', 'action', 'is_active']
    search_fields = ['code', 'name']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_system_role', 'is_active', 'created_at']
    list_filter = ['is_system_role', 'is_active']
    search_fields = ['name']


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'role', 'permission']
    list_filter = ['role']
    search_fields = ['role__name', 'permission__name']


@admin.register(EmployeeRole)
class EmployeeRoleAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee', 'role', 'granted_at', 'revoked_at']
    list_filter = ['role', 'revoked_at']
    search_fields = ['employee__first_name', 'employee__fourth_name', 'role__name']
    raw_id_fields = ['employee', 'granted_by', 'revoked_by']


@admin.register(EmployeeExtraPermission)
class EmployeeExtraPermissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee', 'permission', 'granted_at', 'expires_at']
    list_filter = ['permission']
    search_fields = ['employee__first_name', 'permission__name']
    raw_id_fields = ['employee', 'granted_by']


@admin.register(DelegationRight)
class DelegationRightAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee', 'can_delegate_permission', 'is_active', 'granted_at']
    list_filter = ['is_active']
    search_fields = ['employee__first_name', 'can_delegate_permission__name']
    raw_id_fields = ['employee', 'granted_by']


@admin.register(PermissionDelegation)
class PermissionDelegationAdmin(admin.ModelAdmin):
    list_display = ['id', 'delegator', 'delegate', 'permission', 'is_active', 'expires_at']
    list_filter = ['is_active']
    search_fields = ['delegator__first_name', 'delegate__first_name', 'permission__name']
    raw_id_fields = ['delegator', 'delegate']
