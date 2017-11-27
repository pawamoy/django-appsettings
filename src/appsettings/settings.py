# -*- coding: utf-8 -*-

"""Settings module."""

import importlib

from django.conf import settings


# Type checkers ===============================================================
class TypeChecker(object):
    def __init__(self, base_type):
        self.base_type = base_type

    def __call__(self, name, value):
        if not isinstance(value, self.base_type):
            raise ValueError('%s must be %s, not %s' % (
                name, self.base_type, value.__class__))


class BooleanTypeChecker(TypeChecker):
    def __init__(self):
        super(BooleanTypeChecker, self).__init__(bool)


class IntegerTypeChecker(TypeChecker):
    def __init__(self, minimum=None, maximum=None):
        super(IntegerTypeChecker, self).__init__(int)
        self.minimum = minimum
        self.maximum = maximum

    def __call__(self, name, value):
        super(IntegerTypeChecker, self).__call__(name, value)
        if isinstance(self.minimum, int):
            if value < self.minimum:
                raise ValueError('%s must be greater or equal %s' % (
                    name, self.minimum))
        if isinstance(self.maximum, int):
            if value > self.maximum:
                raise ValueError('%s must be less or equal %s' % (
                    name, self.maximum))


class FloatTypeChecker(TypeChecker):
    def __init__(self, minimum=None, maximum=None):
        super(FloatTypeChecker, self).__init__(float)
        self.minimum = minimum
        self.maximum = maximum

    def __call__(self, name, value):
        super(FloatTypeChecker, self).__call__(name, value)
        if isinstance(self.minimum, float):
            if value < self.minimum:
                raise ValueError('%s must be greater or equal %s' % (
                    name, self.minimum))
        if isinstance(self.maximum, float):
            if value > self.maximum:
                raise ValueError('%s must be less or equal %s' % (
                    name, self.maximum))


# Iterable type checkers ------------------------------------------------------
class IterableTypeChecker(TypeChecker):
    def __init__(self, iter_type, item_type=None, min_length=None, max_length=None, empty=True):
        super(IterableTypeChecker, self).__init__(iter_type)
        self.item_type = item_type
        self.min_length = min_length
        self.max_length = max_length
        self.empty = empty

    def __call__(self, name, value):
        super(IterableTypeChecker, self).__call__(name, value)
        if isinstance(self.item_type, type):
            if not all(isinstance(o, self.item_type) for o in value):
                raise ValueError('All elements of %s must be %s' % (
                    name, self.item_type))
        if isinstance(self.min_length, int):
            if len(value) < self.min_length:
                raise ValueError('%s must be longer than %s (or equal)' % (
                    name, self.min_length))
        if isinstance(self.max_length, int):
            if len(value) > self.max_length:
                raise ValueError('%s must be shorter than %s (or equal)' % (
                    name, self.max_length))
        if len(value) == 0 and not self.empty:
            raise ValueError('%s must not be empty' % name)


class StringTypeChecker(IterableTypeChecker):
    def __init__(self, min_length=None, max_length=None, empty=True):
        super(StringTypeChecker, self).__init__(
            str, None, min_length, max_length, empty)


class ListTypeChecker(IterableTypeChecker):
    def __init__(self, item_type=None, min_length=None, max_length=None, empty=True):
        super(ListTypeChecker, self).__init__(
            list, item_type, min_length, max_length, empty)


class SetTypeChecker(IterableTypeChecker):
    def __init__(self, item_type=None, min_length=None, max_length=None, empty=True):
        super(SetTypeChecker, self).__init__(
            set, item_type, min_length, max_length, empty)


class TupleTypeChecker(IterableTypeChecker):
    def __init__(self, item_type=None, min_length=None, max_length=None, empty=True):
        super(TupleTypeChecker, self).__init__(
            tuple, item_type, min_length, max_length, empty)


class RangeTypeChecker(IterableTypeChecker):
    def __init__(self, min_length=None, max_length=None, empty=True):
        super(RangeTypeChecker, self).__init__(
            # don't need to check for integers as range enforces it
            range, None, min_length, max_length, empty)


# Dict type checkers ----------------------------------------------------------
class DictTypeChecker(TypeChecker):
    def __init__(self, key_type=None, value_type=None, min_length=None, max_length=None, empty=True):
        super(DictTypeChecker, self).__init__(dict)
        self.key_type = key_type
        self.value_type = value_type
        self.min_length = min_length
        self.max_length = max_length
        self.empty = empty

    def __call__(self, name, value):
        super(DictTypeChecker, self).__call__(name, value)
        if isinstance(self.key_type, type):
            if not all(isinstance(o, self.key_type) for o in value.keys()):
                raise ValueError('All keys of %s must be %s' % (
                    name, self.key_type))
        if isinstance(self.value_type, type):
            if not all(isinstance(o, self.value_type) for o in value.values()):
                raise ValueError('All values of %s must be %s' % (
                    name, self.value_type))
        if isinstance(self.min_length, int):
            if len(value) < self.min_length:
                raise ValueError('%s must be longer than %s (or equal)' % (
                    name, self.min_length))
        if isinstance(self.max_length, int):
            if len(value) > self.max_length:
                raise ValueError('%s must be shorter than %s (or equal)' % (
                    name, self.max_length))
        if len(value) == 0 and not self.empty:
            raise ValueError('%s must not be empty' % name)


