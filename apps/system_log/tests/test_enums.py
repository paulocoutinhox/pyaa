from django.test import TestCase

from apps.system_log.enums import LogLevel


class SystemLogEnumsTest(TestCase):

    def test_log_level_get_choices(self):
        choices = LogLevel.get_choices()
        self.assertIsInstance(choices, tuple)
        self.assertGreater(len(choices), 0)

        for choice in choices:
            self.assertIsInstance(choice, tuple)
            self.assertEqual(len(choice), 2)
