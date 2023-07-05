"""
Тестируем доступность url
"""

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.conf import settings
from django.urls import reverse, NoReverseMatch


class UrlsTestCase(TestCase):  # python manage.py test members.tests.test_urls
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.client = Client()
        cls.user = get_user_model().objects.create_user(username='test_user',
                                                        email='test@testsite.ru',
                                                        password='test_user_password')
        settings.SECRET_KEY = "some_test_secret_key!"
        settings.LOGIN_REDIRECT_URL = 'register'
        settings.LOGOUT_REDIRECT_URL = 'register'

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        settings.SECRET_KEY = None

    def test_register(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_repeat_send_email(self):
        response = self.client.get(reverse('repeat-send-email', kwargs={'flat_id': 0}))
        self.assertEqual(response.status_code, 302)

    def test_password_changed(self):
        response = self.client.get(reverse('password-changed'))
        self.assertEqual(response.status_code, 200)

    # Проверяем наличие путей, которые предоставляет django.contrib.auth.urls,
    # на случай изменения urlpatterns

    def test_login(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_logout(self):
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response,
                             expected_url=reverse('register'),
                             status_code=302,
                             target_status_code=200,
                             fetch_redirect_response=True)

    def test_password_change(self):
        response = self.client.get(reverse('password_change'))
        self.assertEqual(response.status_code, 302)

    def test_password_change_done(self):
        response = self.client.get(reverse('password_change_done'))
        self.assertEqual(response.status_code, 302)

    def test_password_reset(self):
        response = self.client.get(reverse('password_reset'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/password_reset_form.html')

    def test_password_reset_done(self):
        response = self.client.get(reverse('password_reset_done'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/password_reset_done.html')

    def test_password_reset_confirm(self):
        with self.assertRaises(NoReverseMatch):
            self.client.get(reverse('password_reset_confirm',
                                    kwargs={'uidb64': '', 'token': ''}))

    def test_password_reset_complete(self):
        response = self.client.get(reverse('password_reset_complete'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/password_reset_complete.html')
