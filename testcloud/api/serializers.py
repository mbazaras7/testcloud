from .models import *
from rest_framework import serializers

# Transaction Serializer
class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'user', 'amount', 'category', 'date', 'type', 'source']
        read_only_fields = ['user']


# Income Serializer
class IncomeSerializer(serializers.ModelSerializer):
    transaction = TransactionSerializer()

    class Meta:
        model = Income
        fields = ['id', 'transaction', 'source']

    def create(self, validated_data):
        transaction_data = validated_data.pop('transaction')
        transaction = Transaction.objects.create(**transaction_data)
        income = Income.objects.create(transaction=transaction, **validated_data)
        return income


# Expense Serializer
class ExpenseSerializer(serializers.ModelSerializer):
    transaction = TransactionSerializer()

    class Meta:
        model = Expense
        fields = ['id', 'transaction', 'vendor', 'payment_method']

    def create(self, validated_data):
        transaction_data = validated_data.pop('transaction')
        transaction = Transaction.objects.create(**transaction_data)
        expense = Expense.objects.create(transaction=transaction, **validated_data)
        return expense


# Receipt Serializer
class ReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = ['id', 'transaction', 'image_url', 'raw_data', 'parsed_data']

    def create(self, validated_data):
        transaction = validated_data.get('transaction')
        receipt = Receipt.objects.create(transaction=transaction, **validated_data)
        return receipt


# Budget Serializer
class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = ['id', 'user', 'category', 'limit_amount', 'current_spending']
        read_only_fields = ['user', 'current_spending']

    def create(self, validated_data):
        budget = Budget.objects.create(**validated_data)
        return budget


# Notification Serializer
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'type', 'message', 'sent_at', 'is_read']
        read_only_fields = ['user', 'sent_at']