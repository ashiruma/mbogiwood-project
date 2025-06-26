# File: payments/views.py

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .models import Payment
import uuid

class InitiateMpesaPaymentView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user
        amount = 500
        phone_number = request.data.get('phone_number')
        if not phone_number:
            return Response({"detail": "Phone number is required."}, status=status.HTTP_400_BAD_REQUEST)
        checkout_request_id = f"ws_CO_{uuid.uuid4().hex}" 
        response_code = "0"
        if response_code == "0":
            Payment.objects.create(
                user=user, provider=Payment.Provider.MPESA, status=Payment.Status.PENDING,
                amount=amount, provider_reference=checkout_request_id, metadata={'phone_number': phone_number}
            )
            return Response({"detail": "STK Push initiated."}, status=status.HTTP_200_OK)
        return Response({"detail": "Failed to initiate M-Pesa payment."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DarajaCallbackView(APIView):
    def post(self, request):
        data = request.data
        result_code = data.get('ResultCode')
        checkout_request_id = data.get('CheckoutRequestID')
        try:
            with transaction.atomic():
                payment = Payment.objects.select_for_update().get(provider_reference=checkout_request_id)
                if payment.status == Payment.Status.COMPLETED:
                    return Response(status=status.HTTP_200_OK)
                if result_code == 0:
                    callback_metadata = data.get('CallbackMetadata', {})
                    paid_amount = self.extract_amount(callback_metadata)
                    if paid_amount != payment.amount:
                        payment.status = Payment.Status.FAILED
                        payment.metadata['failure_reason'] = f"Amount mismatch. Expected {payment.amount}, got {paid_amount}."
                        payment.save()
                        return Response(status=status.HTTP_400_BAD_REQUEST)
                    payment.status = Payment.Status.COMPLETED
                    payment.metadata['mpesa_receipt'] = self.extract_receipt(callback_metadata)
                    payment.save()
                else:
                    payment.status = Payment.Status.FAILED
                    payment.metadata['failure_reason'] = data.get('ResultDesc', 'Unknown failure.')
                    payment.save()
        except Payment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_200_OK)
    def extract_amount(self, metadata):
        items = metadata.get('Item', [])
        for item in items:
            if item.get('Name') == 'Amount': return item.get('Value')
        return None
    def extract_receipt(self, metadata):
        items = metadata.get('Item', [])
        for item in items:
            if item.get('Name') == 'MpesaReceiptNumber': return item.get('Value')
        return None
