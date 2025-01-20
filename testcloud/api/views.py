from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence.models import AnalyzeResult, AnalyzeDocumentRequest
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import viewsets, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Income, Expense, Budget, Receipt
from .serializers import (
    #TransactionSerializer,
    IncomeSerializer,
    ExpenseSerializer,
    ReceiptSerializer,
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
import os


User = get_user_model()

'''
class AllowDummyToken(BasePermission):
    def has_permission(self, request, view):
        return request.headers.get('Authorization') == f"Bearer test-token" #delete later in development
'''

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
    permission_classes = [AllowAny]

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
#class IncomeViewSet(UserScopedViewSet):
class IncomeViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny] # delete later in development 
    serializer_class = IncomeSerializer
    queryset = Income.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ['category', 'date', 'source']
    
    def perform_create(self, serializer):

        #serializer.save(user=self.request.user)
        serializer.save()


# Expense ViewSet
#class ExpenseViewSet(UserScopedViewSet):c
class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    queryset = Expense.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ['category', 'date', 'vendor', 'payment_method']
    
    def perform_create(self, serializer):

        #serializer.save(user=self.request.user)
        serializer.save()


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
def _format_price(price_dict):
    if price_dict is None:
        return "N/A"
    return "".join([f"{p}" for p in price_dict.values()])

class ReceiptViewSet(viewsets.ModelViewSet):
    serializer_class = ReceiptSerializer
    queryset = Receipt.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ['id','merchant']
    
    def perform_create(self, serializer):

        serializer.save()

class ProcessReceiptView(APIView):

    def post(self, request, *args, **kwargs):
        receiptUrl = request.data.get('image_url')
        if not receiptUrl:
            return Response({"error": "Image URL is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        endpoint = os.environ["DOCUMENTINTELLIGENCE_ENDPOINT"]
        key = os.environ["DOCUMENTINTELLIGENCE_API_KEY"]
        
        document_intelligence_client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))
        
        poller = document_intelligence_client.begin_analyze_document(
        "prebuilt-receipt",
        AnalyzeDocumentRequest(url_source=receiptUrl)
        )       

        receipts: AnalyzeResult = poller.result()
        
        if receipts.documents:
            for idx, receipt in enumerate(receipts.documents):
                if receipt.fields:
                    merchant_name = receipt.fields.get("MerchantName")
                    total = receipt.fields.get("Total")
                    items = receipt.fields.get("Items")
                    transaction_date_field = receipt.fields.get("TransactionDate")
                    if items:
                        receipt_items = []
                        for idx, item in enumerate(items.get("valueArray")):
                            item_details = {}
                            item_description = item.get("valueObject").get("Description")
                            if item_description:
                                item_details["description"] = {
                                "value": item_description.get("valueString"),
                                }

                            item_quantity = item.get("valueObject").get("Quantity")
                            if item_quantity:
                                item_details["quantity"] = {
                                "value": item_quantity.get("valueString"),
                                }

                            item_total_price = item.get("valueObject").get("TotalPrice")
                            if item_total_price:
                                item_details["total_price"] = {
                                "value": str(item_total_price.get("valueCurrency")),
                                }

                            receipt_items.append(item_details)

                        
                    
        receipt = Receipt.objects.create(image_url=receiptUrl,
                                         merchant=merchant_name.get('valueString') if merchant_name else "Unknown Merchant",
                                         total_amount=_format_price(total.get('valueCurrency')) if total else "0.00",
                                         parsed_items=receipt_items,
                                         transaction_date=transaction_date_field.get("valueDate") if transaction_date_field else None
                                         )
        serializer = ReceiptSerializer(receipt)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

        

            