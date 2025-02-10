from .models import *
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'date_of_birth']
        read_only_fields = ['id']

class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'full_name', 'date_of_birth', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data['full_name'],
            date_of_birth=validated_data['date_of_birth']
        )
        return user

# Transaction Serializer
class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'user', 'amount', 'category', 'date', 'description', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']


# Income Serializer
class IncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Income
        #fields = ['id', 'user', 'amount', 'category', 'date', 'source', 'created_at', 'updated_at']
        fields = ['id', 'amount', 'category', 'date', 'source', 'created_at', 'updated_at']

        #read_only_fields = ['user', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

'''
    def create(self, validated_data):
        user = self.context['request'].user  # Automatically associate the income with the current user
        return Income.objects.create(user=user, **validated_data)
'''

# Expense Serializer
class ExpenseSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Expense
        fields = ['id', 'user', 'amount', 'category', 'date', 'vendor', 'payment_method', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']

'''
    def create(self, validated_data):
        user = self.context['request'].user  # Automatically associate the expense with the current user
        return Expense.objects.create(user=user, **validated_data)
'''

# Receipt Serializer
'''
class ReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = ['id', 'transaction', 'image_url', 'raw_data', 'parsed_data']

    def create(self, validated_data):
        transaction = validated_data.get('transaction')
        receipt = Receipt.objects.create(transaction=transaction, **validated_data)
        return receipt
'''
class ReceiptSerializer(serializers.ModelSerializer):
    transaction_date = serializers.DateTimeField(format="%d-%m-%Y", required=False)  # Ensure it's a DateField
    uploaded_at = serializers.DateTimeField(format="%d-%m-%Y", required=False)

    class Meta:
        model = Receipt
        fields = ['id', 'user', 'image_url', 'merchant', 'total_amount','transaction_date', 'parsed_items', 'receipt_category', 'uploaded_at']
        extra_kwargs = {'user': {'read_only': True},'uploaded_at': {'read_only': True}}


# Budget Serializer
class BudgetSerializer(serializers.ModelSerializer):
    receipts = ReceiptSerializer(many=True, read_only=True)  # Show receipts under budget
    start_date = serializers.DateField(format="%d-%m-%Y")
    end_date = serializers.DateField(format="%d-%m-%Y")
    class Meta:
        model = Budget
        fields = ['id', 'user', 'category', 'limit_amount', 'current_spending', 'start_date', 'end_date', 'receipts']
        read_only_fields = ['current_spending']
        extra_kwargs = {'user': {'read_only': True}}
