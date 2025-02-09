from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, FloatField, Q
from django.db.models.functions import Cast
from django.utils.timezone import now


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
    username = None
    id = models.AutoField(primary_key=True)
    email = models.EmailField('Email Address', unique=True, db_index=True)
    full_name = models.CharField(max_length=150, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name','date_of_birth']
    objects = UserManager()
    
    def __str__(self):
        return self.email
    
class Transaction(models.Model):

    #user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="%(class)ss", verbose_name=_("User"))
    #user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="%(class)ss", verbose_name=_("User"), null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Amount"), help_text=_("Enter the transaction amount."))
    category = models.CharField(max_length=50,verbose_name=_("Category"),help_text=_("Specify the category of the transaction")) # going to need to add list of categories
    date = models.DateField(blank=True, null=True, verbose_name=_("Transaction Date"),help_text=_("The date of the transaction."))
    created_at = models.DateTimeField(auto_now_add=True,verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True,verbose_name=_("Updated At"))
    
    class Meta:
        abstract = True
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.amount} - {self.category}"
    
class Income(Transaction):
    source = models.CharField(max_length=100,verbose_name=_("Income Source"),help_text=_("The source of the income, e.g., salary, investment, etc."))
    
    class Meta:
        verbose_name = _("Income")
        verbose_name_plural = _("Incomes")

class CategoryChoices(models.TextChoices):
    MEAL = "Meal", _("Meal")
    SUPPLIES = "Supplies", _("Supplies")
    HOTEL = "Hotel", _("Hotel")
    FUEL_ENERGY = "Fuel & Energy", _("Fuel & Energy")
    TRANSPORTATION = "Transportation", _("Transportation")
    COMMUNICATION_SUBSCRIPTIONS = "Communication & Subscriptions", _("Communication & Subscriptions")
    ENTERTAINMENT = "Entertainment", _("Entertainment")
    TRAINING = "Training", _("Training")
    HEALTHCARE = "Healthcare", _("Healthcare")
    OTHER = "Other", _("Other")

class Expense(Transaction):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="expenses")
    category = models.CharField(max_length=50,choices=CategoryChoices.choices,default=CategoryChoices.OTHER,verbose_name=_("Category"),help_text=_("Select the category of the expense."),)
    vendor = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Vendor"),help_text=_("The vendor or merchant associated with the expense."))
    payment_method = models.CharField(max_length=50,blank=True,null=True,verbose_name=_("Payment Method"),help_text=_("Payment method used for the expense, e.g., credit card, cash."))
    class Meta:
        verbose_name = _("Expense")
        verbose_name_plural = _("Expenses")

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="budgets")
    name = models.CharField(max_length=255, null=True, blank=True, default="Budget")
    category = models.CharField(max_length=255, null=True, blank=True)  # Budget category
    limit_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Budget limit
    current_spending = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Total spent
    start_date = models.DateField()  # Start of budget period
    end_date = models.DateField()  # End of budget period
    created_at = models.DateTimeField(auto_now_add=True)

    def update_spending(self):
        """ Update current spending based on linked receipts' total amounts. """
        total_spent = (
            Receipt.objects.filter(
                Q(transaction_date__range=[self.start_date, self.end_date]) |  # Use transaction_date if available
                Q(transaction_date__isnull=True, uploaded_at__range=[self.start_date, self.end_date]),  # Otherwise, use uploaded_at
                user=self.user,
            )
            .exclude(total_amount=None)
            .annotate(total_as_float=Cast("total_amount", FloatField()))
            .aggregate(total=Sum("total_as_float"))["total"] or 0
        )
        self.current_spending = total_spent
        self.save()

    class Meta:
        verbose_name = _("Budget")
        verbose_name_plural = _("Budgets")


class Receipt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receipts")
    image_url = models.URLField(max_length=500, verbose_name=_("Image URL"), blank=True, null=True)  # Store uploaded receipt image URLs
    budget = models.ForeignKey(Budget, on_delete=models.SET_NULL, null=True, blank=True, related_name='receipts')  # Link to budget
    merchant = models.CharField(max_length=100, verbose_name=_("Merchant"), blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Total"), blank=True, null=True)
    uploaded_at = models.DateTimeField(default=now)
    parsed_items = models.JSONField(blank=True, null=True, verbose_name=_("Parsed Items"))  # Store parsed item details (list of dictionaries)
    transaction_date = models.DateTimeField(blank=True, null=True, verbose_name=_("Transaction Date")) 
    receipt_category = models.CharField(max_length=50,choices=CategoryChoices.choices,default=CategoryChoices.OTHER,verbose_name=_("Category"),help_text=_("Select the category of the receipt."),)
    
    def __str__(self):
        return f"Receipt from {self.merchant or 'Unknown Merchant'} uploaded on {self.uploaded_at}"
    
    def assign_to_budget(self):
        """ Automatically assigns the receipt to the correct budget if applicable. """
        active_budget = Budget.objects.filter(user=self.user,start_date__lte=self.transaction_date if self.transaction_date else self.uploaded_at,end_date__gte=self.transaction_date if self.transaction_date else self.uploaded_at).first()
        if active_budget:
            self.budget = active_budget
            self.save()
            active_budget.update_spending()
    
    def determine_category(parsed_category):
        """Assigns a category based on parsed data."""
        category_map = {c.label.lower(): c.value for c in CategoryChoices}
        return category_map.get(parsed_category.lower(), CategoryChoices.OTHER)