# Complex type checkers -------------------------------------------------------
class ObjectTypeChecker(StringTypeChecker):
    # TODO: maybe check that the object actually exists,
    # see http://stackoverflow.com/questions/14050281
    # TODO: check that value is a valid Python path (no slash, etc.)
    pass


# Settings ====================================================================
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
                 call=True,
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
        self.call = call
        self.required = required
        self.prefix = prefix
        self.checker = checker

    @property
    def full_name(self):
        return self.prefix.upper() + self.name.upper()

    @property
    def default_value(self):
        if callable(self.default) and self.call:
            return self.default()
        return self.default

    @property
    def raw_value(self):
        """Get the setting from ``django.conf.settings``."""
        try:
            return getattr(settings, self.full_name)
        except AttributeError:
            if self.required:
                raise AttributeError(
                    'setting %s is required.' % self.full_name)
            return self.default_value

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


class BooleanSetting(Setting):
    def __init__(self, name='', default=True, required=False,
                 prefix='', call=True):
        super(BooleanSetting, self).__init__(
            name=name, default=default, required=required, prefix=prefix,
            call=call, checker=BooleanTypeChecker())


class IntegerSetting(Setting):
    def __init__(self, name='', default=0, required=False,
                 prefix='', call=True, **checker_kwargs):
        super(IntegerSetting, self).__init__(
            name=name, default=default, required=required, prefix=prefix,
            call=call, checker=IntegerTypeChecker(**checker_kwargs))


class PositiveIntegerSetting(Setting):
    def __init__(self, name='', default=0, required=False,
                 prefix='', call=True, **checker_kwargs):
        super(PositiveIntegerSetting, self).__init__(
            name=name, default=default, required=required, prefix=prefix,
            call=call, checker=IntegerTypeChecker(minimum=0, **checker_kwargs))


class FloatSetting(Setting):
    def __init__(self, name='', default=0.0, required=False,
                 prefix='', call=True, **checker_kwargs):
        super(FloatSetting, self).__init__(
            name=name, default=default, required=required, prefix=prefix,
            call=call, checker=FloatTypeChecker(**checker_kwargs))


class PositiveFloatSetting(Setting):
    def __init__(self, name='', default=0.0, required=False,
                 prefix='', call=True, **checker_kwargs):
        super(PositiveFloatSetting, self).__init__(
            name=name, default=default, required=required, prefix=prefix,
            call=call, checker=FloatTypeChecker(minimum=0.0, **checker_kwargs))


class IterableSetting(Setting):
    def __init__(self, name='', default='', required=False,
                 prefix='', call=True, **checker_kwargs):
        super(IterableSetting, self).__init__(
            name=name, default=default, required=required, prefix=prefix,
            call=call, checker=IterableTypeChecker(
                iter_type=object, **checker_kwargs))


class StringSetting(Setting):
    def __init__(self, name='', default='', required=False,
                 prefix='', call=True, **checker_kwargs):
        super(StringSetting, self).__init__(
            name=name, default=default, required=required, prefix=prefix,
            call=call, checker=StringTypeChecker(**checker_kwargs))


class ListSetting(Setting):
    def __init__(self, name='', default=lambda: list(), required=False,
                 prefix='', call=True, **checker_kwargs):
        super(ListSetting, self).__init__(
            name=name, default=default, required=required, prefix=prefix,
            call=call, checker=ListTypeChecker(**checker_kwargs))


class SetSetting(Setting):
    def __init__(self, name='', default=lambda: set(), required=False,
                 prefix='', call=True, **checker_kwargs):
        super(SetSetting, self).__init__(
            name=name, default=default, required=required, prefix=prefix,
            call=call, checker=SetTypeChecker(**checker_kwargs))


class TupleSetting(Setting):
    def __init__(self, name='', default=lambda: tuple(), required=False,
                 prefix='', call=True, **checker_kwargs):
        super(TupleSetting, self).__init__(
            name=name, default=default, required=required, prefix=prefix,
            call=call, checker=SetTypeChecker(**checker_kwargs))


class RangeSetting(Setting):
    def __init__(self, name='', default=lambda: range(0), required=False,
                 prefix='', call=True, **checker_kwargs):
        super(RangeSetting, self).__init__(
            name=name, default=default, required=required, prefix=prefix,
            call=call, checker=SetTypeChecker(**checker_kwargs))


class DictSetting(Setting):
    def __init__(self, name='', default=lambda: dict(), required=False,
                 prefix='', call=True, **checker_kwargs):
        super(DictSetting, self).__init__(
            name=name, default=default, required=required, prefix=prefix,
            call=call, checker=DictTypeChecker(**checker_kwargs))


# Complex settings ------------------------------------------------------------
class ObjectSetting(Setting):
    """Setting to import an object given its Python path (a.b.c)."""

    def __init__(self, name='', default=None, required=False,
                 prefix='', call=False):
        super(ObjectSetting, self).__init__(
            name=name, default=default, required=required, prefix=prefix,
            call=call, checker=ObjectTypeChecker())

    def transform(self):
        path = self.raw_value
        if path is None:
            return None
        module_name = '.'.join(path.split('.')[:-1])
        module_obj = importlib.import_module(name=module_name)
        obj = getattr(module_obj, path.split('.')[-1])
        return obj
