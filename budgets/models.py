from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.db.models import Sum
from django.utils import timezone

User = get_user_model()


class Budget(models.Model):
    """Budget model for managing user budgets"""

    # Budget types
    BUDGET_TYPES = [
        ('monthly', 'Monthly'),
        ('weekly', 'Weekly'),
        ('yearly', 'Yearly'),
        ('custom', 'Custom Period'),
    ]

    # Budget status
    BUDGET_STATUS = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
    ]

    # Basic budget information
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='budgets')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Budget amount and period
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    budget_type = models.CharField(
        max_length=20, choices=BUDGET_TYPES, default='monthly')

    # Custom period settings
    start_date = models.DateField()
    end_date = models.DateField()

    # Budget status and settings
    status = models.CharField(
        max_length=20, choices=BUDGET_STATUS, default='active')
    is_active = models.BooleanField(default=True)
    is_shared = models.BooleanField(default=False)

    # Budget allocation
    allocated_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

    # Notifications and alerts
    alert_threshold = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=80.00,
        help_text='Percentage of budget used to trigger alerts'
    )
    send_notifications = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Budget')
        verbose_name_plural = _('Budgets')
        ordering = ['-start_date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'start_date']),
            models.Index(fields=['status', 'is_active']),
        ]

    def __str__(self):
        return f"{self.name} - ${self.amount} ({self.user.username})"

    def save(self, *args, **kwargs):
        """Override save to set default dates and validate"""
        if not self.start_date:
            self.start_date = timezone.now().date()

        if not self.end_date:
            if self.budget_type == 'weekly':
                self.end_date = self.start_date + timezone.timedelta(days=7)
            elif self.budget_type == 'monthly':
                # Calculate end of month
                if self.start_date.month == 12:
                    self.end_date = self.start_date.replace(
                        year=self.start_date.year + 1, month=1, day=1) - timezone.timedelta(days=1)
                else:
                    self.end_date = self.start_date.replace(
                        month=self.start_date.month + 1, day=1) - timezone.timedelta(days=1)
            elif self.budget_type == 'yearly':
                self.end_date = self.start_date.replace(
                    year=self.start_date.year + 1) - timezone.timedelta(days=1)

        super().save(*args, **kwargs)

    @property
    def total_expenses(self):
        """Calculate total expenses for this budget period"""
        from expenses.models import Expense

        expenses = Expense.objects.filter(
            user=self.user,
            date__gte=self.start_date,
            date__lte=self.end_date
        )

        return expenses.aggregate(total=Sum('amount'))['total'] or 0.00

    @property
    def remaining_amount(self):
        """Calculate remaining budget amount"""
        return self.amount - self.total_expenses

    @property
    def usage_percentage(self):
        """Calculate budget usage percentage"""
        if self.amount > 0:
            return (self.total_expenses / self.amount) * 100
        return 0.00

    @property
    def is_over_budget(self):
        """Check if budget is exceeded"""
        return self.total_expenses > self.amount

    @property
    def is_near_limit(self):
        """Check if budget is near the alert threshold"""
        return self.usage_percentage >= self.alert_threshold

    @property
    def days_remaining(self):
        """Calculate days remaining in budget period"""
        today = timezone.now().date()
        if today > self.end_date:
            return 0
        return (self.end_date - today).days

    @property
    def progress_percentage(self):
        """Calculate progress through budget period"""
        total_days = (self.end_date - self.start_date).days
        if total_days <= 0:
            return 100

        days_elapsed = (timezone.now().date() - self.start_date).days
        return min(100, max(0, (days_elapsed / total_days) * 100))

    @classmethod
    def get_active_budgets(cls, user):
        """Get all active budgets for a user"""
        today = timezone.now().date()
        return cls.objects.filter(
            user=user,
            is_active=True,
            start_date__lte=today,
            end_date__gte=today
        )

    @classmethod
    def get_monthly_budget(cls, user, year, month):
        """Get monthly budget for a specific month"""
        start_date = timezone.datetime(year, month, 1).date()
        if month == 12:
            end_date = timezone.datetime(year + 1, 1, 1).date()
        else:
            end_date = timezone.datetime(year, month + 1, 1).date()

        try:
            return cls.objects.get(
                user=user,
                start_date__lte=start_date,
                end_date__gte=end_date,
                is_active=True
            )
        except cls.DoesNotExist:
            return None


