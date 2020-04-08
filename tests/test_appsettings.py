"""Main test script."""
import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.test import SimpleTestCase, override_settings

import appsettings


def imported_object():
    return "tests.test_appsettings.ImportedClass._imported_object2"


class ImportedClass:
    """Mixin for tests."""

    @staticmethod
    def _imported_object2():
        return "nothing"


class SettingTestCase(SimpleTestCase):
    NOT_A_CALLABLE = {}  # type: dict

    def setUp(self):
        self.message_required = "%s setting is required and"
        self.message_missing_item = "%s setting is missing required item"
        self.message_no_attr = "has no attribute '%s'"

    def test_setting(self):
        setting = appsettings.Setting(name="simple")
        assert setting.name == "simple"
        assert setting.full_name == "SIMPLE"
        assert setting.default_value is None
        assert setting.value is None
        assert setting.get_value() is None
        assert setting.validators == []
        setting.check()
        with pytest.raises(AttributeError, match="SIMPLE"):
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
        with pytest.raises(ImproperlyConfigured, match=self.message_required % setting.full_name):
            assert setting.value
        assert setting.default_value

        setting.parent_setting = appsettings.NestedDictSetting(settings={}, name="parent_setting")
        with override_settings(PARENT_SETTING={}):
            with pytest.raises(
                ImproperlyConfigured, match=self.message_missing_item % setting.parent_setting.full_name
            ):
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
            with pytest.raises(
                ImproperlyConfigured, match="Setting INQUISITOR has an invalid value:.*You're not worthy!"
            ):
                setting.check()

        assert validator.mock_calls == [mock.call(mock.sentinel.lister)]

    def test_setting_custom_validate(self):
        # Test custom validate method
        class TestSetting(appsettings.Setting):
            def validate(self, value):
                raise ValidationError("You're not worthy!")

        setting = TestSetting(name="INQUISITOR")

        with self.settings(INQUISITOR=mock.sentinel.lister):
            with pytest.raises(
                ImproperlyConfigured, match="Setting INQUISITOR has an invalid value:.*You're not worthy!"
            ):
                setting.check()

    def test_setting_raw_value(self):
        setting = appsettings.Setting(name="setting")
        setting.check()
        with pytest.raises(AttributeError):
            setting.raw_value
        with override_settings(SETTING="value"):
            setting.check()
            assert setting.raw_value == "value"

        setting.parent_setting = appsettings.NestedDictSetting(settings={}, name="parent_setting")
        with override_settings(PARENT_SETTING={}):
            with pytest.raises(KeyError):
                setting.raw_value
        with override_settings(PARENT_SETTING={"SETTING": "value"}):
            setting.check()
            assert setting.raw_value == "value"

        setting.parent_setting = appsettings.NestedListSetting(inner_setting=setting, name="parent_setting")
        setting.nested_list_index = 0
        with override_settings(PARENT_SETTING=[]):
            with pytest.raises(IndexError):
                setting.raw_value
        with override_settings(PARENT_SETTING=["value"]):
            setting.check()
            assert setting.raw_value == "value"

    @mock.patch.dict(os.environ, {"PREFERENCE_SETTING": '"__ENV__"'})
    def test_preference_of_environ_values(self):
        setting = appsettings.Setting(name="preference_setting")
        with override_settings(PREFERENCE_SETTING="__OVER__"):
            setting.check()
            assert setting.value == "__ENV__"

    @mock.patch.dict(os.environ, {"SETTING": '{"key": ["v", "a", "l"]}'})
    def test_json_from_environ_value(self):
        setting = appsettings.Setting(name="setting")
        setting.check()
        assert setting.value == {"key": ["v", "a", "l"]}


