# -*- coding: utf-8 -*-

u"""Django AppSettings package."""

from django.core.exceptions import ImproperlyConfigured

import six

from .settings import (
    BooleanListSetting,
    BooleanListTypeChecker,
    BooleanSetSetting,
    BooleanSetting,
    BooleanSetTypeChecker,
    BooleanTypeChecker,
    DictKeyValueTypeChecker,
    DictSetting,
    DictTypeChecker,
    FloatListSetting,
    FloatListTypeChecker,
    FloatSetSetting,
    FloatSetting,
    FloatSetTypeChecker,
    FloatTypeChecker,
    IntegerListSetting,
    IntegerListTypeChecker,
    IntegerSetSetting,
    IntegerSetting,
    IntegerSetTypeChecker,
    IntegerTypeChecker,
    ListSetting,
    ListTypeChecker,
    ObjectSetting,
    ObjectTypeChecker,
    PositiveFloatSetting,
    PositiveFloatTypeChecker,
    PositiveIntegerSetting,
    PositiveIntegerTypeChecker,
    SetSetting,
    Setting,
    SetTypeChecker,
    StringListSetting,
    StringListTypeChecker,
    StringSetSetting,
    StringSetting,
    StringSetTypeChecker,
    StringTypeChecker,
    TupleTypeChecker,
    TypeChecker
)

__all__ = (
    'BooleanListSetting',
    'BooleanListTypeChecker',
    'BooleanSetSetting',
    'BooleanSetting',
    'BooleanSetTypeChecker',
    'BooleanTypeChecker',
    'DictKeyValueTypeChecker',
    'DictSetting',
    'DictTypeChecker',
    'FloatListSetting',
    'FloatListTypeChecker',
    'FloatSetSetting',
    'FloatSetting',
    'FloatSetTypeChecker',
    'FloatTypeChecker',
    'IntegerListSetting',
    'IntegerListTypeChecker',
    'IntegerSetSetting',
    'IntegerSetting',
    'IntegerSetTypeChecker',
    'IntegerTypeChecker',
    'ListSetting',
    'ListTypeChecker',
    'ObjectSetting',
    'ObjectTypeChecker',
    'PositiveFloatSetting',
    'PositiveFloatTypeChecker',
    'PositiveIntegerSetting',
    'PositiveIntegerTypeChecker',
    'SetSetting',
    'Setting',
    'SetTypeChecker',
    'StringListSetting',
    'StringListTypeChecker',
    'StringSetSetting',
    'StringSetting',
    'StringSetTypeChecker',
    'StringTypeChecker',
    'TupleTypeChecker',
    'TypeChecker'
)


class _Metaclass(type):
    """``AppSettings``'s metaclass."""

    def __new__(mcs, cls, bases, dct):
        """
        New method.

        Args:
            cls (str): class name.
            bases (tuple): base classes to inherit from.
            dct (dict): class attributes.

        Returns:
            class: the new created class.
        """
        new_attr = {}
        _meta = dct.pop('Meta', type('Meta', (), {'setting_prefix': ''}))()
        _meta.settings = {}

        for name, setting in dct.items():
            if isinstance(setting, Setting):
                _meta.settings[name] = setting
                # populate name
                if setting.name == '':
                    setting.name = name.upper()
                # populate prefix
                if setting.prefix == '':
                    setting.prefix = _meta.setting_prefix
            else:
                new_attr[name] = setting
        new_attr['_meta'] = _meta
        new_attr['settings'] = _meta.settings

        return super(_Metaclass, mcs).__new__(mcs, cls, bases, new_attr)

    def __init__(cls, name, bases, dct):
        """
        Initialization method.

        Args:
            name (str): class name.
            bases (tuple): base classes to inherit from.
            dct (dict): class attributes.
        """
        super(_Metaclass, cls).__init__(name, bases, dct)


class AppSettings(six.with_metaclass(_Metaclass)):
    """Base class for application settings."""

    def __init__(self):
        """Initialization method."""
        self._cache = {}

    def __getattr__(self, item):
        if item in self.settings.keys():
            if item in self._cache:
                return self._cache[item]
            value = self._cache[item] = self.settings[item].get_value()
            return value
        raise AttributeError("'%s' class has no setting '%s'" % (
            repr(self), item))

    @classmethod
    def check(cls):
        """
        Class method to check every settings.

        Will raise an ``ImproperlyConfigured`` exception with explanation.
        """
        exceptions = []
        for setting in cls.settings.values():
            try:
                getattr(cls, '%s' % setting).check()
            # pylama:ignore=W0703
            except Exception as e:
                exceptions.append(str(e))
        if exceptions:
            raise ImproperlyConfigured('\n'.join(exceptions))

    def invalidate_cache(self):
        self._cache = {}
