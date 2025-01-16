from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import viewsets, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Income, Expense, Budget
from .serializers import (
    #TransactionSerializer,
    IncomeSerializer,
    ExpenseSerializer,
    #ReceiptSerializer,
    BudgetSerializer,
    #NotificationSerializer,
    UserSerializer,
    UserCreateSerializer
)
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework.permissions import BasePermission, AllowAny


User = get_user_model()


class AllowDummyToken(BasePermission):
    def has_permission(self, request, view):
        return request.headers.get('Authorization') == f"Bearer test-token" #delete later in development

class UserViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for retrieving and creating users.
    """
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def perform_create(self, serializer):
        """
        Save the user instance.
        """
        serializer.save()
        
class UserScopedViewSet(viewsets.ModelViewSet):
    """
    A base ViewSet to restrict queryset to the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Limit queryset to objects belonging to the authenticated user.
        """
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Automatically associate the authenticated user with the created object.
        """
        serializer.save(user=self.request.user)

# Transaction ViewSet
'''
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
'''

# Income ViewSet
class IncomeViewSet(UserScopedViewSet):
    permission_classes = [AllowAny] # delete later in development 
    serializer_class = IncomeSerializer
    queryset = Income.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ['category', 'date', 'source']


# Expense ViewSet
class ExpenseViewSet(UserScopedViewSet):
    serializer_class = ExpenseSerializer
    queryset = Expense.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ['category', 'date', 'vendor', 'payment_method']


# Receipt ViewSet
'''
class ReceiptViewSet(viewsets.ModelViewSet):
    serializer_class = ReceiptSerializer
    queryset = Receipt.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ['transaction']

    def get_queryset(self):
        return Receipt.objects.filter(transaction__user=self.request.user)
'''

# Budget ViewSet
class BudgetViewSet(UserScopedViewSet):
    serializer_class = BudgetSerializer
    queryset = Budget.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ['category']

    def perform_create(self, serializer):
        """
        Ensure that `current_spending` is initialized to zero upon creation.
        """
        serializer.save(user=self.request.user, current_spending=0)

# Notification ViewSet
'''
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
'''