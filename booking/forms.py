from django import forms
from django.contrib.auth.models import User
from booking.models import UserProfile

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    phone_number = forms.CharField(label='Номер телефону')

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()
            # Додаємо номер телефону в уже створений через сигнал профіль
            user.userprofile.phone_number = self.cleaned_data['phone_number']
            user.userprofile.save()
        return user
