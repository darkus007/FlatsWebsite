from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django import forms

from captcha.fields import CaptchaField

from .models import FlatsUser


class UserRegistrationForm(UserCreationForm):
    """ Стилизуем форму регистрации пользователя. """
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}),
                                 label='Имя')
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}),
                                label='Фамилия')
    captcha = CaptchaField(label='Введите текст с картинки',
                           error_messages={'invalid': 'Неверно указан текст с картинки'})

    class Meta:
        model = FlatsUser
        # fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'captcha')
        labels = {'username': 'Логин'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control '
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'


class EditUserForm(UserChangeForm):
    """ Стилизуем форму обновления профиля пользователя. """
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Имя')
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}),
                                label='Фамилия')
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Логин')

    class Meta:
        model = FlatsUser
        fields = ('username', 'first_name', 'last_name', 'email', 'password')


class UserPasswordChangeForm(PasswordChangeForm):
    """ Стилизуем форму смены пароля пользователя. """
    old_password = forms.CharField(max_length=100,
                                   widget=forms.PasswordInput(attrs={'class': 'form-control', 'type': 'password'}),
                                   label='Старый пароль')
    new_password1 = forms.CharField(max_length=100,
                                    widget=forms.PasswordInput(attrs={'class': 'form-control', 'type': 'password'}),
                                    label='Новый пароль')
    new_password2 = forms.CharField(max_length=100,
                                    widget=forms.PasswordInput(attrs={'class': 'form-control', 'type': 'password'}),
                                    label='Подтверждение нового пароля')

    class Meta:
        model = FlatsUser
        fields = ('old_password', 'new_password1', 'new_password2')
