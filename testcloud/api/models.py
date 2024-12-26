from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager

# Create your models here.

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class User(AbstractUser):
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField('Email', unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()
    
class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50)
    date = models.DateField()
    type = models.CharField(max_length=7, choices=TRANSACTION_TYPES)
    source = models.CharField(max_length=20, default="manual")  # 'manual' or 'receipt'

    def __str__(self):
        return f"{self.type.capitalize()} of {self.amount} by {self.user}"
    
class Income(models.Model):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name="income_detail")
    source = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Income: {self.transaction.amount}"


class Expense(models.Model):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name="expense_detail")
    vendor = models.CharField(max_length=100, blank=True, null=True)
    payment_method = models.CharField(max_length=50, blank=True, null=True)  # e.g., Credit Card, Cash

    def __str__(self):
        return f"Expense: {self.transaction.amount}"
    
class Receipt(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name="receipt")
    image_url = models.URLField(max_length=500)  # Store uploaded receipt image URLs
    raw_data = models.TextField(blank=True, null=True)  # Store OCR-processed raw text data
    parsed_data = models.JSONField(blank=True, null=True)  # Parsed key-value pairs (e.g., total, vendor)

    def __str__(self):
        return f"Receipt for Transaction ID: {self.transaction.id}"


class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="budgets")
    category = models.CharField(max_length=50)
    limit_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_spending = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Budget for {self.category}: {self.limit_amount}"


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('anomaly', 'Anomaly Alert'),
        ('recommendation', 'Budget Recommendation'),
        ('prediction', 'Spending Prediction'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.type.capitalize()}"