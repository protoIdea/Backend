from rest_framework import serializers
from .models import Expense, ExpenseTemplate, ExpenseReminder


class ExpenseSerializer(serializers.ModelSerializer):
    """Serializer for Expense model"""

    category_name = serializers.CharField(
        source='category.name', read_only=True)
    category_color = serializers.CharField(
        source='category.color', read_only=True)
    user_username = serializers.CharField(
        source='user.username', read_only=True)

    class Meta:
        model = Expense
        fields = [
            'id', 'user', 'title', 'description', 'amount', 'category',
            'category_name', 'category_color', 'user_username', 'date', 'time',
            'expense_type', 'payment_method', 'is_recurring', 'recurring_frequency',
            'recurring_end_date', 'location', 'tags', 'receipt_image',
            'attachments', 'is_verified', 'is_shared', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def create(self, validated_data):
        """Create expense and assign to current user"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ExpenseCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating expenses"""

    class Meta:
        model = Expense
        fields = [
            'title', 'description', 'amount', 'category', 'date', 'time',
            'expense_type', 'payment_method', 'is_recurring', 'recurring_frequency',
            'recurring_end_date', 'location', 'tags', 'receipt_image',
            'attachments', 'notes'
        ]

    def create(self, validated_data):
        """Create expense and assign to current user"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ExpenseUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating expenses"""

    class Meta:
        model = Expense
        fields = [
            'title', 'description', 'amount', 'category', 'date', 'time',
            'expense_type', 'payment_method', 'is_recurring', 'recurring_frequency',
            'recurring_end_date', 'location', 'tags', 'receipt_image',
            'attachments', 'is_verified', 'is_shared', 'notes'
        ]


class ExpenseTemplateSerializer(serializers.ModelSerializer):
    """Serializer for ExpenseTemplate model"""

    category_name = serializers.CharField(
        source='category.name', read_only=True)
    category_color = serializers.CharField(
        source='category.color', read_only=True)

    class Meta:
        model = ExpenseTemplate
        fields = [
            'id', 'name', 'description', 'amount', 'category', 'category_name',
            'category_color', 'is_favorite', 'tags', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ExpenseReminderSerializer(serializers.ModelSerializer):
    """Serializer for ExpenseReminder model"""

    expense_title = serializers.CharField(
        source='expense.title', read_only=True)
    expense_amount = serializers.DecimalField(
        source='expense.amount', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = ExpenseReminder
        fields = [
            'id', 'expense', 'expense_title', 'expense_amount', 'reminder_date',
            'reminder_time', 'message', 'is_sent', 'is_read', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ExpenseSummarySerializer(serializers.Serializer):
    """Serializer for expense summary data"""

    total_expenses = serializers.DecimalField(max_digits=10, decimal_places=2)
    expense_count = serializers.IntegerField()
    average_expense = serializers.DecimalField(max_digits=10, decimal_places=2)
    largest_expense = serializers.DecimalField(max_digits=10, decimal_places=2)
    category_breakdown = serializers.ListField()
    monthly_totals = serializers.ListField()
    recent_expenses = serializers.ListField()


class ExpenseStatsSerializer(serializers.Serializer):
    """Serializer for expense statistics"""

    period = serializers.CharField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    expense_count = serializers.IntegerField()
    category_totals = serializers.ListField()
    payment_method_breakdown = serializers.ListField()
    daily_averages = serializers.ListField()


class BulkExpenseSerializer(serializers.Serializer):
    """Serializer for bulk expense operations"""

    expenses = serializers.ListField(
        child=serializers.DictField()
    )

    def validate_expenses(self, value):
        """Validate bulk expense data"""
        for expense_data in value:
            required_fields = ['title', 'amount', 'category', 'date']
            for field in required_fields:
                if field not in expense_data:
                    raise serializers.ValidationError(
                        f"Missing required field: {field}")

        return value


class ExpenseFilterSerializer(serializers.Serializer):
    """Serializer for expense filtering"""

    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    category = serializers.IntegerField(required=False)
    min_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False)
    max_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False)
    expense_type = serializers.ChoiceField(
        choices=Expense.EXPENSE_TYPES, required=False)
    payment_method = serializers.ChoiceField(
        choices=Expense.PAYMENT_METHODS, required=False)
    is_recurring = serializers.BooleanField(required=False)
    tags = serializers.ListField(child=serializers.CharField(), required=False)
