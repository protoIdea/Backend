from rest_framework import serializers
from .models import Category, CategoryGroup
from django.db import models


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""

    total_expenses = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True)
    budget_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True)
    remaining_budget = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True)
    usage_percentage = serializers.DecimalField(
        max_digits=5, decimal_places=2, read_only=True)

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'description', 'color', 'icon', 'category_type',
            'budget_percentage', 'is_default', 'is_active', 'total_expenses',
            'budget_amount', 'remaining_budget', 'usage_percentage',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'total_expenses',
                            'budget_amount', 'remaining_budget', 'usage_percentage']

    def validate(self, attrs):
        """Validate category data"""
        # Ensure budget percentage doesn't exceed 100%
        if 'budget_percentage' in attrs:
            user = self.context['request'].user
            existing_percentage = Category.objects.filter(
                user=user,
                is_active=True
            ).exclude(
                pk=self.instance.pk if self.instance else None
            ).aggregate(
                total=models.Sum('budget_percentage')
            )['total'] or 0.00

            if existing_percentage + attrs['budget_percentage'] > 100:
                raise serializers.ValidationError(
                    "Total budget percentage across all categories cannot exceed 100%"
                )

        return attrs


class CategoryGroupSerializer(serializers.ModelSerializer):
    """Serializer for CategoryGroup model"""

    categories = CategorySerializer(many=True, read_only=True)
    total_budget = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True)
    total_expenses = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CategoryGroup
        fields = [
            'id', 'name', 'description', 'color', 'icon', 'categories',
            'total_budget', 'total_expenses', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'categories',
                            'total_budget', 'total_expenses']


class CategoryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating categories"""

    class Meta:
        model = Category
        fields = [
            'name', 'description', 'color', 'icon', 'category_type',
            'budget_percentage'
        ]

    def create(self, validated_data):
        """Create category and assign to current user"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class CategoryUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating categories"""

    class Meta:
        model = Category
        fields = [
            'name', 'description', 'color', 'icon', 'category_type',
            'budget_percentage', 'is_active'
        ]


class CategoryBulkUpdateSerializer(serializers.Serializer):
    """Serializer for bulk updating categories"""

    categories = serializers.ListField(
        child=serializers.DictField()
    )

    def validate_categories(self, value):
        """Validate bulk update data"""
        for category_data in value:
            if 'id' not in category_data:
                raise serializers.ValidationError(
                    "Each category must have an 'id' field")

        return value

    def update(self, instance, validated_data):
        """Update multiple categories"""
        user = self.context['request'].user
        updated_categories = []

        for category_data in validated_data['categories']:
            try:
                category = Category.objects.get(
                    id=category_data['id'],
                    user=user
                )

                # Update fields
                for field, value in category_data.items():
                    if field != 'id' and hasattr(category, field):
                        setattr(category, field, value)

                category.save()
                updated_categories.append(category)

            except Category.DoesNotExist:
                continue

        return {'updated_categories': updated_categories}


class CategoryStatsSerializer(serializers.Serializer):
    """Serializer for category statistics"""

    category_id = serializers.IntegerField()
    category_name = serializers.CharField()
    category_color = serializers.CharField()
    total_expenses = serializers.DecimalField(max_digits=10, decimal_places=2)
    budget_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    remaining_budget = serializers.DecimalField(
        max_digits=10, decimal_places=2)
    usage_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    expense_count = serializers.IntegerField()


class CategorySummarySerializer(serializers.Serializer):
    """Serializer for category summary"""

    total_categories = serializers.IntegerField()
    active_categories = serializers.IntegerField()
    total_budget_allocated = serializers.DecimalField(
        max_digits=10, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=10, decimal_places=2)
    remaining_budget = serializers.DecimalField(
        max_digits=10, decimal_places=2)
    categories = CategoryStatsSerializer(many=True)

