from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import ChatMessage, ChatSession, ChatbotKnowledge, ChatbotAnalytics
from .serializers import ChatMessageSerializer, ChatSessionSerializer, ChatbotKnowledgeSerializer, ChatbotAnalyticsSerializer

# Basic Django Views


class ChatSessionListView(ListView):
    model = ChatSession
    template_name = 'chatbot/session_list.html'


class ChatSessionDetailView(DetailView):
    model = ChatSession
    template_name = 'chatbot/session_detail.html'


class ChatSessionCreateView(CreateView):
    model = ChatSession
    template_name = 'chatbot/session_form.html'
    fields = '__all__'


class ChatSessionDeleteView(DeleteView):
    model = ChatSession
    template_name = 'chatbot/session_confirm_delete.html'
    success_url = '/chatbot/sessions/'

# Chat Messages


class ChatMessageListView(ListView):
    model = ChatMessage
    template_name = 'chatbot/message_list.html'


class ChatMessageDetailView(DetailView):
    model = ChatMessage
    template_name = 'chatbot/message_detail.html'


class ChatMessageCreateView(CreateView):
    model = ChatMessage
    template_name = 'chatbot/message_form.html'
    fields = '__all__'


class ChatMessageUpdateView(UpdateView):
    model = ChatMessage
    template_name = 'chatbot/message_form.html'
    fields = '__all__'

# Chatbot Knowledge


class ChatbotKnowledgeListView(ListView):
    model = ChatbotKnowledge
    template_name = 'chatbot/knowledge_list.html'


class ChatbotKnowledgeDetailView(DetailView):
    model = ChatbotKnowledge
    template_name = 'chatbot/knowledge_detail.html'


class ChatbotKnowledgeSearchView(ListView):
    model = ChatbotKnowledge
    template_name = 'chatbot/knowledge_search.html'

# Chatbot Analytics


class ChatbotAnalyticsListView(ListView):
    model = ChatbotAnalytics
    template_name = 'chatbot/analytics_list.html'


class ChatbotAnalyticsDetailView(DetailView):
    model = ChatbotAnalytics
    template_name = 'chatbot/analytics_detail.html'

# REST API Viewsets


class ChatSessionViewSet(viewsets.ModelViewSet):
    queryset = ChatSession.objects.all()
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]


class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]


class ChatbotKnowledgeViewSet(viewsets.ModelViewSet):
    queryset = ChatbotKnowledge.objects.all()
    serializer_class = ChatbotKnowledgeSerializer
    permission_classes = [IsAuthenticated]


class ChatbotAnalyticsViewSet(viewsets.ModelViewSet):
    queryset = ChatbotAnalytics.objects.all()
    serializer_class = ChatbotAnalyticsSerializer
    permission_classes = [IsAuthenticated]

