# -*- coding: utf-8 -*-

"""Main test script."""

import mock
import pytest
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.test import SimpleTestCase, override_settings

import appsettings


def imported_object():
    return "tests.test_appsettings.SettingTestCase._imported_object2"


class TypeCheckerTestCase(SimpleTestCase):
    """Type checkers tests."""

    def setUp(self):
        self.name = "setting"
        self.message = r"setting must be %s, not %s"
        self.message_greater = r"setting must be greater or equal %s"
        self.message_less = r"setting must be less or equal %s"
        self.message_longer = r"setting must be longer than %s \(or equal\)"
        self.message_shorter = r"setting must be shorter than %s \(or equal\)"
        self.message_empty = r"setting must not be empty"
        self.message_items = r"All elements of setting must be %s"
        self.message_keys = r"All keys of setting must be %s"
        self.message_values = r"All values of setting must be %s"

    def test_type_checker(self):
        checker = appsettings.TypeChecker(int)
        checker(self.name, 0)
        with pytest.raises(ValueError, match=self.message % (checker.base_type, type(None))):
            checker(self.name, None)

    def test_boolean_type_checker(self):
        checker = appsettings.BooleanTypeChecker()
        checker(self.name, True)
        with pytest.raises(ValueError, match=self.message % (checker.base_type, type(None))):
            checker(self.name, None)

    def test_integer_type_checker(self):
        checker = appsettings.IntegerTypeChecker()
        checker(self.name, 0)
        with pytest.raises(ValueError, match=self.message % (checker.base_type, type(None))):
            checker(self.name, None)

        checker.minimum = 1
        checker(self.name, 1)
        with pytest.raises(ValueError, match=self.message_greater % checker.minimum):
            checker(self.name, 0)

        checker.maximum = 2
        checker(self.name, 2)
        with pytest.raises(ValueError, match=self.message_less % checker.maximum):
            checker(self.name, 3)

    def test_float_type_checker(self):
        checker = appsettings.FloatTypeChecker()
        checker(self.name, 0.0)
        with pytest.raises(ValueError, match=self.message % (checker.base_type, type(None))):
            checker(self.name, None)

        checker.minimum = 1.1
        checker(self.name, 1.1)
        with pytest.raises(ValueError, match=self.message_greater % checker.minimum):
            checker(self.name, 0.1)

        checker.maximum = 2.1
        checker(self.name, 2.1)
        with pytest.raises(ValueError, match=self.message_less % checker.maximum):
            checker(self.name, 3.1)

    def test_string_type_checker(self):
        checker = appsettings.StringTypeChecker()
        checker(self.name, "")
        with pytest.raises(ValueError, match=self.message % (checker.base_type, type(None))):
            checker(self.name, None)

        checker.min_length = 1
        checker(self.name, "1")
        with pytest.raises(ValueError, match=self.message_longer % checker.min_length):
            checker(self.name, "")

        checker.max_length = 2
        checker(self.name, "12")
        with pytest.raises(ValueError, match=self.message_shorter % checker.max_length):
            checker(self.name, "123")

        checker.min_length = None
        checker.max_length = None
        checker.empty = False
        with pytest.raises(ValueError, match=self.message_empty):
            checker(self.name, "")

    def test_list_type_checker(self):
        checker = appsettings.ListTypeChecker()
        checker(self.name, list())
        with pytest.raises(ValueError, match=self.message % (checker.base_type, type(None))):
            checker(self.name, None)

        checker.item_type = str
        checker(self.name, list())  # empty
        checker(self.name, ["ding"])  # one item
        checker(self.name, ["ding", "dong"])  # multiple items
        with pytest.raises(ValueError, match=self.message_items % checker.item_type):
            checker(self.name, [None])
        with pytest.raises(ValueError, match=self.message_items % checker.item_type):
            checker(self.name, ["ding", None])  # not all

    def test_set_type_checker(self):
        checker = appsettings.SetTypeChecker()
        checker(self.name, set())
        with pytest.raises(ValueError, match=self.message % (checker.base_type, type(None))):
            checker(self.name, None)

    def test_tuple_type_checker(self):
        checker = appsettings.TupleTypeChecker()
        checker(self.name, tuple())
        with pytest.raises(ValueError, match=self.message % (checker.base_type, type(None))):
            checker(self.name, None)

    def test_dict_type_checker(self):
        checker = appsettings.DictTypeChecker()
        checker(self.name, dict())
        with pytest.raises(ValueError, match=self.message % (checker.base_type, type(None))):
            checker(self.name, None)

        checker.min_length = 1
        checker(self.name, {1: 1})
        with pytest.raises(ValueError, match=self.message_longer % checker.min_length):
            checker(self.name, {})

        checker.max_length = 2
        checker(self.name, {1: 1, 2: 2})
        with pytest.raises(ValueError, match=self.message_shorter % checker.max_length):
            checker(self.name, {1: 1, 2: 2, 3: 3})

        checker.min_length = None
        checker.max_length = None
        checker.empty = False
        with pytest.raises(ValueError, match=self.message_empty):
            checker(self.name, {})

        checker = appsettings.DictTypeChecker(key_type=int, value_type=str)
        checker(self.name, {0: "0"})  # one pair
        checker(self.name, {0: "0", 1: "1"})  # multiple pairs
        with pytest.raises(ValueError, match=self.message_keys % checker.key_type):
            checker(self.name, {None: None})  # both key and value wrong
        with pytest.raises(ValueError, match=self.message_keys % checker.key_type):
            checker(self.name, {None: "0"})  # only key wrong
        with pytest.raises(ValueError, match=self.message_values % checker.value_type):
            checker(self.name, {0: None})  # only value wrong
        with pytest.raises(ValueError, match=self.message_keys % checker.key_type):
            checker(self.name, {0: "0", "1": "1"})  # not all keys
        with pytest.raises(ValueError, match=self.message_values % checker.value_type):
            checker(self.name, {0: "0", 1: 1})  # not all values