class BooleanSettingTestCase(SimpleTestCase):
    """BooleanSetting tests."""

    def test_boolean_setting(self):
        setting = appsettings.BooleanSetting()
        assert setting.value is True

    @mock.patch.dict(os.environ, {"SETTING": "true"})
    def test_json_boolean_setting_from_environ_true_value(self):
        setting = appsettings.BooleanSetting(name="setting")
        setting.check()
        assert setting.value is True

    @mock.patch.dict(os.environ, {"BOOL_LOWER": "true", "BOOL_UPPER": "TRUE", "BOOL_NUM": "1", "BOOL_WORD": "yes"})
    def test_string_boolean_setting_from_environ_true_value(self):
        bool_lower = appsettings.BooleanSetting(name="bool_lower")
        bool_lower.check()
        assert bool_lower.value is True

        bool_upper = appsettings.BooleanSetting(name="bool_upper")
        bool_upper.check()
        assert bool_upper.value is True

        bool_num = appsettings.BooleanSetting(name="bool_num")
        bool_num.check()
        assert bool_num.value is True

        bool_word = appsettings.BooleanSetting(name="bool_word")
        bool_word.check()
        assert bool_word.value is True

    @mock.patch.dict(os.environ, {"BOOL_LOWER": "false", "BOOL_UPPER": "FALSE", "BOOL_NUM": "0", "BOOL_WORD": "no"})
    def test_string_boolean_setting_from_environ_false_value(self):
        bool_lower = appsettings.BooleanSetting(name="bool_lower")
        bool_lower.check()
        assert bool_lower.value is False

        bool_upper = appsettings.BooleanSetting(name="bool_upper")
        bool_upper.check()
        assert bool_upper.value is False

        bool_num = appsettings.BooleanSetting(name="bool_num")
        bool_num.check()
        assert bool_num.value is False

        bool_word = appsettings.BooleanSetting(name="bool_word")
        bool_word.check()
        assert bool_word.value is False

    @mock.patch.dict(os.environ, {"BOOL_SETTING": "invalid"})
    def test_string_boolean_setting_from_environ_invalid_value(self):
        bool_setting = appsettings.BooleanSetting(name="bool_setting")
        with pytest.raises(ValueError, match="Invalid boolean setting BOOL_SETTING"):
            bool_setting.check()


class IntegerSettingTestCase(SimpleTestCase):
    """IntegerSetting tests."""

    def test_integer_setting(self):
        setting = appsettings.IntegerSetting()
        assert setting.value == 0

    @mock.patch.dict(os.environ, {"SETTING": "123"})
    def test_integer_setting_from_environ_value(self):
        setting = appsettings.IntegerSetting(name="setting")
        setting.check()
        assert setting.value == 123
        assert type(setting.value) is int


class PositiveIntegerSettingTestCase(SimpleTestCase):
    """PositiveIntegerSetting tests."""

    def test_positive_integer_setting(self):
        setting = appsettings.PositiveIntegerSetting()
        assert setting.value == 0


class FloatSettingTestCase(SimpleTestCase):
    """FloatSetting tests."""

    def test_float_setting(self):
        setting = appsettings.FloatSetting()
        assert setting.value == 0.0

    @mock.patch.dict(os.environ, {"SETTING": "123.456"})
    def test_float_setting_from_environ_value(self):
        setting = appsettings.FloatSetting(name="setting")
        setting.check()
        assert setting.value == 123.456
        assert type(setting.value) is float


class PositiveFloatSettingTestCase(SimpleTestCase):
    """PositiveFloatSetting tests."""

    def test_positive_float_setting(self):
        setting = appsettings.PositiveFloatSetting()
        assert setting.value == 0.0


class IterableSettingTestCase(SimpleTestCase):
    """IterableSetting tests."""

    def test_iterable_setting(self):
        setting = appsettings.IterableSetting()
        assert setting.value is None

    @mock.patch.dict(os.environ, {"SETTING": "[1, 2, 3]"})
    def test_iterable_setting_from_environ_json_value(self):
        setting = appsettings.IterableSetting(name="setting")
        setting.check()
        assert setting.value == [1, 2, 3]

    @mock.patch.dict(os.environ, {"SETTING": "1:2:3"})
    def test_iterable_setting_from_environ_delimiter_value(self):
        setting = appsettings.IterableSetting(name="setting")
        setting.check()
        assert setting.value == ["1", "2", "3"]

    @mock.patch.dict(os.environ, {"SETTING": "1-2-3"})
    def test_iterable_setting_from_environ_delimiter_value_with_item_type(self):
        setting = appsettings.IterableSetting(name="setting", item_type=int, delimiter="-")
        setting.check()
        assert setting.value == [1, 2, 3]


