from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect
from booking.models import UserProfile

class PhoneRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        try:
            profile = request.user.userprofile
            if not profile.phone_number:
                return redirect('fill-phone')
        except UserProfile.DoesNotExist:
            return redirect('fill-phone')

        return super().dispatch(request, *args, **kwargs)