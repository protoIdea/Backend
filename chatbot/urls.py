from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    # Chat Sessions
    path('sessions/', views.ChatSessionListView.as_view(), name='session-list'),
    path('sessions/<int:pk>/', views.ChatSessionDetailView.as_view(),
         name='session-detail'),
    path('sessions/create/', views.ChatSessionCreateView.as_view(),
         name='session-create'),
    path('sessions/<int:pk>/delete/',
         views.ChatSessionDeleteView.as_view(), name='session-delete'),

    # Chat Messages
    path('sessions/<int:session_id>/messages/',
         views.ChatMessageListView.as_view(), name='message-list'),
    path('sessions/<int:session_id>/messages/create/',
         views.ChatMessageCreateView.as_view(), name='message-create'),
    path('messages/<int:pk>/', views.ChatMessageDetailView.as_view(),
         name='message-detail'),
    path('messages/<int:pk>/update/',
         views.ChatMessageUpdateView.as_view(), name='message-update'),

    # Chatbot Knowledge
    path('knowledge/', views.ChatbotKnowledgeListView.as_view(),
         name='knowledge-list'),
    path('knowledge/<int:pk>/', views.ChatbotKnowledgeDetailView.as_view(),
         name='knowledge-detail'),
    path('knowledge/search/', views.ChatbotKnowledgeSearchView.as_view(),
         name='knowledge-search'),

    # Chatbot Analytics
    path('analytics/', views.ChatbotAnalyticsListView.as_view(),
         name='analytics-list'),
    path('analytics/<int:pk>/', views.ChatbotAnalyticsDetailView.as_view(),
         name='analytics-detail'),
]

