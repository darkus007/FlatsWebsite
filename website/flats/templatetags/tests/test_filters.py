from django.test import TestCase

from flats.templatetags.filters import replace_n


class FiltersTestCase(TestCase):
    def test_replace_n(self):
        test_data = '\\nПроверка\\n удаления \\nпереносов строки!\\n'
        expected_data = '. Проверка.  удаления . переносов строки!. '
        self.assertEqual(replace_n(test_data), expected_data)