class StringSettingTestCase(SimpleTestCase):
    """StringSetting tests."""

    def test_string_setting(self):
        setting = appsettings.StringSetting()
        assert setting.value == ""

    @mock.patch.dict(os.environ, {"SETTING": '"json-string"'})
    def test_string_setting_from_environ_json_value(self):
        setting = appsettings.StringSetting(name="setting")
        setting.check()
        assert setting.value == "json-string"

    @mock.patch.dict(os.environ, {"SETTING": "pure-string"})
    def test_string_setting_from_environ_pure_value(self):
        setting = appsettings.StringSetting(name="setting")
        setting.check()
        assert setting.value == "pure-string"


class ListSettingTestCase(SimpleTestCase):
    """ListSetting tests."""

    def test_list_setting(self):
        setting = appsettings.ListSetting()
        assert setting.value == []


class SetSettingTestCase(SimpleTestCase):
    """SetSetting tests."""

    def test_set_setting(self):
        setting = appsettings.SetSetting()
        assert setting.value == set()

    @mock.patch.dict(os.environ, {"SETTING": "a:b:b:b:c"})
    def test_set_setting_from_environ_value(self):
        setting = appsettings.SetSetting(name="setting")
        setting.check()
        assert setting.value == {"a", "b", "c"}


class TupleSettingTestCase(SimpleTestCase):
    """TupleSetting tests."""

    def test_tuple_setting(self):
        setting = appsettings.TupleSetting()
        assert setting.value == ()

    @mock.patch.dict(os.environ, {"SETTING": "a:b:c"})
    def test_tuple_setting_from_environ_value(self):
        setting = appsettings.TupleSetting(name="setting")
        setting.check()
        assert setting.value == ("a", "b", "c")


class DictSettingTestCase(SimpleTestCase):
    """DictSetting tests."""

    def test_dict_setting(self):
        setting = appsettings.DictSetting()
        assert setting.value == {}

    @mock.patch.dict(os.environ, {"SETTING": '{"a": "A", "b": "B"}'})
    def test_dict_setting_from_environ_json_value(self):
        setting = appsettings.DictSetting(name="setting")
        setting.check()
        assert setting.value == {"a": "A", "b": "B"}

    @mock.patch.dict(os.environ, {"SETTING": "a=A b=B"})
    def test_dict_setting_from_environ_delimiter_value(self):
        setting = appsettings.DictSetting(name="setting")
        setting.check()
        assert setting.value == {"a": "A", "b": "B"}

    @mock.patch.dict(os.environ, {"SETTING": "a:1--b:2"})
    def test_dict_setting_from_environ_delimiter_value_with_types(self):
        setting = appsettings.DictSetting(
            name="setting", outer_delimiter="--", inner_delimiter=":", key_type=str, value_type=int
        )
        setting.check()
        assert setting.value == {"a": 1, "b": 2}


class ObjectSettingTestCase(SimpleTestCase):
    """ObjectSetting tests."""

    def test_object_setting(self):
        setting = appsettings.ObjectSetting(name="object")
        setting.check()
        assert setting.value is None
        with override_settings(OBJECT="tests.test_appsettings.imported_object"):
            setting.check()
            assert setting.value is imported_object
        setting.default = imported_object
        setting.call_default = True
        assert setting.value == "tests.test_appsettings.ImportedClass._imported_object2"
        setting.transform_default = True
        assert setting.value is ImportedClass._imported_object2
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

    @mock.patch.dict(os.environ, {"SETTING": "tests.test_appsettings.imported_object"})
    def test_object_setting_from_environ_value(self):
        setting = appsettings.ObjectSetting(name="setting")
        setting.check()
        assert setting.value is imported_object


class CallablePathSettingTestCase(SimpleTestCase):
    """CallablePathSetting tests."""

    def test_callable_path_setting(self):
        setting = appsettings.CallablePathSetting(name="callable_path")
        setting.check()
        assert setting.value is None
        with override_settings(CALLABLE_PATH="tests.test_appsettings.imported_object"):
            setting.check()
            assert setting.value is imported_object
        with override_settings(CALLABLE_PATH="tests.test_appsettings.SettingTestCase.NOT_A_CALLABLE"):
            with pytest.raises(ImproperlyConfigured):
                setting.check()
        with override_settings(CALLABLE_PATH=None):
            with pytest.raises(ImproperlyConfigured):
                setting.check()


