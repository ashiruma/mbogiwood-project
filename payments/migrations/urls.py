from django.urls import path
from .views import InitiateMpesaPaymentView, DarajaCallbackView

app_name = 'payments'

urlpatterns = [
    # e.g., /api/v1/payments/initiate-mpesa/
    path('initiate-mpesa/', InitiateMpesaPaymentView.as_view(), name='initiate-mpesa'),
    
    # This is the URL you provide to Safaricom in your Daraja app setup
    # e.g., https://www.yourdomain.com/api/v1/payments/daraja-callback/
    path('daraja-callback/', DarajaCallbackView.as_view(), name='daraja-callback'),
]
