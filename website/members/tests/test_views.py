from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.conf import settings
from django.urls import reverse
from django.core.signing import Signer

signer = Signer()


class ViewsTestCase(TestCase):  # python manage.py test members.tests.test_views
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        settings.SECRET_KEY = "some_test_secret_key!"

        cls.user = get_user_model().objects.create_user(username='test_user',
                                                        email='test@testsite.ru',
                                                        password='test_user_password')
        cls.client = Client()
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        settings.SECRET_KEY = None

    def test_user_registration_view(self):
        response = self.client.get('/members/login/')
        self.assertEqual(response.status_code, 200)

    def test_user_password_change_view_not_logged(self):
        response = self.client.get('/members/password/')
        self.assertRedirects(response,
                             expected_url='/members/login/?next=/members/password/',
                             status_code=302,
                             target_status_code=200,
                             fetch_redirect_response=True)

    def test_user_password_change_view_logged(self):
        response = self.auth_client.get('/members/password/')
        self.assertEqual(response.status_code, 200)

    def test_password_changed(self):
        response = self.auth_client.get('/members/password-success/')
        self.assertEqual(response.status_code, 200)

    def test_user_email_activate_get_activation_done(self):
        sign = signer.sign(self.user.username)
        response = self.client.get(reverse('email-activate', kwargs={'sign': sign}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/activation_done.html')

    def test_user_email_activate_get_user_is_activated(self):
        user = get_user_model().objects.create_user(username='test_user_is_email_activated',
                                                    email='test_is_email_activated@testsite.ru',
                                                    password='test_user_password',
                                                    is_email_activated=True)
        sign = signer.sign(user.username)
        response = self.client.get(reverse('email-activate', kwargs={'sign': sign}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/user_is_activated.html')

    def test_send_email_activate_letter_not_logged(self):
        response = self.client.get(reverse('repeat-send-email', kwargs={'flat_id': 1}))
        self.assertRedirects(response,
                             expected_url='/members/login/?next=/members/repeat-send-email/1/',
                             status_code=302,
                             target_status_code=200,
                             fetch_redirect_response=True)

    def test_send_email_activate_letter_logged(self):
        response = self.auth_client.get(reverse('repeat-send-email', kwargs={'flat_id': 1}))
        self.assertEqual(str(response.context['user']), 'test_user')
        self.assertRedirects(response,
                             expected_url=reverse('flat-detail', kwargs={'flatid': 1}),
                             status_code=302,
                             target_status_code=200,
                             fetch_redirect_response=True)
