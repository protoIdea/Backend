from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Custom User model extending Django's AbstractUser"""

    # Additional fields
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/', blank=True, null=True)

    # Budget preferences
    currency = models.CharField(
        max_length=3, default='USD', help_text='Preferred currency for budgets')
    monthly_income = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00)

    # Account settings
    is_premium = models.BooleanField(default=False)
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-date_joined']

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        """Return the user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    @property
    def total_budget(self):
        """Calculate total budget across all active budgets"""
        from budgets.models import Budget
        return Budget.objects.filter(user=self, is_active=True).aggregate(
            total=models.Sum('amount')
        )['total'] or 0.00

    @property
    def total_expenses(self):
        """Calculate total expenses for current month"""
        from expenses.models import Expense
        from django.utils import timezone
        from datetime import datetime

        now = timezone.now()
        start_of_month = datetime(now.year, now.month, 1)

        return Expense.objects.filter(
            user=self,
            date__gte=start_of_month
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or 0.00

    @property
    def remaining_budget(self):
        """Calculate remaining budget for current month"""
        return self.total_budget - self.total_expenses


class UserProfile(models.Model):
    """Extended user profile information"""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile')

    # Personal information
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)

    # Financial goals
    savings_goal = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00)
    emergency_fund_goal = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00)

    # Budget preferences
    default_budget_period = models.CharField(
        max_length=20,
        choices=[
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('yearly', 'Yearly'),
        ],
        default='monthly'
    )

    # Notification preferences
    email_frequency = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('never', 'Never'),
        ],
        default='weekly'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def save(self, *args, **kwargs):
        """Override save to create profile if it doesn't exist"""
        if not self.pk:
            # Set default values for new profiles
            if not self.savings_goal:
                self.savings_goal = self.user.monthly_income * 0.2  # 20% of income
            if not self.emergency_fund_goal:
                self.emergency_fund_goal = self.user.monthly_income * 3  # 3 months of income
        super().save(*args, **kwargs)

