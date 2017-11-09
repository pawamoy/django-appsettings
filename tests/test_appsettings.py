# -*- coding: utf-8 -*-

"""Main test script."""
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings

import pytest

import appsettings


class CustomSetting(appsettings.Setting):
    def transform(self):
        """Example transformer function."""
        if self.raw_value:
            return 'OK'
        return 'NOT OK'


class AppSettingsExample(appsettings.AppSettings):
    """Example AppSettings class."""

    s1 = appsettings.Setting()
    s2 = appsettings.Setting(name='hey')
    s3 = appsettings.Setting(default=1)
    s4 = appsettings.IntegerSetting()
    s5 = CustomSetting()
    s6 = appsettings.Setting(prefix='other')
    s7 = appsettings.Setting(required=True)

    class Meta:
        """AppSettings' Meta class."""

        setting_prefix = 'prefix_'


class MainTestCase(TestCase):
    """Main Django test case."""

    def setUp(self):
        """Setup method."""
        self.package = appsettings

    @override_settings(PREFIX_S7='required')
    def test_find_setting_with_hasattr(self):
        """Main test method."""
        settings = AppSettingsExample()
        for setting in ('s1', 's2', 's3', 's4', 's5'):
            assert hasattr(settings, setting)

    def test_cannot_call_settings_from_class(self):
        """Test static get methods."""
        assert not hasattr(AppSettingsExample, 's1')
        assert not hasattr(AppSettingsExample, 's2')
        assert not hasattr(AppSettingsExample, 's3')
        assert not hasattr(AppSettingsExample, 's4')
        assert not hasattr(AppSettingsExample, 's5')
        assert not hasattr(AppSettingsExample, 's6')

    def test_check_methods(self):
        """Test static check methods."""
        assert AppSettingsExample.settings['s1'].check() is None
        assert AppSettingsExample.settings['s4'].check() is None
        with pytest.raises(ImproperlyConfigured):
            AppSettingsExample.check()
        assert appsettings.AppSettings.check() is None

    @override_settings(PREFIX_S7='required')
    def test_get_return_equals_instance_attr(self):
        """Test static get methods return same thing as instance attributes."""
        settings = AppSettingsExample()
        assert AppSettingsExample.settings['s1'].get_value() == settings.s1
        assert AppSettingsExample.settings['s2'].get_value() == settings.s2
        assert AppSettingsExample.settings['s3'].get_value() == settings.s3
        assert AppSettingsExample.settings['s4'].get_value() == settings.s4
        assert AppSettingsExample.settings['s5'].get_value() == settings.s5
        assert AppSettingsExample.settings['s6'].get_value() == settings.s6

    @override_settings(PREFIX_S7='required')
    def test_independent_from_order(self):
        """Test get methods do not depend on instantiation/import order."""
        got = [AppSettingsExample.settings['s1'].get_value(),
               AppSettingsExample.settings['s2'].get_value(),
               AppSettingsExample.settings['s3'].get_value(),
               AppSettingsExample.settings['s4'].get_value(),
               AppSettingsExample.settings['s5'].get_value(),
               AppSettingsExample.settings['s6'].get_value()]
        settings = AppSettingsExample()
        assert got == [settings.s1,
                       settings.s2,
                       settings.s3,
                       settings.s4,
                       settings.s5,
                       settings.s6]

    @override_settings(PREFIX_S5=True)
    def test_transform(self):
        """Test transform function is actually called."""
        assert AppSettingsExample.settings['s5'].get_value() == 'OK'

    def test_setting_methods(self):
        """Test setting objects methods."""
        assert isinstance(AppSettingsExample.settings['s1'], appsettings.Setting)
        assert AppSettingsExample.settings['s1'].get_value() == AppSettingsExample.settings['s1'].value

    def tearDown(self):
        """Tear down method."""
        del self.package
