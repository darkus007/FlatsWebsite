from django.shortcuts import render
from django.contrib.auth.views import PasswordChangeView
from django.views.generic import CreateView, UpdateView, DetailView
from django.urls import reverse_lazy

from .forms import UserRegistrationForm, EditUserForm, UserPasswordChangeForm


class UserRegistrationView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'registration/register_or_edit_user.html'
    success_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Новый пользователь'
        context['button'] = 'Регистрация'
        context['extra_link'] = False
        return context


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
