from django.contrib import admin
from .models import Category, CategoryGroup


class CategoryAdmin(admin.ModelAdmin):
    """Admin for Category model"""
    list_display = (
        'name', 'user', 'category_type', 'budget_percentage',
        'is_default', 'is_active', 'created_at'
    )
    list_filter = (
        'category_type', 'is_default', 'is_active',
        'created_at', 'updated_at'
    )
    search_fields = ('name', 'description', 'user__username', 'user__email')
    ordering = ('user__username', 'name')
    list_editable = ('is_active', 'budget_percentage')

    fieldsets = (
        (None, {'fields': ('user', 'name', 'description')}),
        ('Appearance', {'fields': ('color', 'icon')}),
        ('Budget Settings', {
         'fields': ('category_type', 'budget_percentage')}),
        ('Status', {'fields': ('is_default', 'is_active')}),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        """Filter categories by user if not superuser"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)


class CategoryGroupAdmin(admin.ModelAdmin):
    """Admin for CategoryGroup model"""
    list_display = ('name', 'user', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'description', 'user__username')
    ordering = ('user__username', 'name')

    fieldsets = (
        (None, {'fields': ('user', 'name', 'description')}),
        ('Appearance', {'fields': ('color', 'icon')}),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        """Filter category groups by user if not superuser"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)


# Register models
admin.site.register(Category, CategoryAdmin)
admin.site.register(CategoryGroup, CategoryGroupAdmin)

