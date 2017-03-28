# -*- coding: utf-8 -*-

"""Main test script."""


from django.test import TestCase

import appsettings


def check_int(name, value):
    if not isinstance(value, int):
        raise ValueError('%s must be int' % name)


def transform(value):
    if value:
        return 'OK'
    return 'NOT OK'


class AppSettingsExample(appsettings.AppSettings):
    my_setting1 = appsettings.Setting()
    my_setting2 = appsettings.Setting(name='hey')
    my_setting3 = appsettings.Setting(default=1)
    my_setting4 = appsettings.Setting(checker=check_int)
    my_setting5 = appsettings.Setting(transformer=transform)

    class Meta:
        settings_prefix = 'prefix_'


class MainTestCase(TestCase):
    """Main Django test case."""

    def setUp(self):
        """Setup method."""
        pass

    def test_main(self):
        """Main test method."""
        for setting in ('my_setting1',
                        'my_setting2',
                        'my_setting3',
                        'my_setting4',
                        'my_setting5'):
            assert hasattr(AppSettingsExample, 'get_raw_%s' % setting)
            attr = getattr(AppSettingsExample, 'get_raw_%s' % setting)
            assert callable(attr)
            assert hasattr(AppSettingsExample, 'get_%s' % setting)
            attr = getattr(AppSettingsExample, 'get_%s' % setting)
            assert callable(attr)
            assert hasattr(AppSettingsExample, 'check_%s' % setting)
            attr = getattr(AppSettingsExample, 'check_%s' % setting)
            assert callable(attr)
        assert AppSettingsExample.get_raw_my_setting1() is None
        assert AppSettingsExample.get_my_setting1() is None
        assert AppSettingsExample.check_my_setting1() is None

    def tearDown(self):
        """Tear down method."""
        pass