class BudgetCategory(models.Model):
    """Budget allocation for specific categories"""

    budget = models.ForeignKey(
        Budget, on_delete=models.CASCADE, related_name='categories')
    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.CASCADE,
        related_name='budget_allocations'
    )

    # Allocation amount
    allocated_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Budget Category')
        verbose_name_plural = _('Budget Categories')
        unique_together = ['budget', 'category']
        ordering = ['-allocated_amount']

    def __str__(self):
        return f"{self.category.name} - ${self.allocated_amount} ({self.budget.name})"

    @property
    def total_expenses(self):
        """Calculate total expenses for this category in budget period"""
        from expenses.models import Expense

        expenses = Expense.objects.filter(
            user=self.budget.user,
            category=self.category,
            date__gte=self.budget.start_date,
            date__lte=self.budget.end_date
        )

        return expenses.aggregate(total=Sum('amount'))['total'] or 0.00

    @property
    def remaining_amount(self):
        """Calculate remaining budget for this category"""
        return self.allocated_amount - self.total_expenses

    @property
    def usage_percentage(self):
        """Calculate usage percentage for this category"""
        if self.allocated_amount > 0:
            return (self.total_expenses / self.allocated_amount) * 100
        return 0.00


class BudgetTemplate(models.Model):
    """Template for creating budgets"""

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    budget_type = models.CharField(
        max_length=20, choices=Budget.BUDGET_TYPES, default='monthly')

    # Template settings
    is_default = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_budget_templates'
    )

    # Category allocations (stored as JSON)
    category_allocations = models.JSONField(
        default=dict,
        help_text='Category allocations as percentage of total budget'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Budget Template')
        verbose_name_plural = _('Budget Templates')
        ordering = ['-is_default', 'name']

    def __str__(self):
        return f"{self.name} ({self.budget_type})"

    def create_budget(self, user, amount, start_date=None, **kwargs):
        """Create a budget from this template"""
        if start_date is None:
            start_date = timezone.now().date()

        # Create budget
        budget = Budget.objects.create(
            user=user,
            name=self.name,
            description=self.description,
            amount=amount,
            budget_type=self.budget_type,
            start_date=start_date,
            **kwargs
        )

        # Create category allocations
        for category_name, percentage in self.category_allocations.items():
            try:
                category = user.categories.get(name=category_name)
                BudgetCategory.objects.create(
                    budget=budget,
                    category=category,
                    allocated_amount=(amount * percentage) / 100
                )
            except:
                continue

        return budget


class BudgetAlert(models.Model):
    """Alerts for budget thresholds"""

    budget = models.ForeignKey(
        Budget, on_delete=models.CASCADE, related_name='alerts')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='budget_alerts')

    # Alert details
    alert_type = models.CharField(
        max_length=20,
        choices=[
            ('threshold', 'Threshold Reached'),
            ('over_budget', 'Over Budget'),
            ('near_limit', 'Near Limit'),
            ('period_ending', 'Period Ending'),
        ]
    )
    message = models.TextField()

    # Alert status
    is_read = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('Budget Alert')
        verbose_name_plural = _('Budget Alerts')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.alert_type} alert for {self.budget.name}"

    def mark_as_read(self):
        """Mark alert as read"""
        self.is_read = True
        self.read_at = timezone.now()
        self.save()

    def dismiss(self):
        """Dismiss the alert"""
        self.is_dismissed = True
        self.save()
