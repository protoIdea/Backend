from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.db.models import Sum, Count
from django.utils import timezone

User = get_user_model()


class Expense(models.Model):
    """Expense model for tracking user expenses"""

    # Expense types
    EXPENSE_TYPES = [
        ('one_time', 'One Time'),
        ('recurring', 'Recurring'),
        ('subscription', 'Subscription'),
    ]

    # Payment methods
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_payment', 'Mobile Payment'),
        ('check', 'Check'),
        ('other', 'Other'),
    ]

    # Basic expense information
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='expenses')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )

    # Category and date
    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.CASCADE,
        related_name='expenses'
    )
    date = models.DateField()
    time = models.TimeField(blank=True, null=True)

    # Expense details
    expense_type = models.CharField(
        max_length=20, choices=EXPENSE_TYPES, default='one_time')
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHODS, default='cash')

    # Recurring expense settings
    is_recurring = models.BooleanField(default=False)
    recurring_frequency = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('yearly', 'Yearly'),
        ],
        blank=True,
        null=True
    )
    recurring_end_date = models.DateField(blank=True, null=True)

    # Location and tags
    location = models.CharField(max_length=200, blank=True)
    tags = models.JSONField(default=list, blank=True)

    # Receipt and attachments
    receipt_image = models.ImageField(
        upload_to='receipts/', blank=True, null=True)
    attachments = models.JSONField(default=list, blank=True)

    # Status and flags
    is_verified = models.BooleanField(default=False)
    is_shared = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Expense')
        verbose_name_plural = _('Expenses')
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['category', 'date']),
            models.Index(fields=['amount', 'date']),
        ]

    def __str__(self):
        return f"{self.title} - ${self.amount} ({self.user.username})"

    def save(self, *args, **kwargs):
        """Override save to handle recurring expenses"""
        if self.is_recurring and not self.recurring_frequency:
            self.recurring_frequency = 'monthly'

        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        """Check if recurring expense is overdue"""
        if not self.is_recurring:
            return False

        today = timezone.now().date()
        if self.recurring_frequency == 'daily':
            return today > self.date
        elif self.recurring_frequency == 'weekly':
            return (today - self.date).days > 7
        elif self.recurring_frequency == 'monthly':
            return (today - self.date).days > 30
        elif self.recurring_frequency == 'yearly':
            return (today - self.date).days > 365

        return False

    @property
    def next_due_date(self):
        """Calculate next due date for recurring expense"""
        if not self.is_recurring:
            return None

        from datetime import timedelta

        if self.recurring_frequency == 'daily':
            return self.date + timedelta(days=1)
        elif self.recurring_frequency == 'weekly':
            return self.date + timedelta(weeks=1)
        elif self.recurring_frequency == 'monthly':
            # Simple monthly calculation
            return self.date + timedelta(days=30)
        elif self.recurring_frequency == 'yearly':
            return self.date + timedelta(days=365)

        return None

    @classmethod
    def get_monthly_summary(cls, user, year, month):
        """Get monthly expense summary for a user"""
        start_date = timezone.datetime(year, month, 1).date()
        if month == 12:
            end_date = timezone.datetime(year + 1, 1, 1).date()
        else:
            end_date = timezone.datetime(year, month + 1, 1).date()

        expenses = cls.objects.filter(
            user=user,
            date__gte=start_date,
            date__lt=end_date
        )

        total_amount = expenses.aggregate(total=Sum('amount'))['total'] or 0.00
        expense_count = expenses.count()

        # Group by category
        category_totals = expenses.values('category__name').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')

        return {
            'total_amount': total_amount,
            'expense_count': expense_count,
            'category_totals': category_totals,
            'period': f"{year}-{month:02d}"
        }

    @classmethod
    def get_yearly_summary(cls, user, year):
        """Get yearly expense summary for a user"""
        start_date = timezone.datetime(year, 1, 1).date()
        end_date = timezone.datetime(year + 1, 1, 1).date()

        expenses = cls.objects.filter(
            user=user,
            date__gte=start_date,
            date__lt=end_date
        )

        total_amount = expenses.aggregate(total=Sum('amount'))['total'] or 0.00
        expense_count = expenses.count()

        # Monthly breakdown
        monthly_totals = []
        for month in range(1, 13):
            month_start = timezone.datetime(year, month, 1).date()
            if month == 12:
                month_end = timezone.datetime(year + 1, 1, 1).date()
            else:
                month_end = timezone.datetime(year, month + 1, 1).date()

            month_total = expenses.filter(
                date__gte=month_start,
                date__lt=month_end
            ).aggregate(total=Sum('amount'))['total'] or 0.00

            monthly_totals.append({
                'month': month,
                'total': month_total
            })

        return {
            'total_amount': total_amount,
            'expense_count': expense_count,
            'monthly_totals': monthly_totals,
            'year': year
        }


class ExpenseTemplate(models.Model):
    """Template for common expenses"""

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.CASCADE,
        related_name='expense_templates'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='expense_templates')

    # Template settings
    is_favorite = models.BooleanField(default=False)
    tags = models.JSONField(default=list, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Expense Template')
        verbose_name_plural = _('Expense Templates')
        ordering = ['-is_favorite', 'name']
        unique_together = ['name', 'user']

    def __str__(self):
        return f"{self.name} - ${self.amount} ({self.user.username})"

    def create_expense(self, date=None, **kwargs):
        """Create an expense from this template"""
        if date is None:
            date = timezone.now().date()

        expense_data = {
            'user': self.user,
            'title': self.name,
            'description': self.description,
            'amount': self.amount,
            'category': self.category,
            'date': date,
            'tags': self.tags,
            **kwargs
        }

        return Expense.objects.create(**expense_data)


class ExpenseReminder(models.Model):
    """Reminder for upcoming or overdue expenses"""

    expense = models.ForeignKey(
        Expense, on_delete=models.CASCADE, related_name='reminders')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='expense_reminders')

    # Reminder settings
    reminder_date = models.DateField()
    reminder_time = models.TimeField(blank=True, null=True)
    message = models.TextField(blank=True)

    # Status
    is_sent = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Expense Reminder')
        verbose_name_plural = _('Expense Reminders')
        ordering = ['reminder_date', 'reminder_time']

    def __str__(self):
        return f"Reminder for {self.expense.title} on {self.reminder_date}"

    @property
    def is_overdue(self):
        """Check if reminder is overdue"""
        today = timezone.now().date()
        return today > self.reminder_date

