from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Listing, Booking, Payment
from .serializers import ListingSerializer, BookingSerializer, PaymentSerializer
from django.http import JsonResponse
import requests
from rest_framework import status
from rest_framework.decorators import action
import uuid
from .tasks import send_payment_confirmation_email, send_booking_confirmation_email
from django.conf import settings

CHAPA_API_URL = settings.CHAPA_API_URL
CHAPA_VERIFY_URL = settings.CHAPA_VERIFY_URL
CHAPA_SECRET_KEY = settings.CHAPA_SECRET_KEY

@api_view(['GET'])
def api_root(request):
    """API root endpoint"""
    return Response({
        'message': 'Welcome to ALX Travel App API',
        'version': 'v1',
        'endpoints': {
            'listings': request.build_absolute_uri('v1/listings/'),
            'bookings': request.build_absolute_uri('v1/bookings/'),
            'payments': request.build_absolute_uri('v1/payments/'),
            'documentation': request.build_absolute_uri('/swagger/'),
        }
    })

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [permissions.AllowAny]  # Allow public access

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.AllowAny]  # Allow public access for demo
    
    def create(self, request, *args, **kwargs):
        """Override create method to send booking confirmation email"""
        response = super().create(request, *args, **kwargs)
        
        if response.status_code == 201:
            booking_data = response.data
            booking = Booking.objects.get(pk=booking_data['booking_id'])
            
            # Trigger booking confirmation email task
            send_booking_confirmation_email.delay(
                user_email=booking.user.email,
                booking_id=str(booking.booking_id),
                listing_title=booking.listing.title,
                start_date=str(booking.start_date),
                end_date=str(booking.end_date)
            )
            
        return response

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.AllowAny]  # Allow public access for demo

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
            "return_url": "https://www.kingsleyusa.dev",
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