from django.db import models
from django.contrib.auth.models import User
from booking.models import Booking  # якщо booking — твій додаток з бронюванням

class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Очікує оплату'),
        ('paid', 'Оплачено'),
        ('failed', 'Не вдалося'),
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    payment_provider = models.CharField(max_length=100, blank=True)  # LiqPay, Stripe...

    def __str__(self):
        return f"{self.user.username} - {self.amount} грн - {self.status}"



