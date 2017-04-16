# -*- coding: utf-8 -*-

"""Main test script."""


from django.test import TestCase

import appsettings


class MainTestCase(TestCase):
    """Main Django test case."""

    def setUp(self):
        """Setup method."""
        self.package = appsettings

    def test_main(self):
        """Main test method."""
        assert self.package

    def tearDown(self):
        """Tear down method."""
        del self.package
