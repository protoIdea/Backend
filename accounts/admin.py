from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile


class UserProfileInline(admin.StackedInline):
    """Inline admin for UserProfile"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class UserAdmin(BaseUserAdmin):
    """Custom User admin"""
    inlines = (UserProfileInline,)

    list_display = (
        'username', 'email', 'first_name', 'last_name', 'is_staff',
        'is_active', 'is_premium', 'currency', 'monthly_income',
        'date_joined', 'last_login'
    )
    list_filter = (
        'is_staff', 'is_superuser', 'is_active', 'is_premium',
        'currency', 'date_joined', 'last_login'
    )
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {
            'fields': (
                'first_name', 'last_name', 'email', 'phone_number',
                'date_of_birth', 'profile_picture'
            )
        }),
        (_('Budget preferences'), {
            'fields': ('currency', 'monthly_income')
        }),
        (_('Account settings'), {
            'fields': (
                'is_premium', 'email_notifications', 'push_notifications'
            )
        }),
        (_('Permissions'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            ),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'password1', 'password2',
                'first_name', 'last_name', 'currency', 'monthly_income'
            ),
        }),
    )

    def get_inline_instances(self, request, obj=None):
        """Only show inline if editing existing user"""
        if not obj:
            return []
        return super().get_inline_instances(request, obj)


class UserProfileAdmin(admin.ModelAdmin):
    """Admin for UserProfile"""
    list_display = (
        'user', 'location', 'savings_goal', 'emergency_fund_goal',
        'default_budget_period', 'email_frequency'
    )
    list_filter = ('default_budget_period', 'email_frequency')
    search_fields = ('user__username', 'user__email', 'location')
    ordering = ('user__username',)

    fieldsets = (
        (None, {'fields': ('user',)}),
        (_('Personal information'), {
            'fields': ('bio', 'location', 'website')
        }),
        (_('Financial goals'), {
            'fields': ('savings_goal', 'emergency_fund_goal')
        }),
        (_('Preferences'), {
            'fields': ('default_budget_period', 'email_frequency')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


# Register models
admin.site.register(User, UserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)

