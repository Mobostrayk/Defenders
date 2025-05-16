from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import UserHabit
from django import forms
from captcha.fields import CaptchaField

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("Этот email уже зарегистрирован")
        return email

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    captcha = CaptchaField(
        label='Подтвердите что вы не робот',
        error_messages={'invalid': 'Неверная капча'}
    )


class VerificationForm(forms.Form):
    code = forms.CharField(
        label='Код подтверждения',
        max_length=6,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    captcha = CaptchaField(
        label='Введите текст с картинки',
        error_messages={'invalid': 'Неверная капча'}
    )

class HabitSettingsForm(forms.ModelForm):
    class Meta:
        model = UserHabit
        fields = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        widgets = {
            'monday': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'tuesday': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'wednesday': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'thursday': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'friday': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'saturday': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sunday': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
class HabitDaysForm(forms.ModelForm):
    class Meta:
        model = UserHabit
        fields = ['monday', 'tuesday', 'wednesday', 'thursday',
                 'friday', 'saturday', 'sunday']