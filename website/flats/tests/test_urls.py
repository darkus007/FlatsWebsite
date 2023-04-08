from datetime import date

from django.conf import settings
from django.db import connection
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from flats.models import Price, Flat, Project


class UrlsTestCase(TestCase):      # python manage.py test flats.tests.test_urls
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

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        settings.SECRET_KEY = None

    def test_index_url_exists_at_desired_location(self):
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('index'))
        self.assertEqual(resp.status_code, 200)

    def test_flat_url_exists_at_desired_location(self):
        response = self.client.get('flat/647794/')
        self.assertEqual(response.status_code, 200)

    def test_flat_url_accessible_by_name(self):
        resp = self.client.get(reverse('flat-detail', kwargs={'flatid': 647794}))
        self.assertEqual(resp.status_code, 200)

    def test_project_url_exists_at_desired_location(self):
        response = self.client.get('project/1/')
        self.assertEqual(response.status_code, 200)

    def test_project_url_accessible_by_name(self):
        resp = self.client.get(reverse('project-list', kwargs={'project_id': 1}))
        self.assertEqual(resp.status_code, 200)
