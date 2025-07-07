from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from simple_history.admin import SimpleHistoryAdmin
from unfold.admin import ModelAdmin
from .models import User, Address

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    search_fields = ('email',)
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    
    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_add_permission(self, request):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

@admin.register(Address)
class AddressAdmin(SimpleHistoryAdmin, ModelAdmin):
    list_display = ('user', 'name', 'phone', 'city', 'pin_code', 'address_type', 'is_default', 'created_at')
    list_filter = ('address_type', 'is_default', 'city', 'created_at')
    search_fields = ('user__email', 'name', 'phone', 'house', 'street', 'city', 'pin_code')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    fieldsets = (
        ('User Information', {'fields': ('user', 'name', 'phone')}),
        ('Address Details', {'fields': ('house', 'street', 'city', 'pin_code', 'address_type')}),
        ('Location', {'fields': ('latitude', 'longitude')}),
        ('Settings', {'fields': ('is_default',)}),
        ('Timestamps', {'fields': ('created_at',), 'classes': ('collapse',)}),
    )
    
    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name='Manager').exists()
    
    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.groups.filter(name='Manager').exists()
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name='Manager').exists()
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser