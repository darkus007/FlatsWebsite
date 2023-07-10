from datetime import date

from django.conf import settings
from django.test import TestCase
from django.db import connection
from django.contrib.auth import get_user_model

from flats.models import Project, Flat, Price, AllFlatsLastPrice
from members.models import SelectedFlat
from api.serializers import (
    ProjectSerializer, AllFlatsLastPriceSerializer, SelectedFlatSerializer,
    UserReadSerializer, UserUpdateSerializer, UserCreateSerializer
)


class Settings(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        settings.SECRET_KEY = "some_secret_key!"

        cls.user = get_user_model().objects.create_user(
            username='test_user',
            first_name='first_name',
            last_name='last_name',
            email='email@mail.ru',
            password='test_user_password'
        )

        cls.project = Project.objects.create(
            project_id=1,
            city='Moscow',
            name='City',
            url='https://www.pik.ru/ms',
            metro='Бабушкинская',
            time_to_metro=5,
            latitude=55.85213,
            longitude=37.622005,
            address='ГринПарк, строители',
            data_created=date(2023, 4, 4)
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
            project=cls.project,
            data_created=date(2023, 4, 4)
        )

        cls.price = Price.objects.create(
            price_id=1,
            benefit_name='Ипотека 1%',
            benefit_description='Первый взнос — от 15%, ставка — 1%, срок — до 30 лет, сумма кредита — до 30 млн ₽',
            price=5000000,
            meter_price=150,
            booking_status='active',
            flat=cls.flat,
            data_created=date(2023, 4, 4)
        )

        cls.selected_flat = SelectedFlat.objects.create(
            flats_user=cls.user,
            flat_id=cls.flat,
            data_created=date(2023, 4, 4)
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

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        settings.SECRET_KEY = None


class AllSerializersTestCase(Settings):  # python manage.py test api.tests.test_serializers.AllSerializersTestCase

    def test_project_serializer(self):
        serializer = ProjectSerializer(self.project)
        expected_data = {'name': 'City', 'url': 'https://www.pik.ru/ms'}
        self.assertEqual(serializer.data, expected_data)

    def test_all_flats_last_price_serializer(self):
        serializer = AllFlatsLastPriceSerializer(AllFlatsLastPrice.objects.first())
        expected_data = {'flat_id': 647794, 'address': 'City', 'floor': 13, 'rooms': 3, 'area': 84.0, 'finishing': True,
                         'settlement_date': str(date(2023, 4, 4)), 'url_suffix': '/flats/647794', 'project_id': 1,
                         'city': 'Moscow', 'name': 'City', 'url': 'https://www.pik.ru/ms', 'price': 5000000,
                         'booking_status': 'active'}
        self.assertEqual(serializer.data, expected_data)

    def test_selected_flat_serializer(self):
        serializer = SelectedFlatSerializer(self.selected_flat)
        expected_data = {'id': 1, 'data_created': '2023-04-04', 'flats_user': 1, 'flat_id': 647794}
        self.assertEqual(serializer.data, expected_data)

    def test_user_read_serializer(self):
        serializer = UserReadSerializer(self.user)
        expected_data = {'id': 1, 'username': 'test_user', 'first_name': 'first_name',
                         'last_name': 'last_name', 'email': 'email@mail.ru'}
        self.assertEqual(serializer.data, expected_data)

    def test_user_update_serializer(self):
        serializer = UserUpdateSerializer(self.user)
        expected_data = {'username': 'test_user', 'first_name': 'first_name', 'last_name': 'last_name'}
        self.assertEqual(serializer.data, expected_data)

    def test_user_create_serializer(self):
        serializer = UserCreateSerializer(self.user)
        expected_data = {'username': 'test_user', 'first_name': 'first_name', 'last_name': 'last_name',
                         'email': 'email@mail.ru', 'password': self.user.password}
        self.assertEqual(serializer.data, expected_data)
