from unittest import TestCase

from .schanze_parser import SchanzeParser


class TestSchanzeParser(TestCase):
    parser: SchanzeParser = None

    def setUp(self):
        super().setUp()
        self.parser = SchanzeParser()

    def test_get_menu_string(self):
        menu = self.parser.get_menu_string()
        self.assertTrue('Veggie' in menu)
        self.assertTrue('Daily' in menu)
        self.assertTrue('CHF' in menu)

