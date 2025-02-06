from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Expense, Receipt, Budget
from datetime import date

User = get_user_model()

class UserTests(TestCase):
    def setUp(self):
        """Create a test user."""
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
            full_name="Test User",
            date_of_birth="2000-01-01"
        )
        self.client = APIClient()

    def test_user_creation(self):
        """Ensure user is created successfully."""
        self.assertEqual(self.user.email, "testuser@example.com")

    def test_user_login(self):
        """Ensure user can log in and receive JWT token."""
        response = self.client.post('/api/login/', {
            'email': 'testuser@example.com',
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

class ExpenseTests(TestCase):
    def setUp(self):
        """Create a test user and an expense."""
        self.user = User.objects.create_user(email="user@example.com", password="password123")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)  # Authenticate user
        
        self.expense = Expense.objects.create(
            user=self.user,
            amount=50.00,
            category="Groceries",
            date=date.today(),
            vendor="Walmart",
            payment_method="Credit Card"
        )

    def test_create_expense(self):
        """Ensure an expense can be created via API."""
        response = self.client.post('/api/expenses/', {
            'amount': 20.00,
            'category': "Transport",
            'date': str(date.today()),
            'vendor': "Uber",
            'payment_method': "Cash"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_expenses(self):
        """Ensure expenses are listed for the authenticated user."""
        response = self.client.get('/api/expenses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

class BudgetTests(TestCase):
    def setUp(self):
        """Create a test user and a budget."""
        self.user = User.objects.create_user(email="budgetuser@example.com", password="securepassword")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.budget = Budget.objects.create(
            user=self.user,
            name="Monthly Budget",
            category="Groceries",
            limit_amount=500.00,
            start_date="2024-02-01",
            end_date="2024-02-28"
        )

    def test_create_budget(self):
        """Ensure a budget can be created via API."""
        response = self.client.post('/api/budgets/', {
            'name': "Test Budget",
            'category': "Entertainment",
            'limit_amount': 100.00,
            'start_date': "2024-02-01",
            'end_date': "2024-02-28"
        })
        print("Response Data (Budget):", response.data)  # Debugging
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_budgets(self):
        """Ensure only the authenticated user's budgets are listed."""
        response = self.client.get('/api/budgets/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

class ReceiptTests(TestCase):
    def setUp(self):
        """Create a test user and a receipt."""
        self.user = User.objects.create_user(email="receiptuser@example.com", password="securepass")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.receipt = Receipt.objects.create(
            user=self.user,
            image_url="http://example.com/receipt.jpg",
            merchant="McDonald's",
            total_amount=15.99,
            transaction_date="2024-02-01",
            receipt_category="Food",
        )

    def test_create_receipt(self):
        """Ensure a receipt can be created via API."""
        response = self.client.post('/api/receipts/', {
            'image_url': "http://example.com/new_receipt.jpg",
            'merchant': "Starbucks",
            'total_amount': 5.99,
            'transaction_date': "2024-02-02",
            'receipt_category': "Drinks"
        })
        print("Response Data (Receipt):", response.data)  # Debugging
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_receipts(self):
        """Ensure only the authenticated user's receipts are listed."""
        response = self.client.get('/api/receipts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

'''
figure out a way to test this mabye add url functionality for ease of use in processviewset
class ProcessReceiptTests(TestCase):
    def setUp(self):
        """Create a test user for testing receipt processing."""
        self.user = User.objects.create_user(email="processuser@example.com", password="processingpass")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_process_receipt(self):
        """Ensure the receipt processing API works (mocked response)."""
        response = self.client.post('/api/process-receipt/', {
            'image_url': "http://example.com/sample_receipt.jpg"
        })
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
'''