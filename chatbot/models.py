from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class ChatMessage(models.Model):
    """Chat message model for the AI chatbot"""

    # Message types
    MESSAGE_TYPES = [
        ('user', 'User Message'),
        ('bot', 'Bot Message'),
        ('system', 'System Message'),
    ]

    # Message status
    MESSAGE_STATUS = [
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
    ]

    # Basic message information
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='chat_messages')
    message_type = models.CharField(
        max_length=20, choices=MESSAGE_TYPES, default='user')
    content = models.TextField()

    # Message metadata
    status = models.CharField(
        max_length=20, choices=MESSAGE_STATUS, default='sent')
    is_processed = models.BooleanField(default=False)

    # AI processing
    ai_response = models.TextField(blank=True)
    confidence_score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='AI confidence score (0-1)'
    )

    # Context and intent
    detected_intent = models.CharField(max_length=100, blank=True)
    entities = models.JSONField(default=dict, blank=True)
    context_data = models.JSONField(default=dict, blank=True)

    # Message threading
    parent_message = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replies'
    )
    conversation_id = models.CharField(max_length=100, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('Chat Message')
        verbose_name_plural = _('Chat Messages')
        ordering = ['conversation_id', 'created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['conversation_id', 'created_at']),
            models.Index(fields=['message_type', 'is_processed']),
        ]

    def __str__(self):
        return f"{self.message_type} message from {self.user.username} at {self.created_at}"

    @property
    def is_user_message(self):
        """Check if this is a user message"""
        return self.message_type == 'user'

    @property
    def is_bot_message(self):
        """Check if this is a bot message"""
        return self.message_type == 'bot'

    @property
    def has_replies(self):
        """Check if this message has replies"""
        return self.replies.exists()

    def mark_as_processed(self):
        """Mark message as processed"""
        from django.utils import timezone
        self.is_processed = True
        self.processed_at = timezone.now()
        self.save(update_fields=['is_processed', 'processed_at'])

    @classmethod
    def get_conversation_history(cls, user, conversation_id=None, limit=50):
        """Get conversation history for a user"""
        queryset = cls.objects.filter(user=user)

        if conversation_id:
            queryset = queryset.filter(conversation_id=conversation_id)

        return queryset.order_by('-created_at')[:limit]


class ChatSession(models.Model):
    """Chat session for tracking conversations"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='chat_sessions')
    session_id = models.CharField(max_length=100, unique=True)

    # Session metadata
    is_active = models.BooleanField(default=True)
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)

    # Session context
    context_data = models.JSONField(default=dict, blank=True)
    user_preferences = models.JSONField(default=dict, blank=True)

    # Session statistics
    message_count = models.IntegerField(default=0)
    total_tokens = models.IntegerField(default=0)

    class Meta:
        verbose_name = _('Chat Session')
        verbose_name_plural = _('Chat Sessions')
        ordering = ['-last_activity']

    def __str__(self):
        return f"Chat session {self.session_id} for {self.user.username}"

    def update_activity(self):
        """Update last activity timestamp"""
        from django.utils import timezone
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])

    def increment_message_count(self):
        """Increment message count"""
        self.message_count += 1
        self.save(update_fields=['message_count'])

    @classmethod
    def get_active_session(cls, user):
        """Get or create active session for user"""
        session, created = cls.objects.get_or_create(
            user=user,
            is_active=True,
            defaults={'session_id': cls.generate_session_id()}
        )
        return session

    @staticmethod
    def generate_session_id():
        """Generate unique session ID"""
        import uuid
        return str(uuid.uuid4())


class ChatbotKnowledge(models.Model):
    """Knowledge base for the chatbot"""

    # Knowledge types
    KNOWLEDGE_TYPES = [
        ('faq', 'Frequently Asked Question'),
        ('tip', 'Budgeting Tip'),
        ('rule', 'Budgeting Rule'),
        ('example', 'Example'),
        ('definition', 'Definition'),
    ]

    # Knowledge content
    title = models.CharField(max_length=200)
    content = models.TextField()
    knowledge_type = models.CharField(
        max_length=20, choices=KNOWLEDGE_TYPES, default='tip')

    # Categorization
    category = models.CharField(max_length=100, blank=True)
    tags = models.JSONField(default=list, blank=True)

    # Usage tracking
    usage_count = models.IntegerField(default=0)
    last_used = models.DateTimeField(null=True, blank=True)

    # Metadata
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(
        default=1, help_text='Priority for matching (1-10)')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Chatbot Knowledge')
        verbose_name_plural = _('Chatbot Knowledge')
        ordering = ['-priority', '-usage_count']
        indexes = [
            models.Index(fields=['knowledge_type', 'category']),
            models.Index(fields=['is_active', 'priority']),
        ]

    def __str__(self):
        return f"{self.title} ({self.knowledge_type})"

    def increment_usage(self):
        """Increment usage count and update last used"""
        from django.utils import timezone
        self.usage_count += 1
        self.last_used = timezone.now()
        self.save(update_fields=['usage_count', 'last_used'])

    @classmethod
    def search_knowledge(cls, query, category=None, limit=10):
        """Search knowledge base"""
        queryset = cls.objects.filter(is_active=True)

        if category:
            queryset = queryset.filter(category=category)

        # Simple text search (can be enhanced with full-text search)
        if query:
            queryset = queryset.filter(
                models.Q(title__icontains=query) |
                models.Q(content__icontains=query) |
                models.Q(tags__contains=[query])
            )

        return queryset.order_by('-priority', '-usage_count')[:limit]


class ChatbotAnalytics(models.Model):
    """Analytics for chatbot usage"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='chatbot_analytics')
    session = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE, related_name='analytics')

    # Interaction data
    message_count = models.IntegerField(default=0)
    session_duration = models.DurationField(null=True, blank=True)

    # User satisfaction
    satisfaction_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    feedback = models.TextField(blank=True)

    # AI performance
    response_time = models.DurationField(null=True, blank=True)
    accuracy_score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Chatbot Analytics')
        verbose_name_plural = _('Chatbot Analytics')
        ordering = ['-created_at']

    def __str__(self):
        return f"Analytics for {self.user.username} session {self.session.session_id}"

    @classmethod
    def get_user_stats(cls, user):
        """Get chatbot usage statistics for a user"""
        analytics = cls.objects.filter(user=user)

        return {
            'total_sessions': analytics.count(),
            'total_messages': analytics.aggregate(
                total=models.Sum('message_count')
            )['total'] or 0,
            'avg_satisfaction': analytics.aggregate(
                avg=models.Avg('satisfaction_rating')
            )['avg'] or 0,
            'avg_response_time': analytics.aggregate(
                avg=models.Avg('response_time')
            )['avg'] or 0,
        }
