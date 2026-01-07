from django.contrib import admin
from .models import User, Role, Permission, RolePermission, UserRole, AccessToken


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('email', 'first_name', 'last_name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('resource_type', 'action', 'description', 'created_at')
    list_filter = ('resource_type', 'action')
    search_fields = ('resource_type', 'action', 'description')


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ('role', 'permission', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('role__name', 'permission__resource_type', 'permission__action')


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'assigned_at')
    list_filter = ('role', 'assigned_at')
    search_fields = ('user__email', 'role__name')


@admin.register(AccessToken)
class AccessTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token_short', 'expires_at', 'last_used_at', 'created_at')
    list_filter = ('expires_at', 'created_at')
    search_fields = ('user__email', 'token')
    readonly_fields = ('token', 'created_at', 'last_used_at')
    
    def token_short(self, obj):
        return f"{obj.token[:20]}..." if obj.token else "-"
    token_short.short_description = 'Токен'
