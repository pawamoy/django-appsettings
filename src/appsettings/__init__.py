# -*- coding: utf-8 -*-

u"""Django AppSettings package."""

from functools import partial

from django.conf import settings

import six

__version__ = '0.1.0'


class Setting(object):
    def __init__(self,
                 name=None,
                 default=None,
                 checker=lambda n, v: None,
                 transformer=lambda v: v,
                 prefix=None):
        self.name = name
        self.default = default
        self.transformer = transformer
        self.checker = checker
        self.prefix = prefix

    def get_raw(self):
        setting_name = self.prefix.upper() + self.name.upper()
        return getattr(settings, setting_name, self.default)

    def get(self):
        return self.transform()

    def check(self):
        return self.checker(self.name, self.get_raw())

    def transform(self):
        return self.transformer(self.get_raw())


class Metaclass(type):
    def __new__(mcs, cls, bases, dct):
        new_attr = {}
        _meta = dct.pop('Meta', type('Meta', (), {'settings_prefix': ''}))()
        _meta.settings = []

        for name, val in dct.items():
            if isinstance(val, Setting):
                _meta.settings.append(name)
                # populate name
                if val.name is None:
                    val.name = name.upper()
                # populate prefix
                if val.prefix is None:
                    val.prefix = _meta.settings_prefix
                # add getter
                new_attr['get_%s' % name] = val.get
                # add checker
                new_attr['check_%s' % name] = val.check
            new_attr[name] = val
        new_attr['_meta'] = _meta

        return super(Metaclass, mcs).__new__(mcs, cls, bases, new_attr)

    def __init__(cls, name, bases, dct):
        super(Metaclass, cls).__init__(name, bases, dct)


class AppSettings(six.with_metaclass(Metaclass)):

    def __init__(self):
        for setting in self._meta.settings:
            setattr(self, setting, getattr(
                self.__class__, 'get_%s' % setting)())

    @classmethod
    def check(cls):
        for setting in cls._meta.settings:
            getattr(cls, 'check_%s' % setting)()
