import requests
import uuid
from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Payment

@api_view(['POST'])
def initiate_payment(request):
    data = request.data
    booking_reference = str(uuid.uuid4())
    amount = data.get('amount')
    email = data.get('email')
    name = data.get('name')

    payment = Payment.objects.create(
        booking_reference=booking_reference,
        amount=amount,
        email=email
    )

    headers = {
        "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"
    }

    payload = {
        "amount": amount,
        "currency": "ETB",
        "email": email,
        "first_name": name,
        "tx_ref": booking_reference,
        "callback_url": f"http://127.0.0.1:8000/api/verify-payment/{booking_reference}/",
        "return_url": "http://127.0.0.1:8000/payment-success/",
        "customization[title]": "Travel Booking Payment",
        "customization[description]": "Payment for travel booking"
    }

    response = requests.post(f"{settings.CHAPA_BASE_URL}/transaction/initialize", headers=headers, data=payload)
    res = response.json()

    if res.get('status') == 'success':
        payment.transaction_id = res['data']['tx_ref']
        payment.save()
        return Response({
            "checkout_url": res['data']['checkout_url'],
            "booking_reference": booking_reference
        })
    else:
        return Response({"error": "Payment initiation failed"}, status=400)

