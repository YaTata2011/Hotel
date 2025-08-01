from django.urls import path
from booking import views
from booking.views import BookRoomViews
from django.contrib.auth import views as auth_views
from booking.views import BookRoomViews, MyBookingsView, EditBookingView, DeleteBookingView

from booking.views import MyBookingsView



urlpatterns = [
    path("", views.index, name="index"),
    path("rooms-list/", views.room_list, name="rooms-list"),
    path("book-room/", BookRoomViews.as_view(), name="book-room"),
    path("booking-details/<int:pk>", views.booking_details, name="booking-details"),
    path("fill-phone/", views.fill_phone, name = "fill-phone"),
    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="booking/login.html"), name="login"),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path("my-bookings/", MyBookingsView.as_view(), name="my-bookings"),
    path("edit-booking/<int:pk>/", EditBookingView.as_view(), name="edit-booking"),
    path("delete-booking/<int:pk>/", DeleteBookingView.as_view(), name="delete-booking"),
    path("my-bookings/", MyBookingsView.as_view(), name="my-bookings"),
    path('contacts/', views.contacts, name='contacts'),
]


