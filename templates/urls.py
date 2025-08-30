from django.urls import path
from . import views

app_name = 'templates'

urlpatterns = [
    # Template CRUD
    path('', views.BudgetTemplateListView.as_view(), name='template-list'),
    path('<int:pk>/', views.BudgetTemplateDetailView.as_view(),
         name='template-detail'),
    path('create/', views.BudgetTemplateCreateView.as_view(), name='template-create'),
    path('<int:pk>/update/', views.BudgetTemplateUpdateView.as_view(),
         name='template-update'),
    path('<int:pk>/delete/', views.BudgetTemplateDeleteView.as_view(),
         name='template-delete'),

    # Template Categories
    path('categories/', views.TemplateCategoryListView.as_view(),
         name='category-list'),
    path('categories/<int:pk>/',
         views.TemplateCategoryDetailView.as_view(), name='category-detail'),

    # Template Reviews
    path('reviews/', views.TemplateReviewListView.as_view(), name='review-list'),
    path('reviews/<int:pk>/', views.TemplateReviewDetailView.as_view(),
         name='review-detail'),

    # Template Usage
    path('usage/', views.TemplateUsageListView.as_view(), name='usage-list'),

    # Search and Filter
    path('search/', views.TemplateSearchView.as_view(), name='template-search'),
]

