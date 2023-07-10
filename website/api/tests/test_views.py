import json
import logging
from datetime import date

from django.test import TestCase
from django.conf import settings
from django.db import connection
from django.db.models import Subquery
from django.core.signing import Signer
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from flats.models import Project, Flat, Price, AllFlatsLastPrice
from members.models import SelectedFlat
from members.utilities import signer

from api.serializers import (
    AllFlatsLastPriceSerializer,
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

        cls.flat2 = Flat.objects.create(
            flat_id=647795,
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

        cls.selected_flat = SelectedFlat.objects.create(
            flats_user=cls.user,
            flat_id=cls.flat,
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

        for i in range(53):
            flat = Flat.objects.create(
                flat_id=i * 100,
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
            Price.objects.create(
                price_id=100 + i,
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

        cls.client = APIClient()
        cls.auth_client = APIClient()

        cls.auth_client.force_login(cls.user)

        cls.signer = Signer()  # Используем для создания цифровой подписи

        logging.getLogger('django.request').setLevel(logging.ERROR)

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        settings.SECRET_KEY = None


# python manage.py test api.tests.test_views.ProjectsAndAllFlatsViewTestCase
class ProjectsAndAllFlatsViewTestCase(Settings):
    """
    Тестируем Квартиры, ЖК:
    ProjectList и AllFlatsLastPriceList.
    """

    # ================ ProjectList ================

    def test_project_list_get(self):
        expected_data = Project.objects.values('name', 'url')
        response = self.client.get(reverse('api_v1:projects'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content).get('results'), list(expected_data))

    def test_project_list_post(self):
        response = self.client.post(reverse('api_v1:projects'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_project_list_put(self):
        response = self.client.put(reverse('api_v1:projects'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_project_list_patch(self):
        response = self.client.patch(reverse('api_v1:projects'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_project_list_delete(self):
        response = self.client.delete(reverse('api_v1:projects'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ================ AllFlatsLastPriceList ================

    def test_all_flats_last_price_list_get(self):
        response = self.client.get(reverse('api_v1:flats'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json.loads(response.content).get('results')),
                         settings.REST_FRAMEWORK_PAGINATION_MAX_SIZE)
        total_flats = AllFlatsLastPrice.objects.count()
        self.assertEqual(json.loads(response.content).get('count'), total_flats)

    def test_all_flats_last_price_list_post(self):
        response = self.client.post(reverse('api_v1:flats'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_all_flats_last_price_list_put(self):
        response = self.client.put(reverse('api_v1:flats'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_all_flats_last_price_list_patch(self):
        response = self.client.patch(reverse('api_v1:flats'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_all_flats_last_price_list_delete(self):
        response = self.client.delete(reverse('api_v1:flats'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ================ Пользователи ================

    def test_user_api_view_get_not_auth(self):
        response = self.client.get(reverse('api_v1:user'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_api_view_get_auth(self):
        self.user.refresh_from_db()
        expected_data = UserReadSerializer(instance=self.user).data
        response = self.auth_client.get(reverse('api_v1:user'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

    def test_user_api_view_post_auth(self):
        response = self.auth_client.post(reverse('api_v1:user'))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_user_api_view_put_auth(self):
        response = self.auth_client.put(reverse('api_v1:user'))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_user_api_view_patch_auth(self):
        response = self.auth_client.patch(reverse('api_v1:user'),
                                          data={'last_name': 'last-name'})
        self.user.refresh_from_db()
        expected_data = UserUpdateSerializer(instance=self.user).data
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, expected_data)
        self.assertEqual(response.data.get('last_name'), 'last-name')

    def test_user_api_view_delete_auth(self):
        response = self.auth_client.delete(reverse('api_v1:user'))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_user_not_auth(self):
        response = self.client.put(reverse('api_v1:user-create'),
                                   data={'username': 'created_user',
                                         'first_name': 'first_name',
                                         'last_name': 'last_name',
                                         'email': 'created_user@mail.ru',
                                         'password': 'created_user_password'},
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected_data = UserCreateSerializer(get_user_model().objects.get(username='created_user')).data
        self.assertEqual(response.data, expected_data)

    def test_send_email_for_activate_user_not_auth(self):
        response = self.client.get(reverse('api_v1:send-activation-email'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_send_email_for_activate_user_auth(self):
        response = self.auth_client.get(reverse('api_v1:send-activation-email'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_email_activate_bad_signature(self):
        response = self.client.get(reverse('api_v1:activate-email', kwargs={'sign': 'sign'}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error': 'Signature does not match.'})

    def test_user_email_activate_object_does_not_exist(self):
        sign = signer.sign('test_user_email_activate')
        response = self.client.get(reverse('api_v1:activate-email', kwargs={'sign': sign}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error': 'User is not found.'})

    def test_user_email_activate_is_email_activated_true(self):
        sign = signer.sign(self.user.username)
        self.user.is_email_activated = True
        self.user.save()
        self.user.refresh_from_db()
        response = self.client.get(reverse('api_v1:activate-email', kwargs={'sign': sign}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'info': 'Email has already been activated.'})

    def test_user_email_activate_is_email_activated_false(self):
        sign = signer.sign(self.user.username)
        self.user.is_email_activated = False
        self.user.save()
        self.user.refresh_from_db()
        response = self.client.get(reverse('api_v1:activate-email', kwargs={'sign': sign}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'info': 'Email is activated successfully.'})

    # ================ Квартиры пользователя для отслеживания ================
    def test_user_selected_flats_api_view_get_not_auth(self):
        response = self.client.get(reverse('api_v1:selected-flats'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_selected_flats_api_view_get_auth(self):
        response = self.auth_client.get(reverse('api_v1:selected-flats'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        subquery = Subquery(SelectedFlat.objects.filter(flats_user=self.user.id).values('flat_id'))
        user_flats = AllFlatsLastPrice.objects.filter(flat_id__in=subquery)
        serializer = AllFlatsLastPriceSerializer(user_flats, many=True)
        self.assertEqual(response.data, serializer.data)

    def test_user_selected_flats_api_view_post_not_auth(self):
        response = self.client.post(reverse('api_v1:selected-flats'),
                                    data={'flat_id': self.flat.flat_id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_selected_flats_api_view_post_auth__already_exist(self):
        response = self.auth_client.post(reverse('api_v1:selected-flats'),
                                         data={'flat_id': self.flat.flat_id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'info': 'The flat has already been added to the tracked.'})

    def test_user_selected_flats_api_view_post_auth__not_found(self):
        response = self.auth_client.post(reverse('api_v1:selected-flats'),
                                         data={'flat_id': 8888})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'info': 'The flat was not found.'})

    def test_user_selected_flats_api_view_post_auth__success(self):
        response = self.auth_client.post(reverse('api_v1:selected-flats'),
                                         data={'flat_id': self.flat2.flat_id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'info': 'The flat is added to the trackable.'})

    def test_user_selected_flats_api_view_delete_not_auth(self):
        response = self.client.delete(reverse('api_v1:selected-flats'),
                                      data={'flat_id': self.flat.flat_id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_selected_flats_api_view_delete_auth_success(self):
        response = self.auth_client.delete(reverse('api_v1:selected-flats'),
                                           data={'flat_id': self.flat.flat_id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_selected_flats_api_view_delete_auth_not_found(self):
        response = self.auth_client.delete(reverse('api_v1:selected-flats'),
                                           data={'flat_id': 8888})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
