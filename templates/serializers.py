from rest_framework import serializers
from .models import BudgetTemplate, TemplateCategory, TemplateReview, TemplateUsage

class BudgetTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetTemplate
        fields = '__all__'

class TemplateCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateCategory
        fields = '__all__'

class TemplateReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateReview
        fields = '__all__'

class TemplateUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateUsage
        fields = '__all__'
