from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication endpoints
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),

    # User profile and dashboard
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('dashboard/', views.UserDashboardView.as_view(), name='dashboard'),
    path('stats/', views.user_stats, name='user_stats'),

    # Password management
    path('change-password/', views.PasswordChangeView.as_view(),
         name='change_password'),
    path('reset-password/', views.PasswordResetView.as_view(), name='reset_password'),
    path('reset-password/confirm/', views.PasswordResetConfirmView.as_view(),
         name='reset_password_confirm'),

    # Notification preferences
    path('toggle-notifications/', views.toggle_notifications,
         name='toggle_notifications'),

    # Admin endpoints
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
]

