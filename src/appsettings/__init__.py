# -*- coding: utf-8 -*-

u"""Django AppSettings package."""

from django.core.exceptions import ImproperlyConfigured
from django.core.signals import setting_changed

import six

from .settings import (
    BooleanSetting,
    BooleanTypeChecker,
    DictSetting,
    DictTypeChecker,
    FloatSetting,
    FloatTypeChecker,
    IntegerSetting,
    IntegerTypeChecker,
    IterableSetting,
    IterableTypeChecker,
    ListSetting,
    ListTypeChecker,
    ObjectSetting,
    ObjectTypeChecker,
    PositiveFloatSetting,
    PositiveIntegerSetting,
    SetSetting,
    Setting,
    SetTypeChecker,
    StringSetting,
    StringTypeChecker,
    TupleSetting,
    TupleTypeChecker,
    TypeChecker
)

__all__ = (
    'BooleanSetting',
    'BooleanTypeChecker',
    'DictSetting',
    'DictTypeChecker',
    'FloatSetting',
    'FloatTypeChecker',
    'IntegerSetting',
    'IntegerTypeChecker',
    'IterableSetting',
    'IterableTypeChecker',
    'ListSetting',
    'ListTypeChecker',
    'ObjectSetting',
    'ObjectTypeChecker',
    'PositiveFloatSetting',
    'PositiveIntegerSetting',
    'SetSetting',
    'Setting',
    'SetTypeChecker',
    'StringSetting',
    'StringTypeChecker',
    'TupleSetting',
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
        super_new = super(_Metaclass, mcs).__new__

        # Also ensure initialization is only performed for subclasses
        # of AppSettings (excluding AppSettings class itself).
        parents = [b for b in bases if isinstance(b, _Metaclass)]
        if not parents:
            return super_new(mcs, cls, bases, dct)

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

        return super_new(mcs, cls, bases, new_attr)

    def __getattr__(cls, item):
        if item in cls._meta.settings.keys():
            return cls._meta.settings[item]
        raise AttributeError("'%s' class has no attribute '%s'" % (
            cls.__name__, item))


class AppSettings(six.with_metaclass(_Metaclass)):
    """Base class for application settings."""

    def __init__(self):
        """Initialization method."""
        setting_changed.connect(self.invalidate_cache, dispatch_uid=id(self))
        self._cache = {}

    def __getattr__(self, item):
        if item in self.settings.keys():
            if item in self._cache:
                return self._cache[item]
            value = self._cache[item] = self.settings[item].get_value()
            return value
        raise AttributeError("'%s' object has no attribute '%s'" % (
            repr(self), item))

    @classmethod
    def check(cls):
        """
        Class method to check every settings.

        Will raise an ``ImproperlyConfigured`` exception with explanation.
        """
        if cls == AppSettings:
            return None

        exceptions = []
        for setting in cls.settings.values():
            try:
                setting.check()
            # pylama:ignore=W0703
            except Exception as e:
                exceptions.append(str(e))
        if exceptions:
            raise ImproperlyConfigured('\n'.join(exceptions))

    def invalidate_cache(self, **kwargs):
        self._cache = {}
