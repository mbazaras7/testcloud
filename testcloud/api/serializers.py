from .models import *
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'email', 'full_name', 'date_of_birth']
        read_only_fields = ['user_id']

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
        #fields = ['id', 'user', 'amount', 'category', 'date', 'vendor', 'payment_method', 'created_at', 'updated_at']
        fields = ['id', 'amount', 'category', 'date', 'vendor', 'payment_method', 'created_at', 'updated_at']
        #read_only_fields = ['user', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

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
    class Meta:
        model = Receipt
        fields = ['id', 'image_url', 'merchant', 'total_amount','transaction_date', 'parsed_items', 'uploaded_at']


# Budget Serializer
class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = ['id', 'user', 'category', 'limit_amount', 'current_spending']
        read_only_fields = ['user', 'current_spending']

    def create(self, validated_data):
        user = self.context['request'].user  # Automatically associate the budget with the current user
        return Budget.objects.create(user=user, **validated_data)


# Notification Serializer
'''
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'type', 'message', 'sent_at', 'is_read']
        read_only_fields = ['user', 'sent_at']
'''