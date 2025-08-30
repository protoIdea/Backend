from rest_framework import serializers
from .models import ChatMessage, ChatSession, ChatbotKnowledge, ChatbotAnalytics


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = '__all__'


class ChatSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSession
        fields = '__all__'


class ChatbotKnowledgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatbotKnowledge
        fields = '__all__'


class ChatbotAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatbotAnalytics
        fields = '__all__'
