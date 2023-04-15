from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.views import PasswordChangeView
from django.views.generic import CreateView, UpdateView, DetailView, TemplateView
from django.urls import reverse_lazy, reverse
from django.core.signing import BadSignature
from django.contrib import messages

from .models import FlatsUser
from .forms import UserRegistrationForm, EditUserForm, UserPasswordChangeForm
from .utilities import signer, send_activation_notification


class UserRegistrationView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'registration/register_or_edit_user.html'
    success_url = reverse_lazy('register-done')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Новый пользователь'
        context['button'] = 'Регистрация'
        context['extra_link'] = False
        return context


class RegisterDoneView(TemplateView):
    template_name = 'billboard/register_done.html'


class UserChangeView(UpdateView):
    form_class = EditUserForm
    template_name = 'registration/register_or_edit_user.html'
    success_url = reverse_lazy('home')

    def get_object(self, queryset=None):
        """
        Переопределяем метод для заполнения формы
        данными текущего авторизованного пользователя.
        """
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактировать пользователя'
        context['button'] = 'Обновить профиль'
        context['extra_link'] = True
        return context


class UserPasswordChangeView(PasswordChangeView):
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy('password_changed')


def password_changed(request):
    return render(request, 'registration/password_changed.html')


def user_email_activate(request, sign):
    """
    Функция для активации e-mail пользователя.
    Принимает сообщение о подтверждении адреса электронной почты
    и если все верно и подпись не скомпрометирована, активирует e-mail пользователя.
    """
    try:
        username = signer.unsign(sign)
    except BadSignature:
        return render(request, 'registration/bad_signature.html')
    user = get_object_or_404(FlatsUser, username=username)
    if user.is_email_activated:
        template = 'registration/user_is_activated.html'
    else:
        template = 'registration/activation_done.html'
        user.is_email_activated = True
        user.save()
    return render(request, template)


@login_required
def send_email_activate_letter(request, flat_id):
    """
    По запросу пользователя повторно отправляет письмо для подтверждения e-mail
    """
    send_activation_notification(request.user)
    messages.add_message(request, messages.SUCCESS,
                         f'Электронной письмо отправлено. Проверьте почту "{request.user.email}".')
    return HttpResponseRedirect(reverse('flat-detail', kwargs={'flatid': flat_id}))
