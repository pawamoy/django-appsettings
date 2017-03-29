# -*- coding: utf-8 -*-

"""Main test script."""


from django.test import TestCase

import pytest

import appsettings


def check_int(name, value):
    if not isinstance(value, int):
        raise ValueError('%s must be int' % name)


def transform(value):
    if value:
        return 'OK'
    return 'NOT OK'


class AppSettingsExample(appsettings.AppSettings):
    s1 = appsettings.Setting()
    s2 = appsettings.Setting(name='hey')
    s3 = appsettings.Setting(default=1)
    s4 = appsettings.Setting(checker=check_int)
    s5 = appsettings.Setting(transformer=transform)
    s6 = appsettings.Setting(prefix='other')

    class Meta:
        settings_prefix = 'prefix_'


class MainTestCase(TestCase):
    """Main Django test case."""

    def setUp(self):
        """Setup method."""
        pass

    def test_main(self):
        """Main test method."""
        for setting in ('s1', 's2', 's3', 's4', 's5'):
            assert hasattr(AppSettingsExample, 'get_%s' % setting)
            attr = getattr(AppSettingsExample, 'get_%s' % setting)
            assert callable(attr)
            assert hasattr(AppSettingsExample, 'check_%s' % setting)
            attr = getattr(AppSettingsExample, 'check_%s' % setting)
            assert callable(attr)
        assert AppSettingsExample.get_s1() is None
        assert AppSettingsExample.get_s2() is None
        assert AppSettingsExample.get_s3() == 1
        assert AppSettingsExample.get_s4() is None
        assert AppSettingsExample.get_s5() == 'NOT OK'
        assert AppSettingsExample.get_s6() is None
        assert AppSettingsExample.check_s1() is None
        with pytest.raises(ValueError):
            AppSettingsExample.check_s4()

    def tearDown(self):
        """Tear down method."""
        pass
