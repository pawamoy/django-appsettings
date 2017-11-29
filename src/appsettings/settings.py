# -*- coding: utf-8 -*-

"""
Settings module.

This module defines the different type checkers and settings classes.
"""

import importlib

from django.conf import settings


# Type checkers ===============================================================
class TypeChecker(object):
    """
    Type checker base class.

    A type checker is a simple class that can be called when instantiated in
    order to validate an object against some conditions. A simple type checker
    will only check the type of the object. More complex type checkers can
    be created by inheriting from this base class.
    """

    def __init__(self, base_type=None):
        """
        Initialization method.

        Args:
            base_type (type): the type to check against value's type.
        """
        self.base_type = base_type

    def __call__(self, name, value):
        """
        Call method.

        Args:
            name (str): the value's name.
            value (object): the value to check.

        Raises:
            ValueError: if value is not type base_type.
        """
        if not isinstance(value, self.base_type):
            raise ValueError('%s must be %s, not %s' % (
                name, self.base_type, value.__class__))


class BooleanTypeChecker(TypeChecker):
    """Boolean type checker."""

    def __init__(self):
        """Initialization method."""
        super(BooleanTypeChecker, self).__init__(base_type=bool)


class IntegerTypeChecker(TypeChecker):
    """Integer type checker."""

    def __init__(self, minimum=None, maximum=None):
        """
        Initialization method.

        Args:
            minimum (int): a minimum value (included).
            maximum (int): a maximum value (included).
        """
        super(IntegerTypeChecker, self).__init__(base_type=int)
        self.minimum = minimum
        self.maximum = maximum

    def __call__(self, name, value):
        """
        Call method.

        Args:
            name (str): the value's name.
            value (int): the value to check.

        Raises:
            ValueError: if value is not type int.
            ValueError: if value is less than minimum.
            ValueError: if value is more than maximum.
        """
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
    """Float type checker."""

    def __init__(self, minimum=None, maximum=None):
        """
        Initialization method.

        Args:
            minimum (float): a minimum value (included).
            maximum (float): a maximum value (included).
        """
        super(FloatTypeChecker, self).__init__(base_type=float)
        self.minimum = minimum
        self.maximum = maximum

    def __call__(self, name, value):
        """
        Call method.

        Args:
            name (str): the value's name.
            value (float): the value to check.

        Raises:
            ValueError: if value is not type float.
            ValueError: if value is less than minimum.
            ValueError: if value is more than maximum.
        """
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
    """
    Iterable type checker.

    Inherit from this class to create type checkers that support iterable
    object checking, with item type, minimum and maximum length, and
    allowed emptiness.
    """

    def __init__(self, iter_type, item_type=None, min_length=None,
                 max_length=None, empty=True):
        """
        Initialization method.

        Args:
            iter_type (type): the type of the iterable object.
            item_type (type): the type of the items inside the object.
            min_length (int): a minimum length (included).
            max_length (int): a maximum length (included).
            empty (bool): whether emptiness is allowed.
        """
        super(IterableTypeChecker, self).__init__(base_type=iter_type)
        self.item_type = item_type
        self.min_length = min_length
        self.max_length = max_length
        self.empty = empty

    def __call__(self, name, value):
        """
        Call method.

        Args:
            name (str): the value's name.
            value (iterable): the value to check.

        Raises:
            ValueError: if value is not type iter_type.
            ValueError: if any item in value is not type item_type.
            ValueError: if value's length is less than min_length.
            ValueError: if value's length is more than max_length.
            ValueError: if value's length is 0 and emptiness is not allowed.
        """
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
    """String type checker."""

    def __init__(self, min_length=None, max_length=None, empty=True):
        """
        Initialization method.

        Args:
            min_length (int): minimum length of the string (included).
            max_length (int): maximum length of the string (included).
            empty (bool): whether empty string is allowed.
        """
        super(StringTypeChecker, self).__init__(
            iter_type=str, min_length=min_length, max_length=max_length,
            empty=empty)


