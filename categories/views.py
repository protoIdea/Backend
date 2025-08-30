from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Category, CategoryGroup
from .serializers import (
    CategorySerializer, CategoryGroupSerializer, CategoryCreateSerializer,
    CategoryUpdateSerializer, CategoryBulkUpdateSerializer,
    CategoryStatsSerializer, CategorySummarySerializer
)


class CategoryListView(generics.ListCreateAPIView):
    """List and create categories"""
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['category_type', 'is_active', 'is_default']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'budget_percentage']

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CategoryCreateSerializer
        return CategorySerializer


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and delete a category"""
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return CategoryUpdateSerializer
        return CategorySerializer


class CategoryBulkUpdateView(APIView):
    """Bulk update multiple categories"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CategoryBulkUpdateSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.update(None, serializer.validated_data)
            return Response({
                'message': f"Updated {len(result['updated_categories'])} categories",
                'updated_categories': CategorySerializer(
                    result['updated_categories'], many=True
                ).data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryStatsView(APIView):
    """Get category statistics"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        period = request.query_params.get('period', 'month')

        # Calculate date range
        now = timezone.now()
        if period == 'week':
            start_date = now - timedelta(days=7)
        elif period == 'month':
            start_date = datetime(now.year, now.month, 1)
        elif period == 'year':
            start_date = datetime(now.year, 1, 1)
        else:
            start_date = datetime(now.year, now.month, 1)

        # Get categories with stats
        categories = Category.objects.filter(
            user=user,
            is_active=True
        ).annotate(
            expense_count=Count('expenses', filter=models.Q(
                expenses__date__gte=start_date
            )),
            total_expenses=Sum('expenses__amount', filter=models.Q(
                expenses__date__gte=start_date
            ))
        )

        # Prepare stats data
        stats_data = []
        for category in categories:
            total_expenses = category.total_expenses or 0.00
            budget_amount = category.budget_amount
            remaining_budget = budget_amount - total_expenses
            usage_percentage = (total_expenses / budget_amount *
                                100) if budget_amount > 0 else 0.00

            stats_data.append({
                'category_id': category.id,
                'category_name': category.name,
                'category_color': category.color,
                'total_expenses': total_expenses,
                'budget_amount': budget_amount,
                'remaining_budget': remaining_budget,
                'usage_percentage': round(usage_percentage, 2),
                'expense_count': category.expense_count or 0
            })

        # Calculate summary
        total_categories = categories.count()
        active_categories = categories.filter(is_active=True).count()
        total_budget_allocated = sum(cat.budget_amount for cat in categories)
        total_expenses = sum(cat.total_expenses or 0.00 for cat in categories)
        remaining_budget = total_budget_allocated - total_expenses

        summary_data = {
            'total_categories': total_categories,
            'active_categories': active_categories,
            'total_budget_allocated': total_budget_allocated,
            'total_expenses': total_expenses,
            'remaining_budget': remaining_budget,
            'categories': stats_data
        }

        return Response(summary_data, status=status.HTTP_200_OK)


class CategoryUsageReportView(APIView):
    """Get detailed category usage report"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        period = request.query_params.get('period', 'month')

        # Calculate date range
        now = timezone.now()
        if period == 'week':
            start_date = now - timedelta(days=7)
        elif period == 'month':
            start_date = datetime(now.year, now.month, 1)
        elif period == 'year':
            start_date = datetime(now.year, 1, 1)
        else:
            start_date = datetime(now.year, now.month, 1)

        # Get categories with detailed stats
        categories = Category.objects.filter(
            user=user,
            is_active=True
        ).prefetch_related('expenses')

        report_data = []
        for category in categories:
            expenses = category.expenses.filter(date__gte=start_date)
            total_amount = expenses.aggregate(total=Sum('amount'))[
                'total'] or 0.00
            expense_count = expenses.count()

            # Calculate average expense
            avg_expense = total_amount / expense_count if expense_count > 0 else 0.00

            # Get largest expense
            largest_expense = expenses.order_by('-amount').first()
            largest_amount = largest_expense.amount if largest_expense else 0.00

            report_data.append({
                'category_id': category.id,
                'category_name': category.name,
                'category_color': category.color,
                'budget_amount': category.budget_amount,
                'total_expenses': total_amount,
                'remaining_budget': category.budget_amount - total_amount,
                'usage_percentage': (total_amount / category.budget_amount * 100) if category.budget_amount > 0 else 0.00,
                'expense_count': expense_count,
                'average_expense': round(avg_expense, 2),
                'largest_expense': largest_amount,
                'is_over_budget': total_amount > category.budget_amount
            })

        # Sort by usage percentage (highest first)
        report_data.sort(key=lambda x: x['usage_percentage'], reverse=True)

        return Response({
            'period': period,
            'start_date': start_date,
            'end_date': now,
            'categories': report_data
        }, status=status.HTTP_200_OK)


class CategoryGroupListView(generics.ListCreateAPIView):
    """List and create category groups"""
    serializer_class = CategoryGroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['name']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']

    def get_queryset(self):
        return CategoryGroup.objects.filter(user=self.request.user)


class CategoryGroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and delete a category group"""
    serializer_class = CategoryGroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CategoryGroup.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_default_categories(request):
    """Create default categories for the current user"""
    try:
        Category.create_default_categories(request.user)
        return Response({
            'message': 'Default categories created successfully'
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({
            'error': 'Failed to create default categories',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def category_suggestions(request):
    """Get category suggestions based on expense description"""
    description = request.query_params.get('description', '').lower()

    if not description:
        return Response({
            'suggestions': []
        }, status=status.HTTP_200_OK)

    # Find categories with similar names
    suggestions = Category.objects.filter(
        user=request.user,
        name__icontains=description
    )[:5]

    # Also check description field
    desc_suggestions = Category.objects.filter(
        user=request.user,
        description__icontains=description
    )[:5]

    # Combine and remove duplicates
    all_suggestions = list(suggestions) + list(desc_suggestions)
    unique_suggestions = list(
        {cat.id: cat for cat in all_suggestions}.values())

    serializer = CategorySerializer(unique_suggestions[:5], many=True)
    return Response({
        'suggestions': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def duplicate_category(request, pk):
    """Duplicate an existing category"""
    try:
        original_category = Category.objects.get(pk=pk, user=request.user)

        # Create duplicate with modified name
        duplicate = Category.objects.create(
            user=request.user,
            name=f"{original_category.name} (Copy)",
            description=original_category.description,
            color=original_category.color,
            icon=original_category.icon,
            category_type=original_category.category_type,
            budget_percentage=0.00,  # Reset budget percentage
            is_default=False
        )

        serializer = CategorySerializer(duplicate)
        return Response({
            'message': 'Category duplicated successfully',
            'category': serializer.data
        }, status=status.HTTP_201_CREATED)

    except Category.DoesNotExist:
        return Response({
            'error': 'Category not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': 'Failed to duplicate category',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def category_usage_report(request):
    """Get detailed category usage report"""
    user = request.user
    period = request.query_params.get('period', 'month')

    # Calculate date range
    now = timezone.now()
    if period == 'week':
        start_date = now - timedelta(days=7)
    elif period == 'month':
        start_date = datetime(now.year, now.month, 1)
    elif period == 'year':
        start_date = datetime(now.year, 1, 1)
    else:
        start_date = datetime(now.year, now.month, 1)

    # Get categories with detailed stats
    categories = Category.objects.filter(
        user=user,
        is_active=True
    ).prefetch_related('expenses')

    report_data = []
    for category in categories:
        expenses = category.expenses.filter(date__gte=start_date)
        total_amount = expenses.aggregate(total=Sum('amount'))['total'] or 0.00
        expense_count = expenses.count()

        # Calculate average expense
        avg_expense = total_amount / expense_count if expense_count > 0 else 0.00

        # Get largest expense
        largest_expense = expenses.order_by('-amount').first()
        largest_amount = largest_expense.amount if largest_expense else 0.00

        report_data.append({
            'category_id': category.id,
            'category_name': category.name,
            'category_color': category.color,
            'budget_amount': category.budget_amount,
            'total_expenses': total_amount,
            'remaining_budget': category.budget_amount - total_amount,
            'usage_percentage': (total_amount / category.budget_amount * 100) if category.budget_amount > 0 else 0.00,
            'expense_count': expense_count,
            'average_expense': round(avg_expense, 2),
            'largest_expense': largest_amount,
            'is_over_budget': total_amount > category.budget_amount
        })

    # Sort by usage percentage (highest first)
    report_data.sort(key=lambda x: x['usage_percentage'], reverse=True)

    return Response({
        'period': period,
        'start_date': start_date,
        'end_date': now,
        'categories': report_data
    }, status=status.HTTP_200_OK)
