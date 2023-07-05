from django.contrib.auth import get_user_model
from django.test import TestCase


class FlatsUserModelTestCase(TestCase):   # python manage.py test members.tests.test_models
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = get_user_model().objects.create_user(username='test_user',
                                                        email='test@testsite.ru',
                                                        password='test_user_password')

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()

    def test_verbose_name(self):
        """ verbose_name в новых полях совпадает с ожидаемым. """
        field_verbose = {
            'email': 'Адрес электронной почты',
            'is_email_activated': 'Прошел активацию?',
            'send_email': 'Подписка на рассылку почты',
        }
        for field, expected_value in field_verbose.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.user._meta.get_field(field).verbose_name, expected_value)

    def test_unique_email_field(self):
        self.assertTrue(self.user._meta.get_field('email').unique)
