from django.contrib import admin
from booking.models import Booking, Room

from .models import UserProfile

admin.site.register(Booking)
admin.site.register(Room)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number')
    search_fields = ('user__username', 'phone_number')

