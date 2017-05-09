# -*- coding: utf-8 -*-

"""Main test script."""
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings

import pytest

import appsettings


class CustomSetting(appsettings.Setting):
    def transform(self):
        """Example transformer function."""
        if self.get_raw():
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
    def test_hasattr(self):
        """Main test method."""
        settings = AppSettingsExample()
        for setting in ('s1', 's2', 's3', 's4', 's5'):
            assert hasattr(settings, setting)

    def test_get_methods(self):
        """Test static get methods."""
        assert AppSettingsExample.s1.get() is None
        assert AppSettingsExample.s2.get() is None
        assert AppSettingsExample.s3.get() == 1
        assert AppSettingsExample.s4.get() == 0
        assert AppSettingsExample.s5.get() == 'NOT OK'
        assert AppSettingsExample.s6.get() is None

    def test_check_methods(self):
        """Test static check methods."""
        assert AppSettingsExample.s1.check() is None
        assert AppSettingsExample.s4.check() is None
        with pytest.raises(ImproperlyConfigured):
            AppSettingsExample.check()
        assert appsettings.AppSettings.check() is None

    @override_settings(PREFIX_S7='required')
    def test_get_return_equals_instance_attr(self):
        """Test static get methods return same thing as instance attributes."""
        settings = AppSettingsExample()
        assert AppSettingsExample.s1.get() == settings.s1
        assert AppSettingsExample.s2.get() == settings.s2
        assert AppSettingsExample.s3.get() == settings.s3
        assert AppSettingsExample.s4.get() == settings.s4
        assert AppSettingsExample.s5.get() == settings.s5
        assert AppSettingsExample.s6.get() == settings.s6

    @override_settings(PREFIX_S7='required')
    def test_independent_from_order(self):
        """Test get methods do not depend on instantiation/import order."""
        got = [AppSettingsExample.s1.get(),
               AppSettingsExample.s2.get(),
               AppSettingsExample.s3.get(),
               AppSettingsExample.s4.get(),
               AppSettingsExample.s5.get(),
               AppSettingsExample.s6.get()]
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
        assert AppSettingsExample.s5.get() == 'OK'

    def test_setting_methods(self):
        """Test setting objects methods."""
        assert isinstance(AppSettingsExample.s1, appsettings.Setting)
        assert AppSettingsExample.s1.get() == AppSettingsExample.s1.get()

    def tearDown(self):
        """Tear down method."""
        del self.package
