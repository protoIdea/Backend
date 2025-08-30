from rest_framework import serializers
from .models import Budget, BudgetCategory, BudgetTemplate, BudgetAlert

class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = '__all__'

class BudgetCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetCategory
        fields = '__all__'

class BudgetTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetTemplate
        fields = '__all__'

class BudgetAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetAlert
        fields = '__all__'