class SettingTestCase(SimpleTestCase):
    @staticmethod
    def _imported_object2():
        return "nothing"

    def setUp(self):
        self.message_required = "%s setting is required and"
        self.message_missing_item = "%s setting is missing required item"
        self.message_no_attr = "has no attribute '%s'"

    def test_setting(self):
        setting = appsettings.Setting()
        assert setting.name == ""
        assert setting.full_name == ""
        assert setting.default_value is None
        assert setting.value is None
        assert setting.get_value() is None
        assert setting.checker is None
        assert setting.validators == []
        setting.check()
        with pytest.raises(AttributeError, match=self.message_no_attr % setting.full_name):
            assert setting.raw_value

    def test_setting_name(self):
        setting = appsettings.Setting(name="Name", prefix="Prefix_")
        assert setting.name == "Name"
        assert setting.prefix == "Prefix_"
        assert setting.full_name == "PREFIX_NAME"

    def test_setting_default_callable(self):
        setting = appsettings.Setting(default=lambda: 1, call_default=True)
        assert setting.value == 1
        setting.call_default = False
        assert callable(setting.value)
        assert setting.value() == 1

    def test_setting_default_dont_raise_exception(self):
        setting = appsettings.IntegerSetting(name="setting", default="hello")
        assert setting.value == "hello"
        with override_settings(SETTING=0):
            assert setting.value == 0

    def test_setting_required(self):
        setting = appsettings.Setting(name="setting", prefix="custom_", required=True, default=True)
        with pytest.raises(AttributeError, match=self.message_required % setting.full_name):
            assert setting.value
        assert setting.default_value

        setting.parent_setting = appsettings.Setting(name="parent_setting")
        with override_settings(PARENT_SETTING={}):
            with pytest.raises(KeyError, match=self.message_missing_item % setting.parent_setting.full_name):
                assert setting.value

    def test_setting_transform(self):
        class Setting(appsettings.Setting):
            def transform(self, value):
                if value is None:
                    return "TRANSFORMED"
                return value

        setting = Setting(name="transform")
        with override_settings(TRANSFORM=None):
            assert setting.value == "TRANSFORMED"
        with override_settings(TRANSFORM=1024):
            assert setting.value == 1024

    def test_setting_validators(self):
        # Test default and custom validators are correctly chained.
        class TestSetting(appsettings.Setting):
            default_validators = (mock.sentinel.validator,)

        setting = TestSetting(name="INQUISITOR", validators=(mock.sentinel.custom_validator,))
        assert setting.validators == [mock.sentinel.validator, mock.sentinel.custom_validator]

    def test_setting_validators_pass(self):
        validator = mock.Mock()
        setting = appsettings.Setting(name="INQUISITOR", validators=(validator,))

        with self.settings(INQUISITOR=mock.sentinel.lister):
            setting.check()

        assert validator.mock_calls == [mock.call(mock.sentinel.lister)]

    def test_setting_validators_fail(self):
        validator = mock.Mock(side_effect=ValidationError("You're not worthy!"))
        setting = appsettings.Setting(name="INQUISITOR", validators=(validator,))

        with self.settings(INQUISITOR=mock.sentinel.lister):
            with pytest.raises(ValueError, match="Setting INQUISITOR has an invalid value:.*You're not worthy!"):
                setting.check()

        assert validator.mock_calls == [mock.call(mock.sentinel.lister)]

    def test_setting_custom_validate(self):
        # Test custom validate method
        class TestSetting(appsettings.Setting):
            def validate(self, value):
                raise ValidationError("You're not worthy!")

        setting = TestSetting(name="INQUISITOR")

        with self.settings(INQUISITOR=mock.sentinel.lister):
            with pytest.raises(ValueError, match="Setting INQUISITOR has an invalid value:.*You're not worthy!"):
                setting.check()

    def test_setting_checker(self):
        class Setting(appsettings.Setting):
            def checker(self, name, value):
                if isinstance(value, int):
                    raise ValueError(name)

        setting = Setting(name="check_test")
        with override_settings(CHECK_TEST=0):
            with pytest.raises(ValueError):
                setting.check()
        with override_settings(CHECK_TEST="ok"):
            setting.check()

        def checker(name, value):
            if isinstance(value, str):
                raise ValueError(name)

        setting = Setting(name="check_test2", checker=checker)
        with override_settings(CHECK_TEST2="not ok"):
            with pytest.raises(ValueError):
                setting.check()
        with override_settings(CHECK_TEST2=1):
            setting.check()

        class SettingNoChecker(appsettings.Setting):
            pass

        setting = SettingNoChecker(name="check_test3")
        with override_settings(CHECK_TEST3=list(range(1, 10))):
            setting.check()

        setting = appsettings.NestedSetting(
            name="check_test3", settings=dict(inner=appsettings.Setting(checker=checker))
        )
        setting.check()
        with override_settings(CHECK_TEST3={"INNER": True}):
            setting.check()
        with override_settings(CHECK_TEST3={"INNER": "AAA"}):
            with pytest.raises(ValueError):
                setting.check()

    def test_setting_raw_value(self):
        setting = appsettings.Setting(name="setting")
        setting.check()
        with pytest.raises(AttributeError):
            setting.raw_value
        with override_settings(SETTING="value"):
            setting.check()
            assert setting.raw_value == "value"

        setting.parent_setting = appsettings.Setting(name="parent_setting")
        with override_settings(PARENT_SETTING={}):
            with pytest.raises(KeyError):
                setting.raw_value
        with override_settings(PARENT_SETTING={"SETTING": "value"}):
            setting.check()
            assert setting.raw_value == "value"

    def test_boolean_setting(self):
        setting = appsettings.BooleanSetting()
        assert setting.value is True

    def test_integer_setting(self):
        setting = appsettings.IntegerSetting()
        assert setting.value == 0

    def test_positive_integer_setting(self):
        setting = appsettings.PositiveIntegerSetting()
        assert setting.value == 0

    def test_float_setting(self):
        setting = appsettings.FloatSetting()
        assert setting.value == 0.0

    def test_positive_float_setting(self):
        setting = appsettings.PositiveFloatSetting()
        assert setting.value == 0.0

    def test_iterable_setting(self):
        setting = appsettings.IterableSetting()
        assert setting.value is None

    def test_string_setting(self):
        setting = appsettings.StringSetting()
        assert setting.value == ""

    def test_list_setting(self):
        setting = appsettings.ListSetting()
        assert setting.value == []

    def test_set_setting(self):
        setting = appsettings.SetSetting()
        assert setting.value == set()

    def test_tuple_setting(self):
        setting = appsettings.TupleSetting()
        assert setting.value == ()

    def test_dict_setting(self):
        setting = appsettings.DictSetting()
        assert setting.value == {}

    def test_object_setting(self):
        setting = appsettings.ObjectSetting(name="object")
        setting.check()
        assert setting.value is None
        with override_settings(OBJECT="tests.test_appsettings.imported_object"):
            setting.check()
            assert setting.value is imported_object
        setting.default = imported_object
        setting.call_default = True
        assert setting.value == "tests.test_appsettings.SettingTestCase._imported_object2"
        setting.transform_default = True
        assert setting.value is self._imported_object2
        with override_settings(OBJECT="this_package.does_not_exist"):
            with pytest.raises(ImportError):
                assert setting.value
        with override_settings(OBJECT="tests.test_appsettings.SettingTestCase.this_function_does_not_exist"):
            with pytest.raises(AttributeError):
                assert setting.value
        with override_settings(OBJECT=""):
            assert setting.value is None
        with override_settings(OBJECT=None):
            assert setting.value is None

    def test_nested_setting(self):
        setting = appsettings.NestedSetting(settings=dict())
        assert setting.value == {}
        setting.transform_default = True
        assert setting.value == {}

        setting = appsettings.NestedSetting(
            name="setting",
            default={},
            settings=dict(
                bool1=appsettings.BooleanSetting(default=False),
                bool2=appsettings.BooleanSetting(name="bool3", default=True),
            ),
        )
        assert setting.value == {}

        with override_settings(SETTING={"BOOL3": False}):
            assert setting.value == {"bool1": False, "bool2": False}


