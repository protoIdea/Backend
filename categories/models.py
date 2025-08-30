from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class Category(models.Model):
    """Expense category model"""

    # Category types
    CATEGORY_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('transfer', 'Transfer'),
    ]

    # Default categories
    DEFAULT_CATEGORIES = [
        ('food', 'Food & Dining', '#d97706'),
        ('transport', 'Transportation', '#f97316'),
        ('entertainment', 'Entertainment', '#be123c'),
        ('utilities', 'Utilities', '#4b5563'),
        ('housing', 'Housing', '#059669'),
        ('healthcare', 'Healthcare', '#dc2626'),
        ('shopping', 'Shopping', '#7c3aed'),
        ('education', 'Education', '#0891b2'),
        ('travel', 'Travel', '#ea580c'),
        ('savings', 'Savings', '#16a34a'),
        ('income', 'Income', '#059669'),
        ('other', 'Other', '#6b7280'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(
        max_length=7, default='#3b82f6', help_text='Hex color code')
    icon = models.CharField(max_length=50, blank=True,
                            help_text='Icon name (e.g., lucide-react icon)')

    # Category type and budget allocation
    category_type = models.CharField(
        max_length=20, choices=CATEGORY_TYPES, default='expense')
    budget_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Percentage of total budget allocated to this category'
    )

    # User relationship
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='categories')
    is_default = models.BooleanField(
        default=False, help_text='Is this a default system category?')
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        unique_together = ['name', 'user']
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    def save(self, *args, **kwargs):
        """Override save to set default values"""
        if not self.pk and not self.color:
            # Set default color based on category name
            for default_name, _, default_color in self.DEFAULT_CATEGORIES:
                if default_name.lower() in self.name.lower():
                    self.color = default_color
                    break

        super().save(*args, **kwargs)

    @classmethod
    def create_default_categories(cls, user):
        """Create default categories for a new user"""
        for name, description, color in cls.DEFAULT_CATEGORIES:
            cls.objects.get_or_create(
                name=name.title(),
                user=user,
                defaults={
                    'description': description,
                    'color': color,
                    'is_default': True,
                    'category_type': 'income' if name == 'income' else 'expense'
                }
            )

    @property
    def total_expenses(self):
        """Calculate total expenses for this category"""
        from expenses.models import Expense
        from django.utils import timezone
        from datetime import datetime

        now = timezone.now()
        start_of_month = datetime(now.year, now.month, 1)

        return Expense.objects.filter(
            category=self,
            date__gte=start_of_month
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or 0.00

    @property
    def budget_amount(self):
        """Calculate budget amount based on percentage"""
        if self.budget_percentage > 0:
            return (self.user.monthly_income * self.budget_percentage) / 100
        return 0.00

    @property
    def remaining_budget(self):
        """Calculate remaining budget for this category"""
        return self.budget_amount - self.total_expenses

    @property
    def usage_percentage(self):
        """Calculate usage percentage of budget"""
        if self.budget_amount > 0:
            return (self.total_expenses / self.budget_amount) * 100
        return 0.00


class CategoryGroup(models.Model):
    """Group categories for better organization"""

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#6b7280')
    icon = models.CharField(max_length=50, blank=True)

    # User relationship
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='category_groups')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Category Group')
        verbose_name_plural = _('Category Groups')
        unique_together = ['name', 'user']
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    @property
    def categories(self):
        """Get all categories in this group"""
        return self.categories.all()

    @property
    def total_budget(self):
        """Calculate total budget for all categories in this group"""
        return sum(category.budget_amount for category in self.categories.all())

    @property
    def total_expenses(self):
        """Calculate total expenses for all categories in this group"""
        return sum(category.total_expenses for category in self.categories.all())