class ListTypeChecker(IterableTypeChecker):
    """List type checker."""

    def __init__(self, item_type=None, min_length=None, max_length=None,
                 empty=True):
        """
        Initialization method.

        Args:
            item_type (type): the type of the items inside the list.
            min_length (int): minimum length of the list (included).
            max_length (int): maximum length of the list (included).
            empty (bool): whether empty list is allowed.
        """
        super(ListTypeChecker, self).__init__(
            iter_type=list, item_type=item_type, min_length=min_length,
            max_length=max_length, empty=empty)


class SetTypeChecker(IterableTypeChecker):
    """Set type checker."""

    def __init__(self, item_type=None, min_length=None, max_length=None,
                 empty=True):
        """
        Initialization method.

        Args:
            item_type (type): the type of the items inside the set.
            min_length (int): minimum length of the set (included).
            max_length (int): maximum length of the set (included).
            empty (bool): whether empty set is allowed.
        """
        super(SetTypeChecker, self).__init__(
            iter_type=set, item_type=item_type, min_length=min_length,
            max_length=max_length, empty=empty)


class TupleTypeChecker(IterableTypeChecker):
    """Tuple type checker."""

    def __init__(self, item_type=None, min_length=None, max_length=None,
                 empty=True):
        """
        Initialization method.

        Args:
            item_type (type): the type of the items inside the tuple.
            min_length (int): minimum length of the tuple (included).
            max_length (int): maximum length of the tuple (included).
            empty (bool): whether empty tuple is allowed.
        """
        super(TupleTypeChecker, self).__init__(
            iter_type=tuple, item_type=item_type, min_length=min_length,
            max_length=max_length, empty=empty)


# Dict type checkers ----------------------------------------------------------
class DictTypeChecker(TypeChecker):
    """Dict type checker."""

    def __init__(self, key_type=None, value_type=None, min_length=None,
                 max_length=None, empty=True):
        """
        Initialization method.

        Args:
            key_type (type): the type of the dict keys.
            value_type (type): the type of the dict values.
            min_length (int): minimum length of the dict (included).
            max_length (int): maximum length of the dict (included).
            empty (bool): whether empty dict is allowed.
        """
        super(DictTypeChecker, self).__init__(base_type=dict)
        self.key_type = key_type
        self.value_type = value_type
        self.min_length = min_length
        self.max_length = max_length
        self.empty = empty

    def __call__(self, name, value):
        """
        Call method.

        Args:
            name (str): the value's name.
            value (dict): the value to check.

        Raises:
            ValueError: if value is not type dict.
            ValueError: if any key in value is not type key_type.
            ValueError: if any value in value is not type value_type.
            ValueError: if value's length is less than min_length.
            ValueError: if value's length is more than max_length.
            ValueError: if value's length is 0 and emptiness is not allowed.
        """
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
    """
    Object type checker.

    Actually only check if the given value is a string.

    TODO: maybe check that value is a valid Python path
    (https://stackoverflow.com/questions/47537921).
    TODO: maybe check that the object actually exists
    (https://stackoverflow.com/questions/14050281).
    """

    def __init__(self, empty=True):
        """
        Initialization method.

        Args:
            empty (bool):
        """
        super(ObjectTypeChecker, self).__init__(empty=empty)

    def __call__(self, name, value):
        """
        Call method.

        Args:
            name (str): the value's name.
            value (str): the value to check.

        Raises:
            ValueError: if value is not type str.
        """
        super(ObjectTypeChecker, self).__call__(name, value)
        # TODO: maybe check that value is a valid Python path
        # https://stackoverflow.com/questions/47537921
        # TODO: maybe check that the object actually exists
        # https://stackoverflow.com/questions/14050281


