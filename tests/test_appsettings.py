# -*- coding: utf-8 -*-

"""Main test script."""
from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase, override_settings

import pytest

import appsettings


class MainTestCase(SimpleTestCase):
    """General tests."""

    def test_instantiation(self):
        class AppConf(appsettings.AppSettings):
            setting = appsettings.Setting()
        appconf = AppConf()
        assert appconf


class TypeCheckerTestCase(SimpleTestCase):
    """Type checkers tests."""

    def setUp(self):
        self.name = 'setting'
        self.message = "setting must be %s, not %s"
        self.message_greater = 'setting must be greater or equal %s'
        self.message_less = 'setting must be less or equal %s'
        self.message_longer = 'setting must be longer than %s (or equal)'
        self.message_shorter = 'setting must be shorter than %s (or equal)'
        self.message_empty = 'setting must not be empty'
        self.message_items = 'All elements of setting must be %s'
        self.message_keys = 'All keys of setting must be %s'
        self.message_values = 'All values of setting must be %s'

    def test_type_checker(self):
        checker = appsettings.TypeChecker(int)
        checker(self.name, 0)
        with pytest.raises(ValueError) as e:
            checker(self.name, None)
        assert self.message % (checker.base_type, type(None)) in str(e.value)

    def test_boolean_type_checker(self):
        checker = appsettings.BooleanTypeChecker()
        checker(self.name, True)
        with pytest.raises(ValueError) as e:
            checker(self.name, None)
        assert self.message % (checker.base_type, type(None)) in str(e.value)

    def test_integer_type_checker(self):
        checker = appsettings.IntegerTypeChecker()
        checker(self.name, 0)
        with pytest.raises(ValueError) as e:
            checker(self.name, None)
        assert self.message % (checker.base_type, type(None)) in str(e.value)

        checker.minimum = 1
        checker(self.name, 1)
        with pytest.raises(ValueError) as e:
            checker(self.name, 0)
        assert self.message_greater % checker.minimum in str(e.value)

        checker.maximum = 2
        checker(self.name, 2)
        with pytest.raises(ValueError) as e:
            checker(self.name, 3)
        assert self.message_less % checker.maximum in str(e.value)

    def test_float_type_checker(self):
        checker = appsettings.FloatTypeChecker()
        checker(self.name, 0.0)
        with pytest.raises(ValueError) as e:
            checker(self.name, None)
        assert self.message % (checker.base_type, type(None)) in str(e.value)

        checker.minimum = 1.1
        checker(self.name, 1.1)
        with pytest.raises(ValueError) as e:
            checker(self.name, 0.1)
        assert self.message_greater % checker.minimum in str(e.value)

        checker.maximum = 2.1
        checker(self.name, 2.1)
        with pytest.raises(ValueError) as e:
            checker(self.name, 3.1)
        assert self.message_less % checker.maximum in str(e.value)

    def test_string_type_checker(self):
        checker = appsettings.StringTypeChecker()
        checker(self.name, '')
        with pytest.raises(ValueError) as e:
            checker(self.name, None)
        assert self.message % (checker.base_type, type(None)) in str(e.value)

        checker.min_length = 1
        checker(self.name, '1')
        with pytest.raises(ValueError) as e:
            checker(self.name, '')
        assert self.message_longer % checker.min_length in str(e.value)

        checker.max_length = 2
        checker(self.name, '12')
        with pytest.raises(ValueError) as e:
            checker(self.name, '123')
        assert self.message_shorter % checker.max_length in str(e.value)

        checker.min_length = None
        checker.max_length = None
        checker.empty = False
        with pytest.raises(ValueError) as e:
            checker(self.name, '')
        assert self.message_empty in str(e.value)

    def test_list_type_checker(self):
        checker = appsettings.ListTypeChecker()
        checker(self.name, list())
        with pytest.raises(ValueError) as e:
            checker(self.name, None)
        assert self.message % (checker.base_type, type(None)) in str(e.value)

        checker.item_type = str
        checker(self.name, list())  # empty
        checker(self.name, ['ding'])  # one item
        checker(self.name, ['ding', 'dong'])  # multiple items
        with pytest.raises(ValueError) as e:
            checker(self.name, [None])
        assert self.message_items % checker.item_type in str(e.value)
        with pytest.raises(ValueError) as e:
            checker(self.name, ['ding', None])  # not all
        assert self.message_items % checker.item_type in str(e.value)

    def test_set_type_checker(self):
        checker = appsettings.SetTypeChecker()
        checker(self.name, set())
        with pytest.raises(ValueError) as e:
            checker(self.name, None)
        assert self.message % (checker.base_type, type(None)) in str(e.value)

    def test_tuple_type_checker(self):
        checker = appsettings.TupleTypeChecker()
        checker(self.name, tuple())
        with pytest.raises(ValueError) as e:
            checker(self.name, None)
        assert self.message % (checker.base_type, type(None)) in str(e.value)

    def test_range_type_checker(self):
        checker = appsettings.RangeTypeChecker()
        checker(self.name, range(0))
        with pytest.raises(ValueError) as e:
            checker(self.name, None)
        assert self.message % (checker.base_type, type(None)) in str(e.value)

    def test_dict_type_checker(self):
        checker = appsettings.DictTypeChecker()
        checker(self.name, dict())
        with pytest.raises(ValueError) as e:
            checker(self.name, None)
        assert self.message % (checker.base_type, type(None)) in str(e.value)

        checker.min_length = 1
        checker(self.name, {1: 1})
        with pytest.raises(ValueError) as e:
            checker(self.name, {})
        assert self.message_longer % checker.min_length in str(e.value)

        checker.max_length = 2
        checker(self.name, {1: 1, 2: 2})
        with pytest.raises(ValueError) as e:
            checker(self.name, {1: 1, 2: 2, 3: 3})
        assert self.message_shorter % checker.max_length in str(e.value)

        checker.min_length = None
        checker.max_length = None
        checker.empty = False
        with pytest.raises(ValueError) as e:
            checker(self.name, {})
        assert self.message_empty in str(e.value)
        checker = appsettings.DictTypeChecker()

        checker.key_type = int
        checker.value_type = str
        checker(self.name, {0: '0'})  # one pair
        checker(self.name, {0: '0', 1: '1'})  # multiple pairs
        with pytest.raises(ValueError) as e:
            checker(self.name, {None: None})  # both key and value wrong
        assert self.message_keys % checker.key_type in str(e.value)
        with pytest.raises(ValueError) as e:
            checker(self.name, {None: '0'})  # only key wrong
        assert self.message_keys % checker.key_type in str(e.value)
        with pytest.raises(ValueError) as e:
            checker(self.name, {0: None})  # only value wrong
        assert self.message_values % checker.value_type in str(e.value)
        with pytest.raises(ValueError) as e:
            checker(self.name, {0: '0', '1': '1'})  # not all keys
        assert self.message_keys % checker.key_type in str(e.value)
        with pytest.raises(ValueError) as e:
            checker(self.name, {0: '0', 1: 1})  # not all values
        assert self.message_values % checker.value_type in str(e.value)
