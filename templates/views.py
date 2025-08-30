from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import BudgetTemplate, TemplateCategory, TemplateReview, TemplateUsage
from .serializers import BudgetTemplateSerializer, TemplateCategorySerializer, TemplateReviewSerializer, TemplateUsageSerializer

# Basic Django Views


class BudgetTemplateListView(ListView):
    model = BudgetTemplate
    template_name = 'templates/template_list.html'


class BudgetTemplateDetailView(DetailView):
    model = BudgetTemplate
    template_name = 'templates/template_detail.html'


class BudgetTemplateCreateView(CreateView):
    model = BudgetTemplate
    template_name = 'templates/template_form.html'
    fields = '__all__'


class BudgetTemplateUpdateView(UpdateView):
    model = BudgetTemplate
    template_name = 'templates/template_form.html'
    fields = '__all__'


class BudgetTemplateDeleteView(DeleteView):
    model = BudgetTemplate
    template_name = 'templates/template_confirm_delete.html'
    success_url = '/templates/'

# Template Categories


class TemplateCategoryListView(ListView):
    model = TemplateCategory
    template_name = 'templates/category_list.html'


class TemplateCategoryDetailView(DetailView):
    model = TemplateCategory
    template_name = 'templates/category_detail.html'

# Template Reviews


class TemplateReviewListView(ListView):
    model = TemplateReview
    template_name = 'templates/review_list.html'


class TemplateReviewDetailView(DetailView):
    model = TemplateReview
    template_name = 'templates/review_detail.html'

# Template Usage


class TemplateUsageListView(ListView):
    model = TemplateUsage
    template_name = 'templates/usage_list.html'

# Search


class TemplateSearchView(ListView):
    model = BudgetTemplate
    template_name = 'templates/search.html'

# REST API Viewsets


class BudgetTemplateViewSet(viewsets.ModelViewSet):
    queryset = BudgetTemplate.objects.all()
    serializer_class = BudgetTemplateSerializer
    permission_classes = [IsAuthenticated]


class TemplateCategoryViewSet(viewsets.ModelViewSet):
    queryset = TemplateCategory.objects.all()
    serializer_class = TemplateCategorySerializer
    permission_classes = [IsAuthenticated]


class TemplateReviewViewSet(viewsets.ModelViewSet):
    queryset = TemplateReview.objects.all()
    serializer_class = TemplateReviewSerializer
    permission_classes = [IsAuthenticated]


class TemplateUsageViewSet(viewsets.ModelViewSet):
    queryset = TemplateUsage.objects.all()
    serializer_class = TemplateUsageSerializer
    permission_classes = [IsAuthenticated]

