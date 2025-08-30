from django.urls import path
from . import views

app_name = 'budgets'

urlpatterns = [
    # Budget CRUD
    path('', views.BudgetListView.as_view(), name='budget-list'),
    path('<int:pk>/', views.BudgetDetailView.as_view(), name='budget-detail'),
    path('create/', views.BudgetCreateView.as_view(), name='budget-create'),
    path('<int:pk>/update/', views.BudgetUpdateView.as_view(), name='budget-update'),
    path('<int:pk>/delete/', views.BudgetDeleteView.as_view(), name='budget-delete'),

    # Budget Categories
    path('categories/', views.BudgetCategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/', views.BudgetCategoryDetailView.as_view(),
         name='category-detail'),
    path('categories/create/', views.BudgetCategoryCreateView.as_view(),
         name='category-create'),

    # Budget Templates
    path('templates/', views.BudgetTemplateListView.as_view(), name='template-list'),
    path('templates/<int:pk>/', views.BudgetTemplateDetailView.as_view(),
         name='template-detail'),

    # Budget Alerts
    path('alerts/', views.BudgetAlertListView.as_view(), name='alert-list'),
    path('alerts/<int:pk>/', views.BudgetAlertDetailView.as_view(),
         name='alert-detail'),

    # Statistics and Reports
    path('stats/', views.BudgetStatsView.as_view(), name='budget-stats'),
    path('reports/', views.BudgetReportView.as_view(), name='budget-reports'),
]

