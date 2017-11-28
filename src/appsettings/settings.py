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
    def __init__(self, empty=True):
        super(StringTypeChecker, self).__init__(
            str, None, min_length=None, max_length=None, empty=empty)

    def __call__(self, name, value):
        super(ObjectTypeChecker, self).__call__(name, value)
        # TODO: maybe check that value is a valid Python path
        # https://stackoverflow.com/questions/47537921
        # TODO: maybe check that the object actually exists
        # https://stackoverflow.com/questions/14050281


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
                 call_default=True,
                 transform_default=False,
                 checker=None):
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
        self.call_default = call_default
        self.transform_default = transform_default
        self.required = required
        self.prefix = prefix

        if checker is None:
            if not hasattr(self, 'checker'):
                self.checker = lambda n, v: None
        else:
            self.checker = checker

    def _reraise_if_required(self, err):
        if self.required:
            raise AttributeError('%s setting is required and %s' % (
                self.full_name, err))

    @property
    def full_name(self):
        return self.prefix.upper() + self.name.upper()

    @property
    def default_value(self):
        if callable(self.default) and self.call_default:
            return self.default()
        return self.default

    @property
    def raw_value(self):
        """Get the setting from ``django.conf.settings``."""
        return getattr(settings, self.full_name)

    @property
    def value(self):
        """Get the setting and return it transformed."""
        return self.get_value()

    def get_value(self):
        try:
            value = self.raw_value
        except AttributeError as err:
            self._reraise_if_required(err)
            default_value = self.default_value
            if self.transform_default:
                return self.transform(default_value)
            return default_value
        else:
            return self.transform(value)

    def check(self):
        """Check the setting. Raise exception if incorrect."""
        try:
            value = self.raw_value
        except AttributeError as err:
            self._reraise_if_required(err)
        else:
            self.checker(self.full_name, value)

    def transform(self, value):
        """Get the setting and return it transformed."""
        return value


class BooleanSetting(Setting):
    def __init__(self, name='', default=True, required=False,
                 prefix='', call_default=True):
        super(BooleanSetting, self).__init__(
            name=name, default=default, required=required, prefix=prefix,
            call_default=call_default, checker=BooleanTypeChecker())


class IntegerSetting(Setting):
    def __init__(self, name='', default=0, required=False,
                 prefix='', call_default=True, **checker_kwargs):
        super(IntegerSetting, self).__init__(
            name=name, default=default, required=required, prefix=prefix,
            call_default=call_default, checker=IntegerTypeChecker(**checker_kwargs))


class PositiveIntegerSetting(Setting):
    def __init__(self, name='', default=0, required=False,
                 prefix='', call_default=True, **checker_kwargs):
        super(PositiveIntegerSetting, self).__init__(
            name=name, default=default, required=required, prefix=prefix,
            call_default=call_default, checker=IntegerTypeChecker(minimum=0, **checker_kwargs))


class FloatSetting(Setting):
    def __init__(self, name='', default=0.0, required=False,
                 prefix='', call_default=True, **checker_kwargs):
        super(FloatSetting, self).__init__(
            name=name, default=default, required=required, prefix=prefix,
            call_default=call_default, checker=FloatTypeChecker(**checker_kwargs))


class PositiveFloatSetting(Setting):
    def __init__(self, name='', default=0.0, required=False,
                 prefix='', call_default=True, **checker_kwargs):
        super(PositiveFloatSetting, self).__init__(
            name=name, default=default, required=required, prefix=prefix,
            call_default=call_default, checker=FloatTypeChecker(minimum=0.0, **checker_kwargs))


class IterableSetting(Setting):
    def __init__(self, name='', default=None, required=False,
                 prefix='', call_default=True, **checker_kwargs):
        super(IterableSetting, self).__init__(
            name=name, default=default, required=required, prefix=prefix,
            call_default=call_default, checker=IterableTypeChecker(
                iter_type=object, **checker_kwargs))


class StringSetting(Setting):
    def __init__(self, name='', default='', required=False,
                 prefix='', call_default=True, **checker_kwargs):
        super(StringSetting, self).__init__(
            name=name, default=default, required=required, prefix=prefix,
            call_default=call_default, checker=StringTypeChecker(**checker_kwargs))


class ListSetting(Setting):
    def __init__(self, name='', default=lambda: list(), required=False,
                 prefix='', call_default=True, **checker_kwargs):
        super(ListSetting, self).__init__(
            name=name, default=default, required=required, prefix=prefix,
            call_default=call_default, checker=ListTypeChecker(**checker_kwargs))


class SetSetting(Setting):
    def __init__(self, name='', default=lambda: set(), required=False,
                 prefix='', call_default=True, **checker_kwargs):
        super(SetSetting, self).__init__(
            name=name, default=default, required=required, prefix=prefix,
            call_default=call_default, checker=SetTypeChecker(**checker_kwargs))


class TupleSetting(Setting):
    def __init__(self, name='', default=lambda: tuple(), required=False,
                 prefix='', call_default=True, **checker_kwargs):
        super(TupleSetting, self).__init__(
            name=name, default=default, required=required, prefix=prefix,
            call_default=call_default, checker=SetTypeChecker(**checker_kwargs))


class DictSetting(Setting):
    def __init__(self, name='', default=lambda: dict(), required=False,
                 prefix='', call_default=True, **checker_kwargs):
        super(DictSetting, self).__init__(
            name=name, default=default, required=required, prefix=prefix,
            call_default=call_default, checker=DictTypeChecker(**checker_kwargs))


# Complex settings ------------------------------------------------------------
class ObjectSetting(Setting):
    """Setting to import an object given its Python path (a.b.c)."""

    def __init__(self, name='', default=None, required=False,
                 prefix='', call_default=False, **checker_kwargs):
        super(ObjectSetting, self).__init__(
            name=name, default=default, required=required, prefix=prefix,
            call_default=call_default, checker=ObjectTypeChecker(**checker_kwargs))

    def transform(self, path):
        if path is None or not path:
            return None

        obj_parent_modules = path.split('.')
        objects = [obj_parent_modules.pop(-1)]

        while True:
            try:
                parent_module_path = '.'.join(obj_parent_modules)
                parent_module = importlib.import_module(name=parent_module_path)
                break
            except ImportError:
                if len(obj_parent_modules) == 1:
                    raise ImportError("No module named '%s'" %
                                      obj_parent_modules[0])
                objects.insert(0, obj_parent_modules.pop(-1))

        current_object = parent_module
        for obj in objects:
            current_object = getattr(current_object, obj)
        return current_object