class AppSettingsTestCase(SimpleTestCase):
    def test_instantiation(self):
        class AppConf(appsettings.AppSettings):
            setting = appsettings.Setting()

        appconf = AppConf()
        assert appconf
        assert appconf.setting == AppConf.setting.get_value()
        assert AppConf.setting is AppConf.settings["setting"]
        assert AppConf.settings is AppConf._meta.settings
        with pytest.raises(AttributeError):
            assert not AppConf.not_a_setting

        with pytest.raises(RuntimeError):
            assert not appsettings.AppSettings()

    def test_populating_name(self):
        class AppConf(appsettings.AppSettings):
            without_name = appsettings.Setting()
            with_name = appsettings.Setting(name="got_a_name")

        assert "without_name" in AppConf.settings
        assert "with_name" in AppConf.settings
        assert AppConf.settings["without_name"].name == "without_name"
        assert AppConf.settings["with_name"].name == "got_a_name"

    def test_populating_prefix(self):
        class NoMetaAppConf(appsettings.AppSettings):
            without_prefix = appsettings.Setting()
            with_prefix = appsettings.Setting(prefix="got_a_prefix")

        assert "without_prefix" in NoMetaAppConf.settings
        assert "with_prefix" in NoMetaAppConf.settings
        assert NoMetaAppConf.settings["without_prefix"].prefix == ""
        assert NoMetaAppConf.settings["with_prefix"].prefix == "got_a_prefix"

        class MetaAppConf(appsettings.AppSettings):
            without_prefix = appsettings.Setting()
            with_prefix = appsettings.Setting(prefix="got_a_prefix")

            class Meta:
                setting_prefix = "meta_prefix_"

        assert "without_prefix" in MetaAppConf.settings
        assert "with_prefix" in MetaAppConf.settings
        assert MetaAppConf.settings["without_prefix"].prefix == "meta_prefix_"
        assert MetaAppConf.settings["with_prefix"].prefix == "got_a_prefix"

    def test_full_name(self):
        class AppConf(appsettings.AppSettings):
            setting = appsettings.Setting(name="name")

            class Meta:
                setting_prefix = "prefix_"

        assert AppConf.settings["setting"].full_name == "PREFIX_NAME"

    def test_caching(self):
        class AppConf(appsettings.AppSettings):
            my_int = appsettings.IntegerSetting()

        appconf = AppConf()
        assert "my_int" not in appconf._cache
        assert appconf.my_int == 0
        assert "my_int" in appconf._cache
        assert appconf._cache["my_int"] == 0
        assert appconf.my_int == 0
        appconf.invalidate_cache()
        assert "my_int" not in appconf._cache
        with pytest.raises(AttributeError):
            assert not appconf.not_a_setting

    def test_invalidate_on_signal(self):
        class AppConf(appsettings.AppSettings):
            my_int = appsettings.IntegerSetting()

        appconf = AppConf()
        assert "my_int" not in appconf._cache
        assert appconf.my_int == 0
        assert "my_int" in appconf._cache
        assert appconf._cache["my_int"] == 0

        with override_settings(MY_INT=1):
            assert "my_int" not in appconf._cache
            assert appconf.my_int == 1
            assert "my_int" in appconf._cache
            assert appconf._cache["my_int"] == 1

        assert "my_int" not in appconf._cache
        assert appconf.my_int == 0

    def test_check(self):
        assert appsettings.AppSettings.check() is None

        class AppConf(appsettings.AppSettings):
            setting = appsettings.Setting()

        assert AppConf.check() is None

        AppConf.setting.required = True

        with pytest.raises(ImproperlyConfigured):
            assert not AppConf.check()
