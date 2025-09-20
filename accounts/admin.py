from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, DeveloperProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'is_developer', 'is_active', 'date_joined')
    list_filter = ('is_developer', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('is_developer', 'avatar', 'bio')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': ('is_developer', 'email')
        }),
    )


@admin.register(DeveloperProfile)
class DeveloperProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_name', 'verified', 'created_at')
    list_filter = ('verified', 'created_at')
    search_fields = ('user__username', 'display_name', 'website')
    readonly_fields = ('created_at', 'updated_at')
