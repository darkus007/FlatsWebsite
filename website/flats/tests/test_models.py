from datetime import date

from django.conf import settings
from django.db import connection
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from flats.models import Price, Flat, Project, AllFlatsLastPrice


class ModelsTestCase(TestCase):      # python manage.py test flats.tests.test_models
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        settings.SECRET_KEY = "$ecret_key_for_@ny_te$t$!"

        cls.user = get_user_model().objects.create_user(username='test_user', password='test_user_password')
        cls.client = Client()

        cls.project = Project.objects.create(
            project_id=1,
            city='Moscow',
            name='City',
            url='https://www.pik.ru/ms',
            metro='Бабушкинская',
            time_to_metro=5,
            latitude=55.85213,
            longitude=37.622005,
            address='ГринПарк, строители'
        )

        cls.flat = Flat.objects.create(
            flat_id=647794,
            address='City',
            floor=13,
            rooms=3,
            area=84,
            finishing=True,
            bulk='Блок 8',
            settlement_date=date(2023, 4, 4),
            url_suffix='/flats/647794',
            project=cls.project
        )

        cls.price = Price.objects.create(
            price_id=1,
            benefit_name='Ипотека 1%',
            benefit_description='Первый взнос — от 15%, ставка — 1%, срок — до 30 лет, сумма кредита — до 30 млн ₽',
            price=5000000,
            meter_price=150,
            booking_status='active',
            flat=cls.flat
        )

        # создаем представление
        with connection.cursor() as cursor:
            cursor.execute("""
                        CREATE VIEW all_flats_last_price AS
                            SELECT flat.flat_id, flat.address, flat.floor, flat.rooms, flat.area, flat.finishing,
                            flat.settlement_date, flat.url_suffix,
                                project.project_id, project.name, project.city, project.url,
                                price.price, price.booking_status
                            FROM flat
                            INNER JOIN project ON flat.project_id = project.project_id
                            INNER JOIN price ON price.flat_id = flat.flat_id
                            INNER JOIN (
                                SELECT flat_id, max(data_created) AS max_data
                                FROM price
                                GROUP BY flat_id
                            ) AS last_price ON last_price.flat_id = price.flat_id
                            WHERE price.data_created = last_price.max_data;
                        """)

        cls.all_flats_last_price = AllFlatsLastPrice.objects.first()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        settings.SECRET_KEY = None

    def test_projects_verbose_name(self):
        """ verbose_name в полях совпадает с ожидаемым. """
        field_verbose = {
            'project_id': 'project id',
            'city': 'Город',
            'name': 'ЖК',
            'url': 'URL',
            'metro': 'Метро',
            'time_to_metro': 'Время до метро',
            'latitude': 'Широта',
            'longitude': 'Долгота',
            'address': 'Адрес',
            'data_created': 'Опубликовано',
            'data_closed': 'Снят с продажи',
        }
        for field, expected_value in field_verbose.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.project._meta.get_field(field).verbose_name, expected_value)

    def test_flats_verbose_name(self):
        """ verbose_name в полях совпадает с ожидаемым. """
        field_verbose = {
            'flat_id': 'flat id',
            'address': 'Адрес',
            'floor': 'Этаж',
            'rooms': 'Количество комнат',
            'area': 'Площадь',
            'finishing': 'С отделкой',
            'bulk': 'Корпус',
            'settlement_date': 'Заселение',
            'url_suffix': 'Продолжение URL к адресу ЖК',
            'data_created': 'Опубликовано',
            'data_closed': 'Снята с продажи',
        }
        for field, expected_value in field_verbose.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.flat._meta.get_field(field).verbose_name, expected_value)

    def test_flats_get_absolute_url(self):
        self.assertEqual(self.flat.get_absolute_url(), '/flat/647794/')

    def test_prices_verbose_name(self):
        """ verbose_name в полях совпадает с ожидаемым. """
        field_verbose = {
            'price_id': 'price id',
            'benefit_name': 'Ценовое предложение',
            'benefit_description': 'Описание',
            'price': 'Цена',
            'meter_price': 'Цена за метр',
            'booking_status': 'Бронь',
            'data_created': 'Опубликовано',
            'flat': 'flat',
        }
        for field, expected_value in field_verbose.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.price._meta.get_field(field).verbose_name, expected_value)

    def test_all_flats_last_price_verbose_name(self):
        """ verbose_name в полях совпадает с ожидаемым. """
        field_verbose = {
            'flat_id': 'flat id',
            'address': 'Адрес',
            'floor': 'Этаж',
            'rooms': 'Количество комнат',
            'area': 'Площадь',
            'finishing': 'С отделкой',
            'settlement_date': 'Заселение',
            'url_suffix': 'Продолжение URL к адресу ЖК',

            'project_id': 'project id',
            'city': 'Город',
            'name': 'ЖК',
            'url': 'URL',

            'price': 'Цена',
            'booking_status': 'Бронь',
        }
        for field, expected_value in field_verbose.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.all_flats_last_price._meta.get_field(field).verbose_name, expected_value)

    def test_all_flats_last_price_get_absolute_url(self):
        self.assertEqual(self.all_flats_last_price.get_absolute_url(), '/flat/647794/')
