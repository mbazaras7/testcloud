
# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Transaction, Income, Expense, Receipt, Budget, Notification
from .serializers import (
    TransactionSerializer,
    IncomeSerializer,
    ExpenseSerializer,
    ReceiptSerializer,
    BudgetSerializer,
    NotificationSerializer,
)
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters


# Create your views here.


# Transaction ViewSet
class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ['user', 'type', 'category', 'date']

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# Income ViewSet
class IncomeViewSet(viewsets.ModelViewSet):
    serializer_class = IncomeSerializer
    queryset = Income.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ['transaction', 'transaction__category']

    def get_queryset(self):
        return Income.objects.filter(transaction__user=self.request.user)


# Expense ViewSet
class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    queryset = Expense.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ['transaction', 'transaction__category', 'vendor']

    def get_queryset(self):
        return Expense.objects.filter(transaction__user=self.request.user)


# Receipt ViewSet
class ReceiptViewSet(viewsets.ModelViewSet):
    serializer_class = ReceiptSerializer
    queryset = Receipt.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ['transaction']

    def get_queryset(self):
        return Receipt.objects.filter(transaction__user=self.request.user)


# Budget ViewSet
class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    queryset = Budget.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ['user', 'category']

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# Notification ViewSet
class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ['user', 'type', 'is_read']

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        notification = serializer.save()
        notification.is_read = True
        notification.save()