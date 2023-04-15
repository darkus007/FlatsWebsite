from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse

from flats.models import Flat
from website.utilites import slugify


class FlatsUser(AbstractUser):
    send_email = models.BooleanField(default=False, verbose_name="Подписка на рассылку почты")

    class Meta:
        verbose_name_plural = 'Пользователи'
        verbose_name = 'Пользователь'

    def get_absolute_url(self):
        return reverse('user-profile', kwargs={'slug': slugify(self.username)})


class SelectedFlat(models.Model):
    flats_user = models.ForeignKey(FlatsUser, on_delete=models.CASCADE, related_name='selected_flats')
    flat_id = models.ForeignKey(Flat, on_delete=models.DO_NOTHING, verbose_name="Выбранная квартира")
    data_created = models.DateField(verbose_name='Последнее известное пользователю изменение')

    class Meta:
        verbose_name_plural = 'Выбранные Квартиры'
        verbose_name = 'Выбранная Квартира'
        ordering = ['flats_user']
