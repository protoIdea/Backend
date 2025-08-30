from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Expense, ExpenseTemplate, ExpenseReminder
from .serializers import ExpenseSerializer, ExpenseTemplateSerializer, ExpenseReminderSerializer

# Basic Django Views


class ExpenseListView(ListView):
    model = Expense
    template_name = 'expenses/expense_list.html'


class ExpenseDetailView(DetailView):
    model = Expense
    template_name = 'expenses/expense_detail.html'


class ExpenseCreateView(CreateView):
    model = Expense
    template_name = 'expenses/expense_form.html'
    fields = '__all__'


class ExpenseUpdateView(UpdateView):
    model = Expense
    template_name = 'expenses/expense_form.html'
    fields = '__all__'


class ExpenseDeleteView(DeleteView):
    model = Expense
    template_name = 'expenses/expense_confirm_delete.html'
    success_url = '/expenses/'

# Expense Templates


class ExpenseTemplateListView(ListView):
    model = ExpenseTemplate
    template_name = 'expenses/template_list.html'


class ExpenseTemplateDetailView(DetailView):
    model = ExpenseTemplate
    template_name = 'expenses/template_detail.html'

# Expense Reminders


class ExpenseReminderListView(ListView):
    model = ExpenseReminder
    template_name = 'expenses/reminder_list.html'


class ExpenseReminderDetailView(DetailView):
    model = ExpenseReminder
    template_name = 'expenses/reminder_detail.html'

# Statistics and Reports


class ExpenseStatsView(ListView):
    model = Expense
    template_name = 'expenses/stats.html'


class ExpenseReportView(ListView):
    model = Expense
    template_name = 'expenses/reports.html'


class ExpenseFilterView(ListView):
    model = Expense
    template_name = 'expenses/filter.html'

# REST API Viewsets


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]


class ExpenseTemplateViewSet(viewsets.ModelViewSet):
    queryset = ExpenseTemplate.objects.all()
    serializer_class = ExpenseTemplateSerializer
    permission_classes = [IsAuthenticated]


class ExpenseReminderViewSet(viewsets.ModelViewSet):
    queryset = ExpenseReminder.objects.all()
    serializer_class = ExpenseReminderSerializer
    permission_classes = [IsAuthenticated]

