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

from flats.models import Price, Flat, Project


class ViewsTestSettings(TestCase):     # python manage.py test flats.tests.test_views
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        settings.SECRET_KEY = "$ecret_key_for_@ny_te$t$!"

        cls.user = get_user_model().objects.create_user(username='test_user', password='test_user_password')
        cls.client = Client()
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)

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

        cls.project2 = Project.objects.create(
            project_id=2,
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

        cls.flat2 = Flat.objects.create(
            flat_id=647784,
            address='City',
            floor=13,
            rooms=3,
            area=84,
            finishing=True,
            bulk='Блок 8',
            settlement_date=date(2023, 4, 4),
            url_suffix='/flats/647794',
            project=cls.project2,
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

        cls.price2 = Price.objects.create(
            price_id=2,
            benefit_name='Ипотека 1%',
            benefit_description='Первый взнос — от 15%, ставка — 1%, срок — до 30 лет, сумма кредита — до 30 млн ₽',
            price=5000000,
            meter_price=150,
            booking_status='active',
            flat=cls.flat2,
            data_created=date(2023, 4, 4)
        )

        for i in range(53):
            flat = Flat.objects.create(
                flat_id=i*100,
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
            Price.objects.create(
                price_id=100+i,
                benefit_name='Ипотека 1%',
                benefit_description='Первый взнос — от 15%, ставка — 1%, срок — до 30 лет, сумма кредита — до 30 млн ₽',
                price=5000000,
                meter_price=150,
                booking_status='active',
                flat=flat,
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
        response = self.client.get(reverse('flat-detail', kwargs={'flatid': 647794}))
        self.assertTrue(response.context.get('flats'))    # object_list переопределен на flats и не пуст
        self.assertEqual(response.context.get('flats').pk, 647794)

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


class SelectedFlatListViewTestCase(ViewsTestSettings):

    def test_selected_flat_list_get_page_not_logged(self):
        response = self.client.get(reverse('user-choice', kwargs={'user_id': self.user.id}))
        self.assertRedirects(response,
                             expected_url=f'/members/login/?next=/user-choice/{self.user.id}/',
                             status_code=302,
                             target_status_code=200,
                             fetch_redirect_response=True)

    def test_selected_flat_list_get_page_logged(self):
        response = self.auth_client.get(reverse('user-choice', kwargs={'user_id': self.user.id}))
        # Проверка, что пользователь залогинился
        self.assertEqual(str(response.context['user']), self.user.username)
        self.assertEqual(response.status_code, 200)
