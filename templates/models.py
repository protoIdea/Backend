from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class BudgetTemplate(models.Model):
    """Template for creating budgets with predefined category allocations"""

    # Template types
    TEMPLATE_TYPES = [
        ('student', 'Student Budget'),
        ('family', 'Family Budget'),
        ('travel', 'Travel Budget'),
        ('emergency', 'Emergency Fund'),
        ('business', 'Business Budget'),
        ('retirement', 'Retirement Budget'),
        ('wedding', 'Wedding Budget'),
        ('home_renovation', 'Home Renovation'),
        ('custom', 'Custom Template'),
    ]

    # Budget periods
    BUDGET_PERIODS = [
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
        ('custom', 'Custom Period'),
    ]

    # Basic template information
    name = models.CharField(max_length=200)
    description = models.TextField()
    template_type = models.CharField(
        max_length=30, choices=TEMPLATE_TYPES, default='custom')
    budget_period = models.CharField(
        max_length=20, choices=BUDGET_PERIODS, default='monthly')

    # Template settings
    is_default = models.BooleanField(
        default=False, help_text='Is this a system default template?')
    is_public = models.BooleanField(
        default=False, help_text='Can other users see this template?')
    is_featured = models.BooleanField(
        default=False, help_text='Is this template featured?')

    # Template creator
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_template_templates'
    )

    # Template image and metadata
    image = models.ImageField(
        upload_to='template_images/', blank=True, null=True)
    tags = models.JSONField(default=list, blank=True)

    # Template rating and usage
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    usage_count = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Budget Template')
        verbose_name_plural = _('Budget Templates')
        ordering = ['-is_default', '-rating', '-usage_count']
        indexes = [
            models.Index(fields=['template_type', 'is_public']),
            models.Index(fields=['is_featured', 'rating']),
        ]

    def __str__(self):
        return f"{self.name} ({self.template_type})"

    def increment_usage(self):
        """Increment usage count"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])

    @classmethod
    def get_default_templates(cls):
        """Get all default system templates"""
        return cls.objects.filter(is_default=True, is_public=True)

    @classmethod
    def get_featured_templates(cls):
        """Get featured templates"""
        return cls.objects.filter(is_featured=True, is_public=True)

    @classmethod
    def get_templates_by_type(cls, template_type):
        """Get templates by specific type"""
        return cls.objects.filter(
            template_type=template_type,
            is_public=True
        ).order_by('-rating', '-usage_count')


class TemplateCategory(models.Model):
    """Category allocation for a budget template"""

    template = models.ForeignKey(
        BudgetTemplate,
        on_delete=models.CASCADE,
        related_name='categories'
    )

    # Category information
    category_name = models.CharField(max_length=100)
    category_description = models.TextField(blank=True)
    category_color = models.CharField(max_length=7, default='#3b82f6')
    category_icon = models.CharField(max_length=50, blank=True)

    # Allocation settings
    allocation_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Percentage of total budget allocated to this category'
    )

    # Category type
    category_type = models.CharField(
        max_length=20,
        choices=[
            ('income', 'Income'),
            ('expense', 'Expense'),
            ('savings', 'Savings'),
        ],
        default='expense'
    )

    # Priority and notes
    priority = models.IntegerField(
        default=1, help_text='Priority order for this category')
    notes = models.TextField(blank=True, help_text='Additional notes or tips')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Template Category')
        verbose_name_plural = _('Template Categories')
        ordering = ['template', 'priority', 'allocation_percentage']
        unique_together = ['template', 'category_name']

    def __str__(self):
        return f"{self.category_name} ({self.template.name})"

    def get_allocation_amount(self, total_budget):
        """Calculate allocation amount for a given total budget"""
        return (total_budget * self.allocation_percentage) / 100


class TemplateReview(models.Model):
    """User reviews for budget templates"""

    template = models.ForeignKey(
        BudgetTemplate,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='template_reviews'
    )

    # Review content
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Rating from 1 to 5 stars'
    )
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField()

    # Review metadata
    is_verified_user = models.BooleanField(default=False)
    is_helpful = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Template Review')
        verbose_name_plural = _('Template Reviews')
        ordering = ['-created_at']
        unique_together = ['template', 'user']

    def __str__(self):
        return f"Review by {self.user.username} for {self.template.name}"

    def save(self, *args, **kwargs):
        """Override save to update template rating"""
        super().save(*args, **kwargs)
        self.update_template_rating()

    def update_template_rating(self):
        """Update the template's average rating"""
        reviews = self.template.reviews.all()
        if reviews.exists():
            avg_rating = sum(
                review.rating for review in reviews) / reviews.count()
            self.template.rating = round(avg_rating, 2)
            self.template.save(update_fields=['rating'])


class TemplateUsage(models.Model):
    """Track template usage by users"""

    template = models.ForeignKey(
        BudgetTemplate,
        on_delete=models.CASCADE,
        related_name='usage_records'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='template_usage'
    )

    # Usage details
    budget_created = models.ForeignKey(
        'budgets.Budget',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='template_source'
    )

    # Usage metadata
    used_at = models.DateTimeField(auto_now_add=True)
    success_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text='How successful was this template for the user?'
    )
    feedback = models.TextField(blank=True)

    class Meta:
        verbose_name = _('Template Usage')
        verbose_name_plural = _('Template Usage')
        ordering = ['-used_at']
        unique_together = ['template', 'user', 'used_at']

    def __str__(self):
        return f"{self.user.username} used {self.template.name} on {self.used_at}"
