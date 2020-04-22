"""Django AppSettings package."""
import os

from django.core.exceptions import ImproperlyConfigured
from django.core.signals import setting_changed

from .settings import (
    BooleanSetting,
    CallablePathSetting,
    DictSetting,
    FileSetting,
    FloatSetting,
    IntegerSetting,
    IterableSetting,
    ListSetting,
    NestedDictSetting,
    NestedListSetting,
    NestedSetting,
    ObjectSetting,
    PositiveFloatSetting,
    PositiveIntegerSetting,
    SetSetting,
    Setting,
    StringSetting,
    TupleSetting,
)
from .validators import (
    DictKeysTypeValidator,
    DictValuesTypeValidator,
    FileValidator,
    TypeValidator,
    ValuesTypeValidator,
)

__all__ = (
    "BooleanSetting",
    "CallablePathSetting",
    "DictKeysTypeValidator",
    "DictSetting",
    "DictValuesTypeValidator",
    "FileSetting",
    "FileValidator",
    "FloatSetting",
    "IntegerSetting",
    "IterableSetting",
    "ListSetting",
    "NestedDictSetting",
    "NestedListSetting",
    "NestedSetting",
    "ObjectSetting",
    "PositiveFloatSetting",
    "PositiveIntegerSetting",
    "SetSetting",
    "Setting",
    "StringSetting",
    "TupleSetting",
    "TypeValidator",
    "ValuesTypeValidator",
)


class _Metaclass(type):
    """
    ``AppSettings``'s metaclass.

    Each setting object declared in the class will be populated (name, prefix)
    and moved into the _meta.settings dictionary. A reference to this
    dictionary will also be added in the class as ``settings``.
    """

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
        _meta = dct.pop("Meta", type("Meta", (), {"setting_prefix": ""}))()
        _meta.settings = {}

        for name, setting in dct.items():
            if isinstance(setting, Setting):
                _meta.settings[name] = setting
                # populate name
                if setting.name == "":
                    setting.name = name
                # populate prefix
                if setting.prefix == "":
                    setting.prefix = _meta.setting_prefix
            else:
                new_attr[name] = setting
        new_attr["_meta"] = _meta
        new_attr["settings"] = _meta.settings

        return super_new(mcs, cls, bases, new_attr)

    def __getattr__(cls, item):
        """
        Return a setting object if it is in the ``_meta.settings`` dictionary.

        Args:
            item (str):
                the name of the setting variable (not the setting's name).

        Returns:
            ``Setting``: the setting object.

        Raises:
            AttributeError if the setting does not exist.
        """
        if item in cls._meta.settings.keys():
            return cls._meta.settings[item]
        raise AttributeError("'%s' class has no attribute '%s'" % (cls.__name__, item))


class AppSettings(metaclass=_Metaclass):
    """
    Base class for application settings.

    Only use this class as a parent class for inheritance. If you try to
    access settings directly in ``AppSettings``, it will raise a
    RecursionError. Some protections have been added to prevent you from
    instantiating this very class, or to return immediately when running
    ``AppSettings.check()``, but trying to access attributes on the class is
    not yet prevented.

    """

    OS_ENVIRON_OVERRIDE_PREFIX = "__DAP_"  # type: str

    def __init__(self):
        """
        Initialization method.

        The ``invalidate_cache`` and ``manage_environ_invalidation`` methods will be connected to the Django
        ``setting_changed`` signal in this method, with the dispatch UIDs being method initials and the id of this very
        object (``id(self)``).
        """
        if self.__class__ == AppSettings:
            raise RuntimeError("Do not use AppSettings class as itself, " "use it as a base for subclasses")
        setting_changed.connect(self.invalidate_cache, dispatch_uid="ic" + str(id(self)))
        setting_changed.connect(self.manage_environ_invalidation, dispatch_uid="mei" + str(id(self)))
        self._cache = {}

    def __getattr__(self, item):
        """
        Return a setting value.

        The caching is done here. If the setting exists, and if it's variable
        name is in the cache dictionary, return the cached value. If there
        is no cached value, get the setting value with ``setting.get_value()``,
        cache it, and return it.

        Args:
            item (str):
                the name of the setting variable (not the setting's name).

        Returns:
            object: a setting value.

        Raises:
            AttributeError if the setting does not exist.
        """
        if item in self.settings.keys():
            if item in self._cache:
                return self._cache[item]
            value = self._cache[item] = self.settings[item].get_value()
            return value
        raise AttributeError("'%s' object has no attribute '%s'" % (repr(self), item))

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
            except ImproperlyConfigured as error:
                exceptions.append(str(error))
        if exceptions:
            raise ImproperlyConfigured("\n".join(exceptions))

    def manage_environ_invalidation(self, *, setting, enter, **kwargs):
        """
        Manage keys and values in ``os.environ`` on setting change.

        Environ values take precedence over ``django.conf`` values by default. But when we override a setting, we want
        to take the ``django.conf`` value and therefore we need to remove corresponding key from the ``os.environ``.
        To be able to restore the original value later, we add a prefix (OS_ENVIRON_OVERRIDE_PREFIX) to the key and then
        just remove the prefix.
        """
        for item in self.settings.keys():
            if self.settings[item].full_name == setting:
                setting_override_key = self.OS_ENVIRON_OVERRIDE_PREFIX + setting
                if enter and setting in os.environ:
                    os.environ[setting_override_key] = os.environ[setting]
                    del os.environ[setting]
                elif not enter and setting_override_key in os.environ:
                    os.environ[setting] = os.environ[setting_override_key]
                    del os.environ[setting_override_key]
                break

    def invalidate_cache(self, **kwargs):
        """Invalidate cache. Run when receive ``setting_changed`` signal."""
        self._cache = {}
