from django.urls import path, include
from rest_framework import routers
from api import views
from .views import *
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

router = routers.DefaultRouter()
router.register('users', UserViewSet, basename='users')
#router.register('transactions', TransactionViewSet, basename='transactions')
router.register('incomes', IncomeViewSet, basename='incomes')
router.register('expenses', ExpenseViewSet, basename='expenses')
#router.register('receipts', ReceiptViewSet, basename='receipts')
router.register('budgets', BudgetViewSet, basename='budgets')
#router.register('notifications', NotificationViewSet, basename='notifications')


urlpatterns = [
    path('api/', include(router.urls)),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]