# -*- coding: utf-8 -*-

"""Main test script."""



from django.test import TestCase

import appsettings


class MainTestCase(TestCase):
    """Main Django test case."""

    def setUp(self):
        """Setup method."""
        pass

    def test_main(self):
        """Main test method."""
        assert appsettings

    def tearDown(self):
        """Tear down method."""
        pass
