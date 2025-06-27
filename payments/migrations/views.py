from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .models import Payment
import uuid

class InitiateMpesaPaymentView(APIView):
    """
    An endpoint for a logged-in user to start a subscription payment.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        amount = 500  # Based on our "Simple Choice" pricing model
        phone_number = request.data.get('phone_number')

        if not phone_number:
            return Response({"detail": "Phone number is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # --- This is a placeholder for your Daraja API client ---
        # In a real app, you would import a service that handles the complexity
        # of authenticating with Daraja and making the STK push request.
        # daraja_service = DarajaService()
        # success, response = daraja_service.stk_push(amount, phone_number, ...)
        
        # We will simulate a successful response from Daraja
        success = True
        response = {
            "CheckoutRequestID": f"ws_CO_{uuid.uuid4().hex}",
            "ResponseCode": "0",
            "ResponseDescription": "Success. The request is successfully received.",
        }
        # ---------------------------------------------------------

        if success:
            checkout_request_id = response['CheckoutRequestID']
            
            # Create a local payment record to track this transaction attempt
            Payment.objects.create(
                user=user,
                provider=Payment.Provider.MPESA,
                status=Payment.Status.PENDING,
                amount=amount,
                provider_reference=checkout_request_id,
                metadata={'phone_number': phone_number}
            )
            return Response({"detail": "STK Push initiated. Please enter your M-Pesa PIN on your phone to complete the payment."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Failed to initiate M-Pesa payment with provider."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DarajaCallbackView(APIView):
    """
    This is the secure webhook endpoint that Safaricom's servers will call.
    It should NOT have authentication, as it's a server-to-server call.
    Secure it with IP Whitelisting in your production web server (e.g., NGINX).
    """
    permission_classes = [AllowAny] 

    def post(self, request):
        # The actual callback data is nested inside the request body
        callback_data = request.data.get('Body', {}).get('stkCallback', {})
        
        result_code = callback_data.get('ResultCode')
        checkout_request_id = callback_data.get('CheckoutRequestID')

        if result_code is None or not checkout_request_id:
            return Response({"ResultCode": 1, "ResultDesc": "Invalid payload received."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Use a database transaction and lock the row to prevent race conditions
            with transaction.atomic():
                payment = Payment.objects.select_for_update().get(provider_reference=checkout_request_id)

                # --- Idempotency Check ---
                if payment.status == Payment.Status.COMPLETED:
                    return Response({"ResultCode": 0, "ResultDesc": "Accepted"}) # Acknowledge duplicate

                if result_code == 0:
                    # Payment was successful
                    metadata = {item['Name']: item['Value'] for item in callback_data.get('CallbackMetadata', {}).get('Item', []) if 'Value' in item}
                    paid_amount = metadata.get('Amount')
                    
                    # --- Data Integrity Check ---
                    if paid_amount and float(paid_amount) != float(payment.amount):
                        payment.status = Payment.Status.FAILED
                        payment.metadata['failure_reason'] = f"Amount mismatch. Expected {payment.amount}, but callback received {paid_amount}."
                        payment.save()
                        # TODO: Log this serious error for manual review.
                        return Response({"ResultCode": 1, "ResultDesc": "Rejected due to amount mismatch."})

                    # Everything is correct. Finalize the payment.
                    payment.status = Payment.Status.COMPLETED
                    payment.metadata['mpesa_receipt'] = metadata.get('MpesaReceiptNumber')
                    payment.save()

                    # --- Grant Service to the User ---
                    # Here you would link this payment to a subscription object or update the user's status.
                    # For example: user.subscription.activate() or user.has_active_subscription = True
                
                else:
                    # The payment failed or was cancelled by the user.
                    payment.status = Payment.Status.FAILED
                    payment.metadata['failure_reason'] = callback_data.get('ResultDesc', 'The transaction failed or was cancelled.')
                    payment.save()

        except Payment.DoesNotExist:
            # Safaricom sent a callback for a transaction we don't recognize.
            # This is unusual and should be logged.
            return Response({"ResultCode": 1, "ResultDesc": "Transaction not found."})
            
        # Acknowledge receipt of the callback to Safaricom's servers.
        return Response({"ResultCode": 0, "ResultDesc": "Accepted"})
