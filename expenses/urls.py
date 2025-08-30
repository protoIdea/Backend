from django.urls import path
from . import views

app_name = 'expenses'

urlpatterns = [
    # Expense CRUD
    path('', views.ExpenseListView.as_view(), name='expense-list'),
    path('<int:pk>/', views.ExpenseDetailView.as_view(), name='expense-detail'),
    path('create/', views.ExpenseCreateView.as_view(), name='expense-create'),
    path('<int:pk>/update/', views.ExpenseUpdateView.as_view(),
         name='expense-update'),
    path('<int:pk>/delete/', views.ExpenseDeleteView.as_view(),
         name='expense-delete'),

    # Expense Templates
    path('templates/', views.ExpenseTemplateListView.as_view(), name='template-list'),
    path('templates/<int:pk>/', views.ExpenseTemplateDetailView.as_view(),
         name='template-detail'),

    # Expense Reminders
    path('reminders/', views.ExpenseReminderListView.as_view(), name='reminder-list'),
    path('reminders/<int:pk>/', views.ExpenseReminderDetailView.as_view(),
         name='reminder-detail'),

    # Statistics and Reports
    path('stats/', views.ExpenseStatsView.as_view(), name='expense-stats'),
    path('reports/', views.ExpenseReportView.as_view(), name='expense-reports'),
    path('filter/', views.ExpenseFilterView.as_view(), name='expense-filter'),
]

