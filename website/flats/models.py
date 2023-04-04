from django.db import models
from django.urls import reverse


class Projects(models.Model):
    """ Таблица с информацией о ЖК. """
    project_id = models.IntegerField(primary_key=True)
    city = models.CharField(max_length=127, verbose_name='Город')
    name = models.CharField(max_length=127, verbose_name='ЖК')
    url = models.CharField(max_length=255, verbose_name='URL')
    metro = models.CharField(max_length=127, verbose_name='Метро')
    time_to_metro = models.IntegerField(null=True, blank=True, verbose_name='Время до метро')
    latitude = models.FloatField(null=True, blank=True, verbose_name='Широта')
    longitude = models.FloatField(null=True, blank=True, verbose_name='Долгота')
    address = models.CharField(max_length=255, verbose_name='Адрес')
    data_created = models.DateField(auto_now_add=True, verbose_name='Опубликовано')
    data_closed = models.DateField(null=True, blank=True, verbose_name='Снят с продажи')

    class Meta:
        db_table = 'projects'
        verbose_name_plural = 'Жилые Комплексы'
        verbose_name = 'Жилой Комплекс'
        ordering = ['name']


class Flats(models.Model):
    """ Таблица с информацией о Квартирах. """
    flat_id = models.IntegerField(primary_key=True)
    address = models.CharField(max_length=255, verbose_name='Адрес')
    floor = models.IntegerField(null=True, blank=True, verbose_name='Этаж')
    rooms = models.IntegerField(null=True, blank=True, verbose_name='Количество комнат')
    area = models.FloatField(null=True, blank=True, verbose_name='Площадь')
    finishing = models.BooleanField(null=True, blank=True, verbose_name='С отделкой')
    bulk = models.CharField(max_length=127, verbose_name='Корпус')
    settlement_date = models.DateField(null=True, blank=True, verbose_name='Заселение')
    url_suffix = models.CharField(max_length=127, verbose_name='Продолжение URL к адресу ЖК')
    data_created = models.DateField(auto_now_add=True, verbose_name='Опубликовано')
    data_closed = models.DateField(null=True, blank=True, verbose_name='Снята с продажи')

    project = models.ForeignKey('Projects', on_delete=models.PROTECT)

    def get_absolute_url(self):
        return reverse('flat-detail', kwargs={'flatid': self.pk})

    class Meta:
        db_table = 'flats'
        verbose_name_plural = 'Квартиры'
        verbose_name = 'Квартира'
        ordering = ['rooms']


class Prices(models.Model):
    """ Таблица с информацией о ценах на Квартиру. """
    benefit_name = models.CharField(null=True, blank=True, max_length=127, verbose_name='Ценовое предложение')
    benefit_description = models.CharField(null=True, blank=True, max_length=255, verbose_name='Описание')
    price = models.IntegerField(verbose_name='Цена')
    meter_price = models.IntegerField(null=True, blank=True, verbose_name='Цена за метр')
    booking_status = models.CharField(max_length=15, verbose_name='Бронь')
    data_created = models.DateField(auto_now_add=True, verbose_name='Опубликовано')

    flat = models.ForeignKey('Flats', on_delete=models.PROTECT, related_name='prices')

    class Meta:
        db_table = 'prices'
        verbose_name_plural = 'Цены'
        verbose_name = 'Цена'
        ordering = ['-data_created']


class AllFlatsLastPrice(models.Model):
    """
    Таблица с информацией о ценах на Квартиру.

    На уровне базы данных в виде представления (VIEW).
    Возвращает последнюю запись по квартире
    (последнее изменение по цене или статусу квартиры).
    """
    flat_id = models.IntegerField(primary_key=True)
    address = models.CharField(max_length=255, verbose_name='Адрес')
    floor = models.IntegerField(null=True, blank=True, verbose_name='Этаж')
    rooms = models.IntegerField(null=True, blank=True, verbose_name='Количество комнат')
    area = models.FloatField(null=True, blank=True, verbose_name='Площадь')
    finishing = models.BooleanField(null=True, blank=True, verbose_name='С отделкой')
    settlement_date = models.DateField(null=True, blank=True, verbose_name='Заселение')
    url_suffix = models.CharField(max_length=127, verbose_name='Продолжение URL к адресу ЖК')

    project_id = models.IntegerField(unique=True)
    city = models.CharField(max_length=127, verbose_name='Город')
    name = models.CharField(max_length=127, verbose_name='ЖК')
    url = models.CharField(max_length=255, verbose_name='URL')

    price = models.IntegerField(verbose_name='Цена')
    booking_status = models.CharField(max_length=15, verbose_name='Бронь')

    def get_absolute_url(self):
        return reverse('flat-detail', kwargs={'flatid': self.flat_id})

    class Meta:
        managed = False     # не будет применять миграции
        db_table = 'all_flats_last_price'
        ordering = ['price']
