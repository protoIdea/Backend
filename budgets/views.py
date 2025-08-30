from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Budget, BudgetCategory, BudgetTemplate, BudgetAlert
from .serializers import BudgetSerializer, BudgetCategorySerializer, BudgetTemplateSerializer, BudgetAlertSerializer

# Basic Django Views (for admin interface)


class BudgetListView(ListView):
    model = Budget
    template_name = 'budgets/budget_list.html'
    context_object_name = 'budgets'


class BudgetDetailView(DetailView):
    model = Budget
    template_name = 'budgets/budget_detail.html'


class BudgetCreateView(CreateView):
    model = Budget
    template_name = 'budgets/budget_form.html'
    fields = '__all__'


class BudgetUpdateView(UpdateView):
    model = Budget
    template_name = 'budgets/budget_form.html'
    fields = '__all__'


class BudgetDeleteView(DeleteView):
    model = Budget
    template_name = 'budgets/budget_confirm_delete.html'
    success_url = '/budgets/'

# Budget Categories


class BudgetCategoryListView(ListView):
    model = BudgetCategory
    template_name = 'budgets/category_list.html'


class BudgetCategoryDetailView(DetailView):
    model = BudgetCategory
    template_name = 'budgets/category_detail.html'


class BudgetCategoryCreateView(CreateView):
    model = BudgetCategory
    template_name = 'budgets/category_form.html'
    fields = '__all__'

# Budget Templates


class BudgetTemplateListView(ListView):
    model = BudgetTemplate
    template_name = 'budgets/template_list.html'


class BudgetTemplateDetailView(DetailView):
    model = BudgetTemplate
    template_name = 'budgets/template_detail.html'

# Budget Alerts


class BudgetAlertListView(ListView):
    model = BudgetAlert
    template_name = 'budgets/alert_list.html'


class BudgetAlertDetailView(DetailView):
    model = BudgetAlert
    template_name = 'budgets/alert_detail.html'

# Statistics and Reports


class BudgetStatsView(ListView):
    model = Budget
    template_name = 'budgets/stats.html'


class BudgetReportView(ListView):
    model = Budget
    template_name = 'budgets/reports.html'

# REST API Viewsets


class BudgetViewSet(viewsets.ModelViewSet):
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]


class BudgetCategoryViewSet(viewsets.ModelViewSet):
    queryset = BudgetCategory.objects.all()
    serializer_class = BudgetCategorySerializer
    permission_classes = [IsAuthenticated]


class BudgetTemplateViewSet(viewsets.ModelViewSet):
    queryset = BudgetTemplate.objects.all()
    serializer_class = BudgetTemplateSerializer
    permission_classes = [IsAuthenticated]


class BudgetAlertViewSet(viewsets.ModelViewSet):
    queryset = BudgetAlert.objects.all()
    serializer_class = BudgetAlertSerializer
    permission_classes = [IsAuthenticated]

