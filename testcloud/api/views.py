from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence.models import AnalyzeResult, AnalyzeDocumentRequest
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from django.http import HttpResponse
from datetime import datetime, timedelta
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.shortcuts import render
from rest_framework import viewsets, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Income, Expense, Budget, Receipt, User
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
from django.contrib.auth import get_user_model, authenticate    
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import BasePermission, AllowAny
from PIL import Image
import os
import io
from io import BytesIO
import time

User = get_user_model()

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

def generate_filename(filename):
    timestamp = int(time.time())  # Get current timestamp
    extension = filename.split('.')[-1]  # Extract file extension
    return f"{timestamp}.{extension}"  # Return unique filename

class ProcessReceiptView(APIView):
    
    def post(self, request, *args, **kwargs):
        #receiptUrl = request.data.get('image_url')
        uploaded_file = request.FILES.get('image')
        #blob_name = f"receipt_{uuid.uuid4().hex}.jpg"
        blob_name = generate_filename(uploaded_file.name)
        
        receiptUrl = upload_image_to_azure(uploaded_file, blob_name)
        endpoint = os.environ["DOCUMENTINTELLIGENCE_ENDPOINT"]
        key = os.environ["DOCUMENTINTELLIGENCE_API_KEY"]
    
        document_intelligence_client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))
        print(receiptUrl)
        if receiptUrl:
            # Process URL
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
                    receipt_category = receipt.fields.get("ReceiptType")
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
                                "value": str(item_total_price.get("valueCurrency").get("amount")),
                                }
                            #Later when have time, add each item to expense aswell
                            Expense.objects.create(
                                amount=item_total_price.get("valueCurrency").get("amount"),
                                category=receipt_category.get('valueString') if receipt_category else None,
                                date=transaction_date_field.get("valueDate") if transaction_date_field else None,
                                vendor=merchant_name.get('valueString') if merchant_name else "Unknown Merchant",
                                payment_method=None,
                            )
                            receipt_items.append(item_details)

                        
                    
        receipt = Receipt.objects.create(image_url=receiptUrl if receiptUrl else None,
                                         merchant=merchant_name.get('valueString') if merchant_name else "Unknown Merchant",
                                         total_amount=_format_price(total.get('valueCurrency')) if total else "0.00",
                                         parsed_items=receipt_items,
                                         transaction_date=transaction_date_field.get("valueDate") if transaction_date_field else None,
                                         receipt_category=receipt_category.get('valueString') if receipt_category else None,
                                         )
        serializer = ReceiptSerializer(receipt)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
def upload_image_to_azure(image_file, blob_name):
    """Uploads an image to Azure Blob Storage and returns the URL."""
    
    AZURE_STORAGE_ACCOUNT_NAME = os.environ["AZURE_STORAGE_ACCOUNT_NAME"]
    AZURE_STORAGE_ACCOUNT_KEY = os.environ["AZURE_STORAGE_ACCOUNT_KEY"]
    AZURE_CONTAINER_NAME = os.environ["AZURE_CONTAINER_NAME"]

    compressed_image = compress_image(image_file)
    # Connect to Azure Blob Storage
    
    blob_service_client = BlobServiceClient(
        f'https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net',
        credential=AZURE_STORAGE_ACCOUNT_KEY
    )

    blob_client = blob_service_client.get_blob_client(container=AZURE_CONTAINER_NAME, blob=blob_name)
    blob_client.set_http_headers(content_settings={"content_type": "image/png"})
    # Upload Image
    blob_client.upload_blob(compressed_image, overwrite=True)

    # Generate SAS URL with expiration time (e.g., 1 hour)
    sas_token = generate_blob_sas(
        account_name=AZURE_STORAGE_ACCOUNT_NAME,
        container_name=AZURE_CONTAINER_NAME,
        blob_name=blob_name,
        account_key=AZURE_STORAGE_ACCOUNT_KEY,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(days=365 * 100)  # URL expires in 1 hour
    )

    sas_url = f"{blob_client.url}?{sas_token}"
    print("Generated SAS URL:", sas_url)  # Debugging

    return sas_url
    
class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        # Get email and password from request data
        email = request.data.get('email')
        password = request.data.get('password')

        # Authenticate the user
        user = authenticate(email=email, password=password)

        if user:
            # Generate JWT token
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'full_name': user.full_name,
                }
            }, status=status.HTTP_200_OK)

        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

def compress_image(image_file):
    """Compress the image to reduce file size before uploading."""
    img = Image.open(image_file)

    # Convert to JPEG (reduces file size)
    img = img.convert("RGB")

    # Save to buffer with compression
    img_io = BytesIO()
    img.save(img_io, format="JPEG", quality=70)  # Adjust quality (70-80 is good)
    img_io.seek(0)

    return img_io
        

            