from django.shortcuts import render, redirect
from django.http import HttpResponse
from booking.models import Room, Booking, UserProfile
from django.contrib import messages
from django.views import View
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from booking.forms import UserRegistrationForm
from datetime import datetime, timedelta  # ✅ Додано timedelta для обчислення днів
from django.utils import timezone
from .mixins import PhoneRequiredMixin

from django.views.generic import ListView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django import forms

from django.core.mail import EmailMessage

def index(request):
    room = Room.objects.first()
    context = {
        "render_string": "Hello, world!",
        "room": room,
    }
    return render(request, "booking/index.html", context)

def room_list(request):
    now = timezone.now()
    rooms = Room.objects.all()

    room_bookings = {
        room: room.bookings.filter(end_time__gte=now).order_by("start_time")
        for room in rooms
    }

    return render(request, "booking/rooms_list.html", {
        "room_bookings": room_bookings
    })

class BookRoomViews(PhoneRequiredMixin, View):
    def get(self, request):
        room_id = request.GET.get("room_id")
        rooms = Room.objects.all()
        return render(request, "booking/booking_form.html", {
            "rooms": rooms,
            "selected_room_id": room_id,
        })

    def post(self, request):
        room_id = request.POST.get("room-number")
        start_time_str = request.POST.get("start-time")
        end_time_str = request.POST.get("end-time")

        try:
            start_time = datetime.fromisoformat(start_time_str)
            end_time = datetime.fromisoformat(end_time_str)
        except ValueError:
            messages.error(request, "Невірний формат дати.")
            return redirect("book-room")

        if end_time <= start_time:
            messages.error(request, "Дата виїзду має бути пізніше дати заїзду.")
            return redirect("book-room")

        room = Room.objects.get(id=room_id)
        overlapping = Booking.objects.filter(
            room=room,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exists()

        if overlapping:
            messages.error(request, "Ця кімната вже заброньована на цей період.")
            return redirect("book-room")

        duration_days = (end_time - start_time).days or 1  # ✅ Мінімум 1 день
        total_price = duration_days * room.price_per_day    # ✅ Виправлено: використовуємо price_per_day

        # ✅ Створюємо нове бронювання з обчисленою сумою
        booking = Booking.objects.create(
            user=request.user,
            room=room,
            start_time=start_time,
            end_time=end_time,
            total_price=total_price
        )

        # ✅ Повідомлення з сумою
        messages.success(request, f"Кімната успішно заброньована. Сума: {total_price} грн")
        return redirect("rooms-list")
   

def booking_details(request, pk):
    try:
        booking = Booking.objects.get(id=pk)
        return render(request, "booking/booking_details.html", {"booking": booking})
    except Booking.DoesNotExist:
        return HttpResponse("This booking not exist", status=404)

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserRegistrationForm()
    return render(request, 'booking/register.html', {'form': form})

@login_required
def fill_phone(request):
    if request.method == "POST":
        phone = request.POST.get("phone")
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.phone_number = phone
        profile.save()
        return redirect("book-room")
    return render(request, "booking/fill_phone.html")

@method_decorator(login_required, name='dispatch')
class MyBookingsView(ListView):
    model = Booking
    template_name = "booking/my_bookings.html"
    context_object_name = "bookings"

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).order_by("start_time")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ✅ Додано підрахунок загальної суми всіх бронювань
        context["total_sum"] = sum(booking.total_price for booking in context["bookings"])
        return context

class EditBookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["start_time", "end_time"]
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

@method_decorator(login_required, name='dispatch')
class EditBookingView(UpdateView):
    model = Booking
    form_class = EditBookingForm
    template_name = "booking/edit_booking.html"

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def form_valid(self, form):
        booking = form.save(commit=False)
        overlapping = Booking.objects.filter(
            room=booking.room,
            start_time__lt=booking.end_time,
            end_time__gt=booking.start_time
        ).exclude(id=booking.id).exists()

        if overlapping:
            form.add_error(None, "Ця кімната вже заброньована на вказаний період.")
            return self.form_invalid(form)

        # ✅ Оновлюємо total_price при зміні дат
        duration_days = (booking.end_time - booking.start_time).days or 1
        booking.total_price = duration_days * booking.room.price
        booking.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("my-bookings")

@method_decorator(login_required, name='dispatch')
class DeleteBookingView(DeleteView):
    model = Booking
    template_name = "booking/confirm_delete.html"
    success_url = reverse_lazy("my-bookings")

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

def contacts(request):
    return render(request, 'booking/contacts.html')

