from django.shortcuts import render
from rest_framework import viewsets
from .models import Listing, Booking, Payment
from .serializers import ListingSerializer, BookingSerializer, PaymentSerializer
from django.http import JsonResponse
import requests
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
import uuid
from .tasks import send_payment_confirmation_email
from django.conf import settings

CHAPA_API_URL = settings.CHAPA_API_URL
CHAPA_VERIFY_URL = settings.CHAPA_VERIFY_URL
CHAPA_SECRET_KEY = settings.CHAPA_SECRET_KEY

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    @action(detail=False, methods=['post'])
    def initiate(self, request):
        booking_id = request.data.get('booking')
        amount = request.data.get('amount')
        booking = Booking.objects.get(pk=booking_id)
        data = {
            "amount": amount,
            "currency": "ETB",
            "email": booking.user.email,
            "first_name": booking.user.first_name,
            "last_name": booking.user.last_name,
            "tx_ref": str(uuid.uuid4()),
            "return_url": "https://yourdomain.com/payment/verify/",
        }
        headers = {"Authorization": f"Bearer {CHAPA_SECRET_KEY}"}
        chapa_response = requests.post(CHAPA_API_URL, json=data, headers=headers)
        chapa_data = chapa_response.json()
        if chapa_response.status_code == 200 and chapa_data.get("status") == "success":
            transaction_id = chapa_data["data"]["tx_ref"]
            payment = Payment.objects.create(
                booking=booking,
                amount=amount,
                transaction_id=transaction_id,
                status="Pending"
            )
            return Response({
                "payment": PaymentSerializer(payment).data,
                "checkout_url": chapa_data["data"]["checkout_url"]
            }, status=201)
        return Response({"error": chapa_data.get("message", "Payment initiation failed")}, status=400)

    @action(detail=False, methods=['post'])
    def verify(self, request):
        transaction_id = request.data.get('transaction_id')
        headers = {"Authorization": f"Bearer {CHAPA_SECRET_KEY}"}
        verify_response = requests.get(f"{CHAPA_VERIFY_URL}{transaction_id}/", headers=headers)
        verify_data = verify_response.json()
        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=404)
        if verify_response.status_code == 200 and verify_data.get("status") == "success":
            payment.status = "Completed"
            payment.save()
            send_payment_confirmation_email.delay(payment.booking.user.email, payment.booking.id)
            return Response({"status": "Payment completed"})
        else:
            payment.status = "Failed"
            payment.save()
            return Response({"status": "Payment failed"}, status=400)

def index(request):
    return JsonResponse({'message': 'Hello from listings!'})