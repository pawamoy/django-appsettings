# -*- coding: utf-8 -*-

"""Main test script."""
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings

import pytest

import appsettings


def check_int(name, value):
    """Example checker function."""
    if not isinstance(value, int):
        raise ValueError('%s must be int' % name)


def transform(value):
    """Example transformer function."""
    if value:
        return 'OK'
    return 'NOT OK'


class AppSettingsExample(appsettings.AppSettings):
    """Example AppSettings class."""

    s1 = appsettings.Setting()
    s2 = appsettings.Setting(name='hey')
    s3 = appsettings.Setting(default=1)
    s4 = appsettings.IntSetting()
    s5 = appsettings.Setting(transformer=transform)
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
            assert hasattr(AppSettingsExample, 'get_%s' % setting)
            assert callable(getattr(AppSettingsExample, 'get_%s' % setting))
            assert hasattr(AppSettingsExample, 'check_%s' % setting)
            assert callable(getattr(AppSettingsExample, 'check_%s' % setting))
            assert hasattr(settings, setting)

    def test_get_methods(self):
        """Test static get methods."""
        assert AppSettingsExample.get_s1() is None
        assert AppSettingsExample.get_s2() is None
        assert AppSettingsExample.get_s3() == 1
        assert AppSettingsExample.get_s4() == 0
        assert AppSettingsExample.get_s5() == 'NOT OK'
        assert AppSettingsExample.get_s6() is None

    def test_check_methods(self):
        """Test static check methods."""
        assert AppSettingsExample.check_s1() is None
        assert AppSettingsExample.check_s4() is None
        with pytest.raises(ImproperlyConfigured):
            AppSettingsExample.check()
        assert appsettings.AppSettings.check() is None

    @override_settings(PREFIX_S7='required')
    def test_get_return_equals_instance_attr(self):
        """Test static get methods return same thing as instance attributes."""
        settings = AppSettingsExample()
        assert AppSettingsExample.get_s1() == settings.s1
        assert AppSettingsExample.get_s2() == settings.s2
        assert AppSettingsExample.get_s3() == settings.s3
        assert AppSettingsExample.get_s4() == settings.s4
        assert AppSettingsExample.get_s5() == settings.s5
        assert AppSettingsExample.get_s6() == settings.s6

    @override_settings(PREFIX_S7='required')
    def test_independent_from_order(self):
        """Test get methods do not depend on instantiation/import order."""
        got = [AppSettingsExample.get_s1(),
               AppSettingsExample.get_s2(),
               AppSettingsExample.get_s3(),
               AppSettingsExample.get_s4(),
               AppSettingsExample.get_s5(),
               AppSettingsExample.get_s6()]
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
        assert AppSettingsExample.get_s5() == 'OK'

    def test_setting_methods(self):
        """Test setting objects methods."""
        assert isinstance(AppSettingsExample.s1, appsettings.Setting)
        assert AppSettingsExample.s1.get() == AppSettingsExample.get_s1()

    def test_setting_type(self):
        """Test that settings are correctly initialized."""
        from appsettings.settings import (
            IntSetting, DictSetting, check_int, check_dict)
        int_setting = IntSetting()
        dict_setting = DictSetting()
        assert int_setting.checker == check_int
        assert dict_setting.checker == check_dict

    def tearDown(self):
        """Tear down method."""
        del self.package
