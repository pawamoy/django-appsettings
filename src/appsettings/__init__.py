# -*- coding: utf-8 -*-

u"""Django AppSettings package."""

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

import six

__version__ = '0.2.0'


class Setting(object):
    """
    Generic setting class.

    Serve as base class for more specific setting types.
    """

    def __init__(self,
                 name=None,
                 default=None,
                 checker=lambda n, v: None,
                 transformer=lambda v: v,
                 prefix=None):
        """
        Initialization method.

        Args:
            name (str): name of the setting.
            default (obj): default value given to the setting.
            checker (func):
                function to check the setting. It must take 2 arguments: name,
                value, and raise an error if value is incorrect. Default:
                do nothing.
            transformer ():
                function to transform the value retrieved from Django settings.
                It must take 1 argument: value, and return it transformed.
                Default: identity.
            prefix (str):
                prefix of the setting.
                Will override ``AppSettings.Meta`` prefix.
        """
        self.name = name
        self.default = default
        self.transformer = transformer
        self.checker = checker
        self.prefix = prefix

    def get_raw(self):
        """Get the setting from ``django.conf.settings``."""
        setting_name = self.prefix.upper() + self.name.upper()
        return getattr(settings, setting_name, self.default)

    def get(self):
        """Get the setting and return it transformed."""
        return self.transform()

    def check(self):
        """Check the setting. Raise exception if incorrect."""
        return self.checker(self.name, self.get_raw())

    def transform(self):
        """Get the setting and return it transformed."""
        return self.transformer(self.get_raw())


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
            except Exception as e:
                exceptions.append(str(e))
        if exceptions:
            raise ImproperlyConfigured('\n'.join(exceptions))