# Settings ====================================================================
class Setting(object):
    """
    Base setting class.

    The setting's name and prefix are used to specify the variable name to
    look for in the project settings. The default value is returned only if
    the variable is missing and the setting is not required. If the setting
    is missing and required, trying to access it will raise an AttributeError.

    When accessing a setting's value, the value is first fetched from the
    project settings, then passed to a transform function that will return it
    modified (or not). By default, no transformation is applied.

    The call_default parameter tells if we should try to call the given
    default value before returning it. This allows to give lambdas or callables
    as default values. The transform_default parameter tells if we should
    transform the default value as well through the transform method.
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
            name (str): the name of the setting.
            default (object): default value given to the setting.
            required (bool): whether the setting is required or not.
            prefix (str):
                the setting's prefix (overrides ``AppSettings.Meta`` prefix).
            call_default (bool): whether to call the default (if callable).
            transform_default (bool): whether to transform the default value.
            checker (callable):
                an instance of type checker or any callable object accepting
                two arguments (name, value).
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
        """
        Property to return the full name of the setting.

        Returns:
            str: upper prefix + upper name.
        """
        return self.prefix.upper() + self.name.upper()

    @property
    def default_value(self):
        """
        Property to return the default value.

        If the default value is callable and call_default is True, return
        the result of default(). Else return default.

        Returns:
            object: the default value.
        """
        if callable(self.default) and self.call_default:
            return self.default()
        return self.default

    @property
    def raw_value(self):
        """
        Property to return the variable defined in ``django.conf.settings``.

        Returns:
            object: the variable defined in ``django.conf.settings``.

        Raises:
            AttributeError: if the variable is missing.
        """
        return getattr(settings, self.full_name)

    @property
    def value(self):
        """
        Property to return the transformed raw or default value.

        This property is a simple shortcut for get_value().

        Returns:
            object: the transformed raw value.
        """
        return self.get_value()

    def get_value(self):
        """
        Return the transformed raw or default value.

        If the variable is missing from the project settings, and the setting
        is required, re-raise an AttributeError. If it is not required,
        return the (optionally transformed) default value.

        Returns:
            object: the transformed raw value.
        """
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
        """
        Run the setting checker against the setting raw value.

        Raises:
            AttributeError: if the setting is missing and required.
            ValueError: (or other Exception) if the raw value is invalid.
        """
        try:
            value = self.raw_value
        except AttributeError as err:
            self._reraise_if_required(err)
        else:
            self.checker(self.full_name, value)

    def transform(self, value):
        """
        Return a transformed value.

        By default, no transformation is done.

        Args:
            value (object):

        Returns:
            object: the transformed value.
        """
        return value


class BooleanSetting(Setting):
    """Boolean setting."""

    def __init__(self, name='', default=True, required=False,
                 prefix='', call_default=True, transform_default=False):
        """
        Initialization method.

        Args:
            name (str): the name of the setting.
            default (bool): default value given to the setting.
            required (bool): whether the setting is required or not.
            prefix (str):
                the setting's prefix (overrides ``AppSettings.Meta`` prefix).
            call_default (bool): whether to call the default (if callable).
            transform_default (bool): whether to transform the default value.
        """
        super(BooleanSetting, self).__init__(
            name=name, default=default, required=required, prefix=prefix,
            call_default=call_default, transform_default=transform_default,
            checker=BooleanTypeChecker())


class IntegerSetting(Setting):
    """Integer setting."""

    def __init__(self, name='', default=0, required=False,
                 prefix='', call_default=True, transform_default=False,
                 **checker_kwargs):
        """
        Initialization method.

        Args:
            name (str): the name of the setting.
            default (int): default value given to the setting.
            required (bool): whether the setting is required or not.
            prefix (str):
                the setting's prefix (overrides ``AppSettings.Meta`` prefix).
            call_default (bool): whether to call the default (if callable).
            transform_default (bool): whether to transform the default value.
            **checker_kwargs: keyword arguments passed to the checker.
        """
        super(IntegerSetting, self).__init__(
            name=name, default=default, required=required, prefix=prefix,
            call_default=call_default, transform_default=transform_default,
            checker=IntegerTypeChecker(**checker_kwargs))


class PositiveIntegerSetting(Setting):
    """Positive integer setting."""

    def __init__(self, name='', default=0, required=False,
                 prefix='', call_default=True, transform_default=False,
                 **checker_kwargs):
        """
        Initialization method.

        Args:
            name (str): the name of the setting.
            default (int): default value given to the setting.
            required (bool): whether the setting is required or not.
            prefix (str):
                the setting's prefix (overrides ``AppSettings.Meta`` prefix).
            call_default (bool): whether to call the default (if callable).
            transform_default (bool): whether to transform the default value.
            **checker_kwargs: keyword arguments passed to the checker.
        """
        super(PositiveIntegerSetting, self).__init__(
            name=name, default=default, required=required, prefix=prefix,
            call_default=call_default, transform_default=transform_default,
            checker=IntegerTypeChecker(minimum=0, **checker_kwargs))


class FloatSetting(Setting):
    """Float setting."""

    def __init__(self, name='', default=0.0, required=False,
                 prefix='', call_default=True, transform_default=False,
                 **checker_kwargs):
        """
        Initialization method.

        Args:
            name (str): the name of the setting.
            default (float): default value given to the setting.
            required (bool): whether the setting is required or not.
            prefix (str):
                the setting's prefix (overrides ``AppSettings.Meta`` prefix).
            call_default (bool): whether to call the default (if callable).
            transform_default (bool): whether to transform the default value.
            **checker_kwargs: keyword arguments passed to the checker.
        """
        super(FloatSetting, self).__init__(
            name=name, default=default, required=required, prefix=prefix,
            call_default=call_default, transform_default=transform_default,
            checker=FloatTypeChecker(**checker_kwargs))


class PositiveFloatSetting(Setting):
    """Positive float setting."""

    def __init__(self, name='', default=0.0, required=False,
                 prefix='', call_default=True, transform_default=False,
                 **checker_kwargs):
        """
        Initialization method.

        Args:
            name (str): the name of the setting.
            default (float): default value given to the setting.
            required (bool): whether the setting is required or not.
            prefix (str):
                the setting's prefix (overrides ``AppSettings.Meta`` prefix).
            call_default (bool): whether to call the default (if callable).
            transform_default (bool): whether to transform the default value.
            **checker_kwargs: keyword arguments passed to the checker.
        """
        super(PositiveFloatSetting, self).__init__(
            name=name, default=default, required=required, prefix=prefix,
            call_default=call_default, transform_default=transform_default,
            checker=FloatTypeChecker(minimum=0.0, **checker_kwargs))


# Iterable settings -----------------------------------------------------------
class IterableSetting(Setting):
    """Iterable setting."""

    def __init__(self, name='', default=None, required=False,
                 prefix='', call_default=True, transform_default=False,
                 **checker_kwargs):
        """
        Initialization method.

        Args:
            name (str): the name of the setting.
            default (iterable): default value given to the setting.
            required (bool): whether the setting is required or not.
            prefix (str):
                the setting's prefix (overrides ``AppSettings.Meta`` prefix).
            call_default (bool): whether to call the default (if callable).
            transform_default (bool): whether to transform the default value.
            **checker_kwargs: keyword arguments passed to the checker.
        """
        super(IterableSetting, self).__init__(
            name=name, default=default, required=required, prefix=prefix,
            call_default=call_default, transform_default=transform_default,
            checker=IterableTypeChecker(
                iter_type=object, **checker_kwargs))


class StringSetting(Setting):
    """String setting."""

    def __init__(self, name='', default='', required=False,
                 prefix='', call_default=True, transform_default=False,
                 **checker_kwargs):
        """
        Initialization method.

        Args:
            name (str): the name of the setting.
            default (str): default value given to the setting.
            required (bool): whether the setting is required or not.
            prefix (str):
                the setting's prefix (overrides ``AppSettings.Meta`` prefix).
            call_default (bool): whether to call the default (if callable).
            transform_default (bool): whether to transform the default value.
            **checker_kwargs: keyword arguments passed to the checker.
        """
        super(StringSetting, self).__init__(
            name=name, default=default, required=required, prefix=prefix,
            call_default=call_default, transform_default=transform_default,
            checker=StringTypeChecker(**checker_kwargs))


class ListSetting(Setting):
    """List setting."""

    def __init__(self, name='', default=lambda: list(), required=False,
                 prefix='', call_default=True, transform_default=False,
                 **checker_kwargs):
        """
        Initialization method.

        Args:
            name (str): the name of the setting.
            default (list): default value given to the setting.
            required (bool): whether the setting is required or not.
            prefix (str):
                the setting's prefix (overrides ``AppSettings.Meta`` prefix).
            call_default (bool): whether to call the default (if callable).
            transform_default (bool): whether to transform the default value.
            **checker_kwargs: keyword arguments passed to the checker.
        """
        super(ListSetting, self).__init__(
            name=name, default=default, required=required, prefix=prefix,
            call_default=call_default, transform_default=transform_default,
            checker=ListTypeChecker(**checker_kwargs))


class SetSetting(Setting):
    """Set setting."""

    def __init__(self, name='', default=lambda: set(), required=False,
                 prefix='', call_default=True, transform_default=False,
                 **checker_kwargs):
        """
        Initialization method.

        Args:
            name (str): the name of the setting.
            default (set): default value given to the setting.
            required (bool): whether the setting is required or not.
            prefix (str):
                the setting's prefix (overrides ``AppSettings.Meta`` prefix).
            call_default (bool): whether to call the default (if callable).
            transform_default (bool): whether to transform the default value.
            **checker_kwargs: keyword arguments passed to the checker.
        """
        super(SetSetting, self).__init__(
            name=name, default=default, required=required, prefix=prefix,
            call_default=call_default, transform_default=transform_default,
            checker=SetTypeChecker(**checker_kwargs))


class TupleSetting(Setting):
    """Tuple setting."""

    def __init__(self, name='', default=lambda: tuple(), required=False,
                 prefix='', call_default=True, transform_default=False,
                 **checker_kwargs):
        """
        Initialization method.

        Args:
            name (str): the name of the setting.
            default (tuple): default value given to the setting.
            required (bool): whether the setting is required or not.
            prefix (str):
                the setting's prefix (overrides ``AppSettings.Meta`` prefix).
            call_default (bool): whether to call the default (if callable).
            transform_default (bool): whether to transform the default value.
            **checker_kwargs: keyword arguments passed to the checker.
        """
        super(TupleSetting, self).__init__(
            name=name, default=default, required=required, prefix=prefix,
            call_default=call_default, transform_default=transform_default,
            checker=SetTypeChecker(**checker_kwargs))


# Dict settings ---------------------------------------------------------------
class DictSetting(Setting):
    """Dict setting."""

    def __init__(self, name='', default=lambda: dict(), required=False,
                 prefix='', call_default=True, transform_default=False,
                 **checker_kwargs):
        """
        Initialization method.

        Args:
            name (str): the name of the setting.
            default (dict): default value given to the setting.
            required (bool): whether the setting is required or not.
            prefix (str):
                the setting's prefix (overrides ``AppSettings.Meta`` prefix).
            call_default (bool): whether to call the default (if callable).
            transform_default (bool): whether to transform the default value.
            **checker_kwargs: keyword arguments passed to the checker.
        """
        super(DictSetting, self).__init__(
            name=name, default=default, required=required, prefix=prefix,
            call_default=call_default, transform_default=transform_default,
            checker=DictTypeChecker(**checker_kwargs))


# Complex settings ------------------------------------------------------------
class ObjectSetting(Setting):
    """
    Object setting.

    This setting allows to return an object given its Python path (a.b.c).
    """

    def __init__(self, name='', default=None, required=False,
                 prefix='', call_default=False, transform_default=False,
                 **checker_kwargs):
        """
        Initialization method.

        Args:
            name (str): the name of the setting.
            default (object): default value given to the setting.
            required (bool): whether the setting is required or not.
            prefix (str):
                the setting's prefix (overrides ``AppSettings.Meta`` prefix).
            call_default (bool): whether to call the default (if callable).
            transform_default (bool): whether to transform the default value.
            **checker_kwargs: keyword arguments passed to the checker.
        """
        super(ObjectSetting, self).__init__(
            name=name, default=default, required=required, prefix=prefix,
            call_default=call_default, transform_default=transform_default,
            checker=ObjectTypeChecker(**checker_kwargs))

    def transform(self, path):
        """
        Transform a path into an actual Python object.

        The path can be arbitrary long. You can pass the path to a package,
        a module, a class, a function or a global variable, as deep as you
        want, as long as the deepest module is importable through
        ``importlib.import_module`` and each object is obtainable through
        the ``getattr`` method. Local objects will not work.

        Args:
            path (str): the dot-separated path of the object.

        Returns:
            object: the imported module or obtained object.
        """
        if path is None or not path:
            return None

        obj_parent_modules = path.split('.')
        objects = [obj_parent_modules.pop(-1)]

        while True:
            try:
                parent_module_path = '.'.join(obj_parent_modules)
                parent_module = importlib.import_module(parent_module_path)
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
