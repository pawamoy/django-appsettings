# -*- coding: utf-8 -*-

"""Settings module."""

import importlib

from django.conf import settings


# TODO: allow callables for Setting's default arg (can't put mutable objects)?

# Basic type checkers ---------------------------------------------------------
class TypeChecker(object):
    def __init__(self, base_type):
        self.base_type = base_type

    def __call__(self, name, value):
        if not isinstance(value, self.base_type):
            raise ValueError('%s must be %s, not %s' % (
                name, self.base_type, value.__class__))


class StringTypeChecker(TypeChecker):
    def __init__(self):
        super(StringTypeChecker, self).__init__(str)


class IntegerTypeChecker(TypeChecker):
    def __init__(self):
        super(IntegerTypeChecker, self).__init__(int)


class BooleanTypeChecker(TypeChecker):
    def __init__(self):
        super(BooleanTypeChecker, self).__init__(bool)


class FloatTypeChecker(TypeChecker):
    def __init__(self):
        super(FloatTypeChecker, self).__init__(float)


class ListTypeChecker(TypeChecker):
    def __init__(self):
        super(ListTypeChecker, self).__init__(list)


class DictTypeChecker(TypeChecker):
    def __init__(self):
        super(DictTypeChecker, self).__init__(dict)


class SetTypeChecker(TypeChecker):
    def __init__(self):
        super(SetTypeChecker, self).__init__(set)


class PositiveIntegerTypeChecker(IntegerTypeChecker):
    def __call__(self, name, value):
        super(PositiveIntegerTypeChecker, self).__call__(name, value)
        if value < 0:
            raise ValueError('%s must be positive or zero' % name)


class PositiveFloatTypeChecker(IntegerTypeChecker):
    def __call__(self, name, value):
        super(PositiveFloatTypeChecker, self).__call__(name, value)
        if value < 0.0:
            raise ValueError('%s must be positive or zero' % name)


# Tuple type checkers ---------------------------------------------------------
class TupleTypeChecker(TypeChecker):
    def __init__(self, tuple_type, item_type):
        super(TupleTypeChecker, self).__init__(tuple_type)
        self.item_type = item_type

    def __call__(self, name, value):
        super(TupleTypeChecker, self).__call__(name, value)
        if not all(isinstance(o, self.item_type) for o in value):
            raise ValueError('All elements of %s must be %s' % (
                name, self.item_type))


class StringListTypeChecker(TupleTypeChecker):
    def __init__(self):
        super(StringListTypeChecker, self).__init__(str, list)


class StringSetTypeChecker(TupleTypeChecker):
    def __init__(self):
        super(StringSetTypeChecker, self).__init__(str, set)


class IntegerListTypeChecker(TupleTypeChecker):
    def __init__(self):
        super(IntegerListTypeChecker, self).__init__(int, list)


class IntegerSetTypeChecker(TupleTypeChecker):
    def __init__(self):
        super(IntegerSetTypeChecker, self).__init__(int, set)


class BooleanListTypeChecker(TupleTypeChecker):
    def __init__(self):
        super(BooleanListTypeChecker, self).__init__(bool, list)


class BooleanSetTypeChecker(TupleTypeChecker):
    def __init__(self):
        super(BooleanSetTypeChecker, self).__init__(bool, set)


class FloatListTypeChecker(TupleTypeChecker):
    def __init__(self):
        super(FloatListTypeChecker, self).__init__(float, list)


class FloatSetTypeChecker(TupleTypeChecker):
    def __init__(self):
        super(FloatSetTypeChecker, self).__init__(float, set)


# Dict type checkers ----------------------------------------------------------
class DictKeyValueTypeChecker(DictTypeChecker):
    def __init__(self, key_type, value_type):
        super(DictKeyValueTypeChecker, self).__init__()
        self.key_type = key_type
        self.value_type = value_type

    def __call__(self, name, value):
        super(DictKeyValueTypeChecker, self).__call__(name, value)
        if not all(isinstance(o, self.key_type) for o in value.keys()):
            raise ValueError('All keys of %s must be %s' % (
                name, self.key_type))
        if not all(isinstance(o, self.value_type) for o in value.values()):
            raise ValueError('All values of %s must be %s' % (
                name, self.value_type))


# Complex type checkers -------------------------------------------------------
class ObjectTypeChecker(StringTypeChecker):
    # TODO: maybe check that the object actually exists,
    # see http://stackoverflow.com/questions/14050281
    pass


