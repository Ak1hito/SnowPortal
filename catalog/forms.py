from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile

class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label='Электронная почта',
        widget=forms.EmailInput(attrs={'placeholder': 'example@mail.ru'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        labels = {
            'username': 'Имя пользователя',
            'password1': 'Пароль',
            'password2': 'Подтверждение пароля',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем плейсхолдеры
        self.fields['username'].widget.attrs.update({'placeholder': 'Придумайте логин'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Минимум 8 символов'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Повторите пароль'})

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('height', 'weight')   # убрали riding_style
        widgets = {
            'height': forms.NumberInput(attrs={'min': 140, 'max': 220, 'placeholder': 'см'}),
            'weight': forms.NumberInput(attrs={'min': 30, 'max': 150, 'placeholder': 'кг'}),
        }