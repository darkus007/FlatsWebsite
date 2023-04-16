from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm, PasswordResetForm
from django import forms

from captcha.fields import CaptchaField

from .models import FlatsUser
from .signals import user_registered
from .tasks import task_send_mail_reset_password


class UserRegistrationForm(UserCreationForm):
    """ Форма регистрации пользователя. """
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}),
                                 label='Имя')
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}),
                                label='Фамилия')
    captcha = CaptchaField(label='Введите текст с картинки',
                           error_messages={'invalid': 'Неверно указан текст с картинки'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = False
        user.is_activated = False
        if commit:
            user.save()
        # Можно обойтись без использования сигнала, вызвав напрямую
        # функцию send_activation_notification(user)
        user_registered.send(UserRegistrationForm, instance=user)
        return user

    class Meta:
        model = FlatsUser
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'captcha')
        labels = {'username': 'Логин'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control '
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'


class EditUserForm(UserChangeForm):
    """ Форма обновления профиля пользователя. """
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Имя')
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}),
                                label='Фамилия')
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Логин')

    class Meta:
        model = FlatsUser
        fields = ('username', 'first_name', 'last_name', 'email', 'password')


class UserPasswordChangeForm(PasswordChangeForm):
    """ Форма смены пароля пользователя. """
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


class CustomPasswordResetForm(PasswordResetForm):
    """ Отправляет письма через Celery """
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'id': 'email',
                                                            'placeholder': 'Email'}))

    def send_mail(self, subject_template_name, email_template_name, context,
                  from_email, to_email, html_email_template_name=None):
        context['user'] = context['user'].id
        task_send_mail_reset_password.delay(subject_template_name=subject_template_name,
                                            email_template_name=email_template_name,
                                            context=context, from_email=from_email, to_email=to_email,
                                            html_email_template_name=html_email_template_name)
