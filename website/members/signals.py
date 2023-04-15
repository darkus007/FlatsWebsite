"""
Модуль содержит

Сигнал регистрации нового пользователя и
    обработчик для отправки писем подтверждения e-mail.
"""
from django.dispatch import Signal

from .utilities import send_activation_notification


user_registered = Signal()


def user_registered_dispatcher(sender, **kwargs):
    send_activation_notification(kwargs['instance'])


user_registered.connect(user_registered_dispatcher)