class NestedDictSettingTestCase(SimpleTestCase):
    """NestedDictSetting tests."""

    def test_nested_setting(self):
        setting = appsettings.NestedDictSetting(settings=dict())
        assert setting.value == {}
        setting.transform_default = True
        assert setting.value == {}

        setting = appsettings.NestedDictSetting(
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

    def test_nested_dict_setting_not_required_anything(self):
        outer_setting = appsettings.NestedDictSetting(
            name="outer_setting", settings=dict(inner_setting=appsettings.StringSetting(default="Default"))
        )

        # Not passed anything
        outer_setting.check()
        assert len(outer_setting.value.items()) == 0
        assert outer_setting.value.get("inner_setting") is None

        # Pass outer setting
        with override_settings(OUTER_SETTING={"INNER_FAKE_SETTING": "Fake setting value"}):
            outer_setting.check()
            assert len(outer_setting.value.items()) == 1
            assert outer_setting.value.get("inner_setting") == "Default"

        # Pass inner setting as well
        with override_settings(OUTER_SETTING={"INNER_SETTING": "Value"}):
            outer_setting.check()
            assert len(outer_setting.value.items()) == 1
            assert outer_setting.value.get("inner_setting") == "Value"

    def test_nested_dict_setting_required_outer_setting(self):
        outer_setting = appsettings.NestedDictSetting(
            name="outer_setting",
            required=True,
            settings=dict(inner_setting=appsettings.StringSetting(default="Default")),
        )

        # Not passed anything
        with pytest.raises(ImproperlyConfigured):
            outer_setting.check()

        # Pass outer setting
        with override_settings(OUTER_SETTING={"INNER_FAKE_SETTING": "Fake setting value"}):
            outer_setting.check()
            assert len(outer_setting.value.items()) == 1
            assert outer_setting.value.get("inner_setting") == "Default"

        # Pass inner setting as well
        with override_settings(OUTER_SETTING={"INNER_SETTING": "Value"}):
            outer_setting.check()
            assert len(outer_setting.value.items()) == 1
            assert outer_setting.value.get("inner_setting") == "Value"

    def test_nested_dict_setting_required_inner_setting(self):
        outer_setting = appsettings.NestedDictSetting(
            name="outer_setting", settings=dict(inner_setting=appsettings.StringSetting(required=True))
        )

        # Not passed anything
        outer_setting.check()
        assert len(outer_setting.value.items()) == 0
        assert outer_setting.value.get("inner_setting") is None

        # Pass outer setting
        with override_settings(OUTER_SETTING={"INNER_FAKE_SETTING": "Fake setting value"}):
            with pytest.raises(ImproperlyConfigured):
                outer_setting.check()

        # Pass inner setting as well
        with override_settings(OUTER_SETTING={"INNER_SETTING": "Value"}):
            outer_setting.check()
            assert len(outer_setting.value.items()) == 1
            assert outer_setting.value.get("inner_setting") == "Value"

    def test_nested_dict_setting_required_both_inner_and_outer_setting(self):
        outer_setting = appsettings.NestedDictSetting(
            name="outer_setting", required=True, settings=dict(inner_setting=appsettings.StringSetting(required=True))
        )

        # Not passed anything
        with pytest.raises(ImproperlyConfigured):
            outer_setting.check()

        # Pass outer setting
        with override_settings(OUTER_SETTING={"INNER_FAKE_SETTING": "Fake setting value"}):
            with pytest.raises(ImproperlyConfigured):
                outer_setting.check()

        # Pass inner setting as well
        with override_settings(OUTER_SETTING={"INNER_SETTING": "Value"}):
            outer_setting.check()
            assert len(outer_setting.value.items()) == 1
            assert outer_setting.value.get("inner_setting") == "Value"

    @mock.patch.dict(os.environ, {"SETTING": '{"A": "A", "B": "B"}'})
    def test_nested_dict_setting_from_environ_value(self):
        setting = appsettings.NestedDictSetting(
            settings=dict(a=appsettings.Setting(), b=appsettings.Setting(),), name="setting"
        )
        setting.check()
        assert setting.value == {"a": "A", "b": "B"}

    @mock.patch.dict(os.environ, {"SETTING": '{"A": "A", "B": "B"}', "A": "Fake A", "B": "Fake B"})
    def test_parent_setting_precedence_over_environ_value(self):
        setting = appsettings.NestedDictSetting(
            settings=dict(a=appsettings.StringSetting(), b=appsettings.StringSetting(),), name="setting"
        )
        setting.check()
        assert setting.value["a"] == "A"
        assert setting.value["b"] == "B"


class NestedListSettingTestCase(SimpleTestCase):
    """NestedListSetting tests."""

    def test_nested_list_setting(self):
        setting = appsettings.NestedListSetting(name="setting", default=[], inner_setting=appsettings.IntegerSetting())
        setting.check()
        assert setting.value == []

        with override_settings(SETTING=[0, 1, 2]):
            setting.check()
            assert setting.value == (0, 1, 2)
        with override_settings(SETTING=[0, "1", 2]):
            with pytest.raises(ImproperlyConfigured):
                setting.check()

        setting = appsettings.NestedListSetting(
            name="setting",
            default=["tests.test_appsettings.imported_object"],
            transform_default=True,
            inner_setting=appsettings.ObjectSetting(),
        )
        setting.check()
        assert setting.value == (imported_object,)
        with override_settings(
            SETTING=[
                "tests.test_appsettings.imported_object",
                "tests.test_appsettings.ImportedClass._imported_object2",
            ]
        ):
            setting.check()
            assert setting.value == (imported_object, ImportedClass._imported_object2)

    def test_nested_nested_list_setting(self):
        setting = appsettings.NestedListSetting(
            name="setting",
            default=[],
            inner_setting=appsettings.NestedListSetting(
                name="inner", default=[], inner_setting=appsettings.IntegerSetting()
            ),
        )
        setting.check()
        assert setting.value == []
        assert setting.inner_setting.name == "inner"
        with override_settings(SETTING=([1, 2, 3], [4, 5])):
            setting.check()
            assert setting.value == ((1, 2, 3), (4, 5))
        with override_settings(SETTING=[[1, 2, 3], ["x", 5]]):
            with pytest.raises(ImproperlyConfigured):
                setting.check()

        setting = appsettings.NestedListSetting(
            name="setting",
            inner_setting=appsettings.NestedListSetting(
                inner_setting=appsettings.NestedListSetting(inner_setting=appsettings.ObjectSetting())
            ),
        )
        assert setting.inner_setting.name == "setting"
        with override_settings(
            SETTING=[
                (
                    ["tests.test_appsettings.imported_object"],
                    ["tests.test_appsettings.ImportedClass._imported_object2"],
                )
            ]
        ):
            setting.check()
            assert setting.value == (((imported_object,), (ImportedClass._imported_object2,)),)
        with override_settings(
            SETTING=[[["tests.test_appsettings.imported_object"], ["tests.test_appsettings.object_does_not_exist"]]]
        ):
            with pytest.raises(AttributeError):
                assert setting.value

    def test_nested_list_in_nested_dict_setting(self):
        setting = appsettings.NestedDictSetting(
            name="setting",
            default={},
            settings=dict(
                select=appsettings.NestedListSetting(
                    name="pick", default=[1], inner_setting=appsettings.IntegerSetting()
                )
            ),
        )
        setting.check()
        assert setting.value == {}
        with override_settings(SETTING={}):
            setting.check()
            assert setting.value == {"select": [1]}
        with override_settings(SETTING={"PICK": [2]}):
            setting.check()
            assert setting.value == {"select": (2,)}
        with override_settings(SETTING={"PICK": ["xyz"]}):
            with pytest.raises(ImproperlyConfigured):
                setting.check()


class FileSettingTestCase(SimpleTestCase):
    def test_file_setting_string(self):
        setting = appsettings.FileSetting(name="file")
        with tempfile.NamedTemporaryFile() as fd:
            with override_settings(FILE=fd.name):
                setting.check()
                assert isinstance(setting.value, Path)
                assert setting.value.samefile(fd.name)

    def test_file_setting_path(self):
        setting = appsettings.FileSetting(name="file")
        with tempfile.NamedTemporaryFile() as fd:
            with override_settings(FILE=Path(fd.name)):
                setting.check()
                assert isinstance(setting.value, Path)
                assert setting.value.samefile(fd.name)

    def test_file_setting_with_directory(self):
        setting = appsettings.FileSetting(name="file")
        with tempfile.TemporaryDirectory() as td_name:
            with override_settings(FILE=Path(td_name)):
                setting.check()
                assert isinstance(setting.value, Path)
                assert setting.value.samefile(td_name)


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
