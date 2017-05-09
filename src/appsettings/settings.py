# -*- coding: utf-8 -*-

"""Settings module."""

import importlib

from django.conf import settings


def _import(complete_path):
    module_name = '.'.join(complete_path.split('.')[:-1])
    module_obj = importlib.import_module(name=module_name)
    function_or_class = getattr(module_obj, complete_path.split('.')[-1])
    return function_or_class


def _type_checker(t):
    def check(name, value):
        """Check value for given type."""
        if not isinstance(value, t):
            raise ValueError('%s must be %s, not %s' % (
                name, t, value.__class__))
    check.__name__ = 'check_%s' % t.__name__
    return check


def _type_tuple_checker(ty, tu):
    # pylama:ignore=C0111
    def check(name, value):
        if not isinstance(value, tu):
            raise ValueError('%s must be %s, not %s' % (
                name, tu, value.__class__))
        if not all(isinstance(o, ty) for o in value):
            raise ValueError('All elements of %s must be %s' % (name, ty))
    check.__name__ = 'check_%s_%s' % (ty.__name__, tu.__name__)
    return check


check_string = _type_checker(str)
check_integer = _type_checker(int)
check_boolean = _type_checker(bool)
check_float = _type_checker(float)
check_list = _type_checker(list)
check_dict = _type_checker(dict)
check_set = _type_checker(set)


def check_positive_integer(name, value):
    """Check positive integer value."""
    check_integer(name, value)
    if value < 0:
        raise ValueError('%s must be positive or zero' % name)


def check_positive_float(name, value):
    """Check positive integer value."""
    check_float(name, value)
    if value < 0.0:
        raise ValueError('%s must be positive or zero' % name)


def check_object_path(name, value):
    """Check positive integer value."""
    check_string(name, value)
    # TODO: maybe check that the object actually exists,
    # see http://stackoverflow.com/questions/14050281


check_string_list = _type_tuple_checker(str, list)
check_string_set = _type_tuple_checker(str, set)
check_integer_list = _type_tuple_checker(int, list)
check_integer_set = _type_tuple_checker(int, set)
check_boolean_list = _type_tuple_checker(bool, list)
check_boolean_set = _type_tuple_checker(bool, set)
check_float_list = _type_tuple_checker(float, list)
check_float_set = _type_tuple_checker(float, set)


class Setting(object):
    """
    Generic setting class.

    Serve as base class for more specific setting types.
    """

    def __init__(self,
                 name=None,
                 default=None,
                 required=False,
                 prefix=None):
        """
        Initialization method.

        Args:
            name (str): name of the setting.
            default (obj): default value given to the setting.
            required (bool): whether setting is required or not.
            prefix (str):
                prefix of the setting.
                Will override ``AppSettings.Meta`` prefix.
        """
        self.name = name
        self.default = default
        self.required = required
        self.prefix = prefix

    @property
    def full_name(self):
        return self.prefix.upper() + self.name.upper()

    def get_raw(self):
        """Get the setting from ``django.conf.settings``."""
        try:
            return getattr(settings, self.full_name)
        except AttributeError:
            if self.required:
                raise AttributeError(
                    'setting %s is required.' % self.full_name)
            return self.default

    def get(self):
        """Get the setting and return it transformed."""
        return self.transform()

    def check(self):
        """Check the setting. Raise exception if incorrect."""

        self.get_raw()

    def transform(self):
        """Get the setting and return it transformed."""
        return self.get_raw()


def _type_setting(cls_name, check_func, default_value):
    class _Setting(Setting):
        def __init__(self,
                     name=None,
                     default=default_value,
                     required=False,
                     prefix=None):
            super(_Setting, self).__init__(
                name, default, required, prefix)

        def check(self):
            value = self.get_raw()
            if value != self.default:
                check_func(self.full_name, value)
    _Setting.__name__ = '%sSetting' % cls_name
    return _Setting


StringSetting = _type_setting('String', check_string, '')
IntegerSetting = _type_setting('Integer', check_integer, 0)
PositiveIntegerSetting = _type_setting('PositiveInteger', check_positive_integer, 0)  # noqa
BooleanSetting = _type_setting('Boolean', check_boolean, False)
FloatSetting = _type_setting('Float', check_float, 0.0)
PositiveFloatSetting = _type_setting('PositiveFloat', check_positive_float, 0.0)  # noqa
ListSetting = _type_setting('List', check_list, [])
SetSetting = _type_setting('Set', check_set, ())
DictSetting = _type_setting('Dict', check_dict, {})

StringListSetting = _type_setting('StringList', check_string_list, [])
StringSetSetting = _type_setting('StringSet', check_string_set, ())
IntegerListSetting = _type_setting('IntegerList', check_integer_list, [])
IntegerSetSetting = _type_setting('IntegerSet', check_integer_set, ())
BooleanListSetting = _type_setting('BooleanList', check_boolean_list, [])
BooleanSetSetting = _type_setting('BooleanSet', check_boolean_set, ())
FloatListSetting = _type_setting('FloatList', check_float_list, [])
FloatSetSetting = _type_setting('FloatSet', check_float_set, ())


class ImportedObjectSetting(Setting):
    """Setting to import an object given its Python path (a.b.c)."""

    def __init__(self,
                 name=None,
                 default=None,
                 required=False,
                 prefix=None):
        """
        Initialization method.

        Args:
            name (str): the name of the setting.
            default (obj): the default value given to the setting.
            required (bool): whether setting is required or not.
            checker (func): the function to check the setting value.
            transformer (func): the function to transform the setting value.
            prefix (str): the setting's prefix.
        """
        super(ImportedObjectSetting, self).__init__(
            name, default, required, prefix)

    def check(self):
        value = self.get_raw()
        if value != self.default:
            check_object_path(self.full_name, value)

    def transform(self):
        return _import(self.get_raw())
