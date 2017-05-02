# -*- coding: utf-8 -*-

u"""Django AppSettings package."""

from django.core.exceptions import ImproperlyConfigured

import six

from .settings import (
    BoolListSetting, BoolSetSetting, BoolSetting, DictSetting,
    FloatListSetting, FloatSetSetting, FloatSetting, ImportedObjectSetting,
    IntListSetting, IntSetSetting, IntSetting, ListSetting,
    PositiveFloatSetting, PositiveIntSetting, SetSetting, Setting,
    StringListSetting, StringSetSetting, StringSetting)

__all__ = (
    'BoolListSetting', 'BoolSetSetting', 'BoolSetting', 'DictSetting',
    'FloatListSetting', 'FloatSetSetting', 'FloatSetting',
    'ImportedObjectSetting', 'IntListSetting', 'IntSetSetting', 'IntSetting',
    'ListSetting', 'PositiveFloatSetting', 'PositiveIntSetting', 'SetSetting',
    'Setting', 'StringListSetting', 'StringSetSetting', 'StringSetting')

__version__ = '0.2.4'


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
        _meta.settings = []

        for name, val in dct.items():
            if isinstance(val, Setting):
                _meta.settings.append(name)
                # populate name
                if val.name is None:
                    val.name = name.upper()
                # populate prefix
                if val.prefix is None:
                    val.prefix = _meta.setting_prefix
                # add getter
                new_attr['get_%s' % name] = val.get
                # add checker
                new_attr['check_%s' % name] = val.check
            new_attr[name] = val
        new_attr['_meta'] = _meta

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
        """
        Initialization method.

        Instantiation will replace every class-declared settings with
        the result of their ``get`` method.
        """
        for setting in self._meta.settings:
            setattr(self, setting, getattr(
                self.__class__, 'get_%s' % setting)())

    @classmethod
    def check(cls):
        """
        Class method to check every settings.

        Will raise an ``ImproperlyConfigured`` exception with explanation.
        """
        exceptions = []
        for setting in cls._meta.settings:
            try:
                getattr(cls, 'check_%s' % setting)()
            # pylama:ignore=W0703
            except Exception as e:
                exceptions.append(str(e))
        if exceptions:
            raise ImproperlyConfigured('\n'.join(exceptions))
