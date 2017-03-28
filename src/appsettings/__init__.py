# -*- coding: utf-8 -*-

u"""Django AppSettings package."""


from django.conf import settings

__version__ = '0.1.0'


class Setting(object):
    def __init__(self,
                 name=None,
                 default=None,
                 checker=lambda n, v: None,
                 transformer=lambda v: v):
        self.name = name
        self.default = default
        self.transform = transformer
        self.check = checker


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
                # add raw getters
                raw_name = 'get_raw_%s' % name
                new_attr[raw_name] = staticmethod(lambda: getattr(
                    settings, _meta.settings_prefix.upper() + val.name,
                    val.default))
                # add getters (raw getter + transform)
                new_attr['get_%s' % name] = staticmethod(lambda: val.transform(
                    new_attr[raw_name]()))
                # add checkers (raw getter + checker)
                new_attr['check_%s' % name] = staticmethod(lambda: val.check(
                    val.name, new_attr[raw_name]()))
            new_attr[name] = val
        new_attr['_meta'] = _meta

        return super(Metaclass, mcs).__new__(mcs, cls, bases, new_attr)

    def __init__(cls, name, bases, dct):
        super(Metaclass, cls).__init__(name, bases, dct)


class AppSettings(object):
    __metaclass__ = Metaclass

    def __init__(self):
        for setting in self._meta.settings:
            setattr(self, setting, getattr(
                self.__class__, 'get_%s' % setting)())

    @classmethod
    def check(cls):
        for setting in cls._meta.settings:
            getattr(cls, 'check_%s' % setting)()
