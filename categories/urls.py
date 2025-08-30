from django.urls import path
from . import views

app_name = 'categories'

urlpatterns = [
    # Category CRUD operations
    path('', views.CategoryListView.as_view(), name='category_list'),
    path('<int:pk>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('bulk-update/', views.CategoryBulkUpdateView.as_view(),
         name='category_bulk_update'),

    # Category statistics and reports
    path('stats/', views.CategoryStatsView.as_view(), name='category_stats'),
    path('usage-report/', views.CategoryUsageReportView.as_view(),
         name='category_usage_report'),

    # Category management
    path('create-defaults/', views.create_default_categories,
         name='create_default_categories'),
    path('suggestions/', views.category_suggestions, name='category_suggestions'),
    path('<int:pk>/duplicate/', views.duplicate_category,
         name='duplicate_category'),

    # Category groups
    path('groups/', views.CategoryGroupListView.as_view(),
         name='category_group_list'),
    path('groups/<int:pk>/', views.CategoryGroupDetailView.as_view(),
         name='category_group_detail'),
]

