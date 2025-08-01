from django.shortcuts import render, redirect, get_object_or_404
from booking.models import Booking
from .models import Payment
from django.contrib.auth.decorators import login_required

@login_required
def checkout(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    # Створюємо запис оплати
    payment = Payment.objects.create(
        booking=booking,
        user=request.user,
        amount=booking.total_price,
        status='pending',
        payment_provider='liqpay'  # або інше
    )

    # Тут можна перенаправити на сторінку платіжного сервісу
    return render(request, 'payments/checkout.html', {'payment': payment})