# Basic settings --------------------------------------------------------------
class Setting(object):
    """
    Generic setting class.

    Serve as base class for more specific setting types.
    """

    def __init__(self,
                 name='',
                 default=None,
                 required=False,
                 prefix='',
                 checker=lambda n, v: None):
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
        self.checker = checker

    @property
    def full_name(self):
        return self.prefix.upper() + self.name.upper()

    @property
    def raw_value(self):
        """Get the setting from ``django.conf.settings``."""
        try:
            return getattr(settings, self.full_name)
        except AttributeError:
            if self.required:
                raise AttributeError(
                    'setting %s is required.' % self.full_name)
            return self.default

    @property
    def value(self):
        """Get the setting and return it transformed."""
        return self.get_value()

    def get_value(self):
        return self.transform()

    def check(self):
        """Check the setting. Raise exception if incorrect."""
        self.checker(self.full_name, self.raw_value)

    def transform(self):
        """Get the setting and return it transformed."""
        return self.raw_value


class StringSetting(Setting):
    def __init__(self, name='', default='', required=False, prefix=''):
        super(StringSetting, self).__init__(
            name, default, required, prefix,
            checker=StringTypeChecker())


class IntegerSetting(Setting):
    def __init__(self, name='', default=0, required=False, prefix=''):
        super(IntegerSetting, self).__init__(
            name, default, required, prefix,
            checker=IntegerTypeChecker())


class PositiveIntegerSetting(Setting):
    def __init__(self, name='', default=0, required=False, prefix=''):
        super(PositiveIntegerSetting, self).__init__(
            name, default, required, prefix,
            checker=PositiveIntegerTypeChecker())


class BooleanSetting(Setting):
    def __init__(self, name='', default=True, required=False, prefix=''):
        super(BooleanSetting, self).__init__(
            name, default, required, prefix,
            checker=BooleanTypeChecker())


class FloatSetting(Setting):
    def __init__(self, name='', default=0.0, required=False, prefix=''):
        super(FloatSetting, self).__init__(
            name, default, required, prefix,
            checker=FloatTypeChecker())


class PositiveFloatSetting(Setting):
    def __init__(self, name='', default=0.0, required=False, prefix=''):
        super(PositiveFloatSetting, self).__init__(
            name, default, required, prefix,
            checker=PositiveFloatTypeChecker())


class ListSetting(Setting):
    def __init__(self, name='', default=None, required=False, prefix=''):
        super(ListSetting, self).__init__(
            name, default, required, prefix,
            checker=ListTypeChecker())


class SetSetting(Setting):
    def __init__(self, name='', default=None, required=False, prefix=''):
        super(SetSetting, self).__init__(
            name, default, required, prefix,
            checker=SetTypeChecker())


class DictSetting(Setting):
    def __init__(self, name='', default=None, required=False, prefix=''):
        super(DictSetting, self).__init__(
            name, default, required, prefix,
            checker=DictTypeChecker())


# Tuple settings --------------------------------------------------------------
class StringListSetting(Setting):
    def __init__(self, name='', default=None, required=False, prefix=''):
        super(StringListSetting, self).__init__(
            name, default, required, prefix,
            checker=StringListTypeChecker())


class StringSetSetting(Setting):
    def __init__(self, name='', default=None, required=False, prefix=''):
        super(StringSetSetting, self).__init__(
            name, default, required, prefix,
            checker=StringSetTypeChecker())


class IntegerListSetting(Setting):
    def __init__(self, name='', default=None, required=False, prefix=''):
        super(IntegerListSetting, self).__init__(
            name, default, required, prefix,
            checker=IntegerListTypeChecker())


class IntegerSetSetting(Setting):
    def __init__(self, name='', default=None, required=False, prefix=''):
        super(IntegerSetSetting, self).__init__(
            name, default, required, prefix,
            checker=IntegerSetTypeChecker())


class BooleanListSetting(Setting):
    def __init__(self, name='', default=None, required=False, prefix=''):
        super(BooleanListSetting, self).__init__(
            name, default, required, prefix,
            checker=BooleanListTypeChecker())


class BooleanSetSetting(Setting):
    def __init__(self, name='', default=None, required=False, prefix=''):
        super(BooleanSetSetting, self).__init__(
            name, default, required, prefix,
            checker=BooleanSetTypeChecker())


class FloatListSetting(Setting):
    def __init__(self, name='', default=None, required=False, prefix=''):
        super(FloatListSetting, self).__init__(
            name, default, required, prefix,
            checker=FloatListTypeChecker())


class FloatSetSetting(Setting):
    def __init__(self, name='', default=None, required=False, prefix=''):
        super(FloatSetSetting, self).__init__(
            name, default, required, prefix,
            checker=FloatSetTypeChecker())


# Complex settings ------------------------------------------------------------
class ObjectSetting(Setting):
    """Setting to import an object given its Python path (a.b.c)."""

    def __init__(self, name='', default=None, required=False, prefix=''):
        super(ObjectSetting, self).__init__(
            name, default, required, prefix,
            checker=ObjectTypeChecker())

    def transform(self):
        path = self.raw_value
        if path is None:
            return None
        module_name = '.'.join(path.split('.')[:-1])
        module_obj = importlib.import_module(name=module_name)
        function_or_class = getattr(module_obj, path.split('.')[-1])
        return function_or_class
