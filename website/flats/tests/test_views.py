"""
Реализована Проверка:
    - views;
    - пагинатора;
    - количества запросов в БД.

"""

from datetime import date

from django.conf import settings
from django.core.cache import cache
from django.test import TestCase, Client
from django.test.utils import CaptureQueriesContext
from django.db import connection
from django.contrib.auth import get_user_model
from django.urls import reverse

from flats.models import Prices, Flats, Projects


class ViewsTestSettings(TestCase):     # python manage.py test flats.tests.test_views
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        settings.SECRET_KEY = "$ecret_key_for_@ny_te$t$!"

        cls.user = get_user_model().objects.create_user(username='test_user', password='test_user_password')
        cls.client = Client()

        cls.project = Projects.objects.create(
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

        cls.project2 = Projects.objects.create(
            project_id=2,
            city='Moscow',
            name='City',
            url='https://www.pik.ru/ms',
            metro='Бабушкинская',
            time_to_metro=5,
            latitude=55.85213,
            longitude=37.622005,
            address='ГринПарк, строители'
        )

        cls.flat = Flats.objects.create(
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

        cls.flat2 = Flats.objects.create(
            flat_id=647784,
            address='City',
            floor=13,
            rooms=3,
            area=84,
            finishing=True,
            bulk='Блок 8',
            settlement_date=date(2023, 4, 4),
            url_suffix='/flats/647794',
            project=cls.project2
        )

        cls.price = Prices.objects.create(
            benefit_name='Ипотека 1%',
            benefit_description='Первый взнос — от 15%, ставка — 1%, срок — до 30 лет, сумма кредита — до 30 млн ₽',
            price=5000000,
            meter_price=150,
            booking_status='active',
            flat=cls.flat
        )

        cls.price2 = Prices.objects.create(
            benefit_name='Ипотека 1%',
            benefit_description='Первый взнос — от 15%, ставка — 1%, срок — до 30 лет, сумма кредита — до 30 млн ₽',
            price=5000000,
            meter_price=150,
            booking_status='active',
            flat=cls.flat2
        )

        for i in range(53):
            flat = Flats.objects.create(
                flat_id=i*100,
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
            Prices.objects.create(
                benefit_name='Ипотека 1%',
                benefit_description='Первый взнос — от 15%, ставка — 1%, срок — до 30 лет, сумма кредита — до 30 млн ₽',
                price=5000000,
                meter_price=150,
                booking_status='active',
                flat=flat
            )

        # создаем представление
        with connection.cursor() as cursor:
            cursor.execute("""
                    CREATE VIEW all_flats_last_price AS
                    SELECT flats.flat_id, flats.address, flats.floor, flats.rooms, flats.area, flats.finishing, 
                    flats.settlement_date, flats.url_suffix,
                        projects.project_id, projects.name, projects.city, projects.url,
                        prices.price, prices.booking_status
                    FROM flats
                    INNER JOIN projects ON flats.project_id = projects.project_id
                    INNER JOIN prices ON prices.flat_id = flats.flat_id
                    INNER JOIN (
                        SELECT flat_id, max(data_created) AS max_data
                        FROM prices
                        GROUP BY flat_id
                    ) AS last_price ON last_price.flat_id = prices.flat_id
                    WHERE prices.data_created = last_price.max_data;""")

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        settings.SECRET_KEY = None


class IndexListTestCase(ViewsTestSettings):
    def test_view(self):
        expected_data = {'flat_id': 647794, 'address': 'City', 'floor': 13, 'rooms': 3, 'area': 84.0, 'finishing': True,
                         'settlement_date': date(2023, 4, 4), 'url_suffix': '/flats/647794', 'project_id': 1,
                         'city': 'Moscow', 'name': 'City', 'url': 'https://www.pik.ru/ms', 'price': 5000000,
                         'booking_status': 'active'}
        response = self.client.get(reverse('index'))
        self.assertTrue(response.context.get('flats'))    # object_list переопределен на flats и не пуст
        self.assertEqual(response.context.get('flats').values()[0], expected_data)

    def test_paginator(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(len(response.context.get('flats')), 50)
        response = self.client.get('/?page=2')
        self.assertEqual(len(response.context.get('flats')), 5)

    def test_queries(self):
        """ Тестируем количество запросов в БД. """
        with CaptureQueriesContext(connection) as queries:
            cache.delete('projects')  # может сохраниться от предыдущих запросов
            response = self.client.get(reverse('index'))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(queries), 3, "Увеличилось число запросов в БД!")


class FlatDetailViewTestCase(ViewsTestSettings):
    def test_view(self):
        expected_data = {'address': 'City', 'rooms': 3, 'area': 84.0, 'floor': 13, 'finishing': True,
                         'settlement_date': date(2023, 4, 4), 'url_suffix': '/flats/647794',
                         'project__name': 'City', 'project__url': 'https://www.pik.ru/ms'}
        response = self.client.get(reverse('flat-detail', kwargs={'flatid': 647794}))
        self.assertTrue(response.context.get('flats'))    # object_list переопределен на flats и не пуст
        self.assertEqual(response.context.get('flats'), expected_data)

    def test_view_context(self):
        expected_data = {'flat': 647794, 'data_created': date(2023, 4, 4), 'price': 5000000,
                         'booking_status': 'active', 'benefit_name': 'Ипотека 1%',
                         'benefit_description': 'Первый взнос — от 15%, ставка — 1%, '
                                                'срок — до 30 лет, сумма кредита — до 30 млн ₽'}
        response = self.client.get(reverse('flat-detail', kwargs={'flatid': 647794}))
        self.assertTrue(response.context.get('flats'))    # object_list переопределен на flats и не пуст
        self.assertTrue(response.context.get('prices'))    # контекст на prices и не пуст
        self.assertEqual(response.context.get('prices')[0], expected_data)

    def test_queries(self):
        """ Тестируем количество запросов в БД. """
        with CaptureQueriesContext(connection) as queries:
            cache.delete('projects')  # может сохраниться от предыдущих запросов
            response = self.client.get(reverse('flat-detail', kwargs={'flatid': 647794}))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(queries), 3, "Увеличилось число запросов в БД!")


class ProjectListViewTestCase(ViewsTestSettings):
    def test_view(self):
        expected_data = {'flat_id': 647784, 'address': 'City', 'floor': 13, 'rooms': 3, 'area': 84.0, 'finishing': True,
                         'settlement_date': date(2023, 4, 4), 'url_suffix': '/flats/647794', 'project_id': 2,
                         'city': 'Moscow', 'name': 'City', 'url': 'https://www.pik.ru/ms', 'price': 5000000,
                         'booking_status': 'active'}
        response = self.client.get(reverse('project-list', kwargs={'project_id': 2}))
        self.assertTrue(response.context.get('flats'))    # object_list переопределен на flats и не пуст
        self.assertEqual(response.context.get('flats').values()[0], expected_data)

    def test_paginator(self):
        response = self.client.get(reverse('project-list', kwargs={'project_id': 1}))
        self.assertEqual(len(response.context.get('flats')), 50)
        response = self.client.get('/?page=2')
        self.assertEqual(len(response.context.get('flats')), 5)

    def test_queries(self):
        """ Тестируем количество запросов в БД. """
        with CaptureQueriesContext(connection) as queries:
            cache.delete('projects')  # может сохраниться от предыдущих запросов
            response = self.client.get(reverse('project-list', kwargs={'project_id': 1}))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(queries), 3, "Увеличилось число запросов в БД!")
