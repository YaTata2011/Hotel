from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta  # 🆕 для роботи з тривалістю

class Room(models.Model):
    number = models.IntegerField()
    capacity = models.IntegerField()
    location = models.TextField()
    price_per_day = models.DecimalField(max_digits=8, decimal_places=2, default=1000)

    image = models.ImageField(upload_to='room_images/', blank=True, null=True)
    video = models.FileField(upload_to="videos/", blank=True, null=True)

    def __str__(self):
        return f"Room # {self.number}-{self.capacity}"
        
    class Meta:
        verbose_name = "Room"
        verbose_name_plural = "Rooms"
        ordering = ["number"]

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="bookings")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    creation_time = models.DateTimeField(auto_now_add=True)

    total_price = models.DecimalField(  # 🆕 поле для збереження загальної ціни
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

    def get_total_price(self):  # 🆕 метод для обчислення суми бронювання
        days = (self.end_time.date() - self.start_time.date()).days
        return days * self.room.price_per_day

    def save(self, *args, **kwargs):  # 🆕 автоматичне збереження суми перед збереженням
        self.total_price = self.get_total_price()
        super().save(*args, **kwargs)

    @property
    def duration_days(self):
        """Повертає кількість днів бронювання, мінімум 1"""
        delta = self.end_time - self.start_time
        return delta.days or 1  # якщо .days == 0, повертаємо 1

    def __str__(self):
        return f"{self.user.username}-{self.room}"
    
    class Meta:
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"
        ordering = ["start_time"]

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
