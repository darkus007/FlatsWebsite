from django.conf import settings
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.core.cache import cache

from flats.models import Project
from flats.middlewares import projects


class MiddlewaresTestsCase(TestCase):      # python manage.py test flats.tests.test_middlewares
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        settings.SECRET_KEY = "$ecret_key_for_@ny_te$t$!"

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

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        settings.SECRET_KEY = None

    def test_projects(self):
        expected_data = {'name': 'City', 'project_id': 1}
        self.assertEqual(projects(None)['projects'][0], expected_data)

    def test_projects_cache(self):
        with CaptureQueriesContext(connection) as queries:
            cache.delete('projects')    # может сохраниться от предыдущих запросов
            projects(None)              # выполняем функцию, которая кеширует данные
            projects(None)              # выполняем несколько раз
            projects(None)
            self.assertEqual(len(queries), 1, "Кэширование не работает!")
