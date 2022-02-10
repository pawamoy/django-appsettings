"""
Settings module.

This module defines the settings classes.
"""

import importlib
import itertools
import json
import os
import warnings
from pathlib import Path
from typing import Callable, Iterable, List, Optional, cast

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.validators import MaxLengthValidator, MaxValueValidator, MinLengthValidator, MinValueValidator

from .validators import (
    DictKeysTypeValidator,
    DictValuesTypeValidator,
    FileValidator,
    TypeValidator,
    ValuesTypeValidator,
)


class Setting(object):
    """
    Base setting class.

    The setting's name and prefix are used to specify the variable name to
    look for in the project settings. The default value is returned only if
    the variable is missing and the setting is not required. If the setting
    is missing and required, trying to access it will raise an AttributeError.

    When accessing a setting's value, the value is first fetched from environment
    or the project settings, then passed to a transform function that will return
    it modified (or not). By default, no transformation is applied.

    The call_default parameter tells if we should try to call the given
    default value before returning it. This allows to give lambdas or callables
    as default values. The transform_default parameter tells if we should
    transform the default value as well through the transform method.

    If the setting value is taken from environment, decode_environ method is
    called. By default it just decodes string as JSON and throws JSONDecodeError
    if the value is not a valid JSON. Some subclasses override and extend this
    method to be able to handle even other common values.

    Class attributes:
        default_validators (list of callables): Default set of validators for the setting.
    """

    default_validators = ()  # type: Iterable[Callable]

    def __init__(
        self,
        name="",
        default=None,
        required=False,
        prefix="",
        call_default=True,
        transform_default=False,
        validators=(),
    ):
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
            validators (list of callables): list of additional validators to use.
        """
        self.name = name
        self.default = default
        self.call_default = call_default
        self.transform_default = transform_default
        self.required = required
        self.prefix = prefix
        self.parent_setting = None  # type: Optional[Setting]
        self.nested_list_index = None
        self.validators = list(itertools.chain(self.default_validators, validators))

    def _reraise_if_required(self, err):
        if self.required:
            if isinstance(err, KeyError):
                msg = "%s setting is missing required item %s" % (cast(Setting, self.parent_setting).full_name, err)
            else:
                msg = "%s setting is required and %s" % (self.full_name, err)
            raise ImproperlyConfigured(msg)

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
        Property to return the variable defined in ``os.environ`` or in``django.conf.settings``.

        Returns:
            object: the variable defined in ``os.environ`` or in ``django.conf.settings``.

        Raises:
            AttributeError: if the variable is missing.
            KeyError: if the item is missing from nested setting.
        """
        if isinstance(self.parent_setting, NestedDictSetting):
            return self.parent_setting.raw_value[self.full_name]
        elif isinstance(self.parent_setting, NestedListSetting):
            return self.parent_setting.raw_value[self.nested_list_index]
        elif self.full_name in os.environ:
            warnings.warn("Loading setting values from environment is deprecated.", DeprecationWarning)
            return self.decode_environ(os.environ[self.full_name])
        else:
            return getattr(settings, self.full_name)

    @property
    def value(self):
        """
        Property to return the transformed raw or default value.

        This property is a simple shortcut for get_value().

        Returns:
            object: the transformed raw value.

        Raises:
            ImproperlyConfigured: The setting doesn't have a valid value.
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

        Raises:
            ImproperlyConfigured: The setting doesn't have a valid value.
        """
        try:
            value = self.raw_value
        except (AttributeError, KeyError) as err:
            self._reraise_if_required(err)
            default_value = self.default_value
            if self.transform_default:
                return self.transform(default_value)
            return default_value
        else:
            return self.transform(value)

    def validate(self, value):
        """Run custom validation on the setting value.

        By default, no additional validation is performed.

        Raises:
            ValidationError: if the validation fails.

        """
        pass

    def run_validators(self, value):
        """Run the validators on the setting value."""
        errors = []  # type: List[str]
        for validator in self.validators:
            try:
                validator(value)
            except ValidationError as error:
                errors.extend(error.messages)
        if errors:
            raise ValidationError(errors)

    def check(self):
        """
        Validate the setting value.

        Raises:
            ImproperlyConfigured: The setting doesn't have a valid value.
        """
        try:
            value = self.raw_value
        except (AttributeError, KeyError) as err:
            self._reraise_if_required(err)
        else:
            try:
                self.validate(value)
                self.run_validators(value)
            except ValidationError as error:
                raise ImproperlyConfigured("Setting {} has an invalid value: {}".format(self.full_name, error))

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

    def decode_environ(self, value):
        """
        Return a decoded value.

        By default, loads a JSON.

        Args:
            value (string):

        Returns:
            Any: the decoded value
        """
        return json.loads(value)


class BooleanSetting(Setting):
    """Boolean setting."""

    default_validators = (TypeValidator(bool),)

    def __init__(
        self,
        name="",
        default=True,
        required=False,
        prefix="",
        call_default=True,
        transform_default=False,
        validators=(),
    ):
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
            validators (list of callables): list of additional validators to use.
        """
        super().__init__(
            name=name,
            default=default,
            required=required,
            prefix=prefix,
            call_default=call_default,
            transform_default=transform_default,
            validators=validators,
        )

    def decode_environ(self, value):
        """
        Return a decoded value.

        Try to load a valid JSON. If JSONDecodeError is raised, chcecks for other common values (True, False, yes, no,
        0, 1).

        Args:
            value (string):

        Returns:
            bool:
        """
        if value.lower() in ("true", "yes", "1"):
            return True
        elif value.lower() in ("false", "no", "0"):
            return False
        else:
            raise ValueError("Invalid boolean setting %s in environ (%s)" % (self.full_name, value))


class IntegerSetting(Setting):
    """Integer setting."""

    default_validators = (TypeValidator(int),)

    def __init__(
        self,
        name="",
        default=0,
        required=False,
        prefix="",
        call_default=True,
        transform_default=False,
        validators=(),
        minimum=None,
        maximum=None,
    ):
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
            validators (list of callables): list of additional validators to use.
            minimum (int): a minimum value (included).
            maximum (int): a maximum value (included).
        """
        super().__init__(
            name=name,
            default=default,
            required=required,
            prefix=prefix,
            call_default=call_default,
            transform_default=transform_default,
            validators=validators,
        )
        if minimum is not None:
            self.validators.append(MinValueValidator(minimum))
        if maximum is not None:
            self.validators.append(MaxValueValidator(maximum))


class PositiveIntegerSetting(IntegerSetting):
    """Positive integer setting."""

    def __init__(
        self,
        name="",
        default=0,
        required=False,
        prefix="",
        call_default=True,
        transform_default=False,
        validators=(),
        maximum=None,
    ):
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
            validators (list of callables): list of additional validators to use.
            maximum (int): a maximum value (included).
        """
        super().__init__(
            name=name,
            default=default,
            required=required,
            prefix=prefix,
            call_default=call_default,
            transform_default=transform_default,
            validators=validators,
            minimum=0,
            maximum=maximum,
        )


class FloatSetting(IntegerSetting):
    """Float setting."""

    default_validators = (TypeValidator(float),)

    def __init__(
        self,
        name="",
        default=0.0,
        required=False,
        prefix="",
        call_default=True,
        transform_default=False,
        validators=(),
        minimum=None,
        maximum=None,
    ):
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
            validators (list of callables): list of additional validators to use.
            minimum (int): a minimum value (included).
            maximum (int): a maximum value (included).
        """
        super().__init__(
            name=name,
            default=default,
            required=required,
            prefix=prefix,
            call_default=call_default,
            transform_default=transform_default,
            validators=validators,
            minimum=minimum,
            maximum=maximum,
        )


class PositiveFloatSetting(FloatSetting):
    """Positive float setting."""

    def __init__(
        self,
        name="",
        default=0.0,
        required=False,
        prefix="",
        call_default=True,
        transform_default=False,
        validators=(),
        maximum=None,
    ):
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
            validators (list of callables): list of additional validators to use.
            maximum (int): a maximum value (included).
        """
        super().__init__(
            name=name,
            default=default,
            required=required,
            prefix=prefix,
            call_default=call_default,
            transform_default=transform_default,
            validators=validators,
            minimum=0,
            maximum=maximum,
        )


# Iterable settings -----------------------------------------------------------
class IterableSetting(Setting):
    """Iterable setting."""

    def __init__(
        self,
        name="",
        default=None,
        required=False,
        prefix="",
        call_default=True,
        transform_default=False,
        validators=(),
        item_type=None,
        delimiter=":",
        min_length=None,
        max_length=None,
        empty=None,
    ):
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
            validators (list of callables): list of additional validators to use.
            item_type (type): the type of the items inside the iterable.
            delimiter (str): value used to split a string into separated parts
            min_length (int): minimum length of the iterable (included).
            max_length (int): maximum length of the iterable (included).
            empty (bool): whether empty iterable is allowed. Deprecated in favor of min_length.
        """
        super().__init__(
            name=name,
            default=default,
            required=required,
            prefix=prefix,
            call_default=call_default,
            transform_default=transform_default,
            validators=validators,
        )
        self.item_type = item_type
        self.delimiter = delimiter
        if item_type is not None:
            self.validators.append(ValuesTypeValidator(item_type))
        if empty is not None:
            warnings.warn("Empty argument is deprecated, use min_length instead.", DeprecationWarning)
            if not empty:
                min_length = 1
        if min_length is not None:
            self.validators.append(MinLengthValidator(min_length))
        if max_length is not None:
            self.validators.append(MaxLengthValidator(max_length))

    def decode_environ(self, value):
        """
        Decode JSON value or split value by a delimiter to a list, if JSONDecodeError is raised.

        Default delimiter is a colon, can be changed via attribute ``delimiter``.

        Args:
            value (str):

        Returns:
            Iterable:
        """
        try:
            value = super().decode_environ(value)
        except json.decoder.JSONDecodeError:
            split_value = value.split(self.delimiter)
            item_convert_func = self.item_type or (lambda v: v)
            value = [item_convert_func(v) for v in split_value]
        return value


class StringSetting(Setting):
    """String setting."""

    default_validators = (TypeValidator(str),)

    def __init__(
        self,
        name="",
        default="",
        required=False,
        prefix="",
        call_default=True,
        transform_default=False,
        validators=(),
        min_length=None,
        max_length=None,
        empty=None,
    ):
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
            validators (list of callables): list of additional validators to use.
            min_length (int): minimum length of the iterable (included).
            max_length (int): maximum length of the iterable (included).
            empty (bool): whether empty iterable is allowed. Deprecated in favor of min_length.
        """
        super().__init__(
            name=name,
            default=default,
            required=required,
            prefix=prefix,
            call_default=call_default,
            transform_default=transform_default,
            validators=validators,
        )
        if empty is not None:
            warnings.warn("Empty argument is deprecated, use min_length instead.", DeprecationWarning)
            if not empty:
                min_length = 1
        if min_length is not None:
            self.validators.append(MinLengthValidator(min_length))
        if max_length is not None:
            self.validators.append(MaxLengthValidator(max_length))

    def decode_environ(self, value):
        """
        Return a decoded value.

        Try to load JSON or return pure string, if JSONDecodeError is raised.

        Args:
            (string):

        Returns:
            string:
        """
        try:
            value = super().decode_environ(value)
        except json.decoder.JSONDecodeError:
            value = str(value)
        return value


class ListSetting(IterableSetting):
    """List setting."""

    default_validators = (TypeValidator(list),)

    def __init__(self, name="", default=list, **kwargs):
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
            validators (list of callables): list of additional validators to use.
            item_type (type): the type of the items inside the iterable.
            min_length (int): minimum length of the iterable (included).
            max_length (int): maximum length of the iterable (included).
            empty (bool): whether empty iterable is allowed. Deprecated in favor of min_length.
        """
        super().__init__(name=name, default=default, **kwargs)

    def decode_environ(self, value):
        """
        Decode JSON value or split value by a delimiter to a list, if JSONDecodeError is raised.

        Default delimiter is a colon, can be changed via attribute ``delimiter``.

        Args:
            value (str):

        Returns:
            list:
        """
        return list(super().decode_environ(value))


class SetSetting(IterableSetting):
    """Set setting."""

    default_validators = (TypeValidator(set),)

    def __init__(self, name="", default=set, **kwargs):
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
            validators (list of callables): list of additional validators to use.
            item_type (type): the type of the items inside the iterable.
            min_length (int): minimum length of the iterable (included).
            max_length (int): maximum length of the iterable (included).
            empty (bool): whether empty iterable is allowed. Deprecated in favor of min_length.
        """
        super().__init__(name=name, default=default, **kwargs)

    def decode_environ(self, value):
        """
        Decode JSON value or split value by a delimiter to a set, if JSONDecodeError is raised.

        Default delimiter is a colon, can be changed via attribute ``delimiter``.

        Args:
            value (str):

        Returns:
            set:
        """
        return set(super().decode_environ(value))


class TupleSetting(IterableSetting):
    """Tuple setting."""

    default_validators = (TypeValidator(tuple),)

    def __init__(self, name="", default=tuple, **kwargs):
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
            validators (list of callables): list of additional validators to use.
            item_type (type): the type of the items inside the iterable.
            min_length (int): minimum length of the iterable (included).
            max_length (int): maximum length of the iterable (included).
            empty (bool): whether empty iterable is allowed. Deprecated in favor of min_length.
        """
        super().__init__(name=name, default=default, **kwargs)

    def decode_environ(self, value):
        """
        Decode JSON value or split value by a delimiter to a tuple, if JSONDecodeError is raised.

        Default delimiter is a colon, can be changed via attribute ``delimiter``.

        Args:
            value (str):

        Returns:
            tuple:
        """
        return tuple(super().decode_environ(value))


# Dict settings ---------------------------------------------------------------
class DictSetting(Setting):
    """Dict setting."""

    default_validators = (TypeValidator(dict),)

    def __init__(
        self,
        name="",
        default=dict,
        required=False,
        prefix="",
        call_default=True,
        transform_default=False,
        validators=(),
        key_type=None,
        value_type=None,
        outer_delimiter=None,
        inner_delimiter="=",
        min_length=None,
        max_length=None,
        empty=None,
    ):
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
            validators (list of callables): list of additional validators to use.
            key_type: the type of the dict keys.
            value_type (type): the type of dict values.
            outer_delimiter (str): value used to split environ string into separated parts
            inner_delimiter (str): value used to split environ string parts
            min_length (int): Noop. Deprecated.
            max_length (int): Noop. Deprecated.
            empty (bool): whether empty iterable is allowed. Deprecated in favor of MinLengthValidator.
        """
        super().__init__(
            name=name,
            default=default,
            required=required,
            prefix=prefix,
            call_default=call_default,
            transform_default=transform_default,
            validators=validators,
        )
        self.key_type = key_type
        self.value_type = value_type
        self.outer_delimiter = outer_delimiter
        self.inner_delimiter = inner_delimiter
        if key_type is not None:
            self.validators.append(DictKeysTypeValidator(key_type))
        if value_type is not None:
            self.validators.append(DictValuesTypeValidator(value_type))
        if empty is not None:
            warnings.warn("Empty argument is deprecated, use MinLengthValidator instead.", DeprecationWarning)
            self.validators.append(MinLengthValidator(1))
        if min_length is not None:
            warnings.warn("Argument min_length does nothing and is deprecated.", DeprecationWarning)
        if max_length is not None:
            warnings.warn("Argument max_length does nothing and is deprecated.", DeprecationWarning)

    def decode_environ(self, value):
        """
        Decode JSON value or split value by delimiters to a dict, if JSONDecodeError is raised.

        Default delimiter to distinguish single items is a whitespace sequence, items are then split by equal sign by
        default. Both delimiters can be changed via instance attributes ``inner_delimiter`` and ``outer_delimiter``.

        Args:
            value (str):

        Raises:
            ValueError: not enough values to unpack

        Returns:
            dict:
        """
        try:
            value = super().decode_environ(value)
        except json.decoder.JSONDecodeError:
            key_func = self.key_type or (lambda v: v)
            value_func = self.value_type or (lambda v: v)
            value = {
                key_func(k): value_func(v)
                for k, v in [value.split(self.inner_delimiter, 2) for value in value.split(self.outer_delimiter)]
            }
        return value


# Complex settings ------------------------------------------------------------
class ObjectSetting(Setting):
    """
    Object setting.

    This setting allows to return an object given its Python path (a.b.c).
    """

    default_validators = (TypeValidator(str),)

    def __init__(
        self,
        name="",
        default=None,
        required=False,
        prefix="",
        call_default=True,
        transform_default=False,
        validators=(),
        min_length=None,
        max_length=None,
        empty=None,
    ):
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
            validators (list of callables): list of additional validators to use.
            min_length (int): Noop. Deprecated.
            max_length (int): Noop. Deprecated.
            empty (bool): Noop. Deprecated.
        """
        super().__init__(
            name=name,
            default=default,
            required=required,
            prefix=prefix,
            call_default=call_default,
            transform_default=transform_default,
            validators=validators,
        )
        if min_length is not None:
            warnings.warn("Argument min_length does nothing and is deprecated.", DeprecationWarning)
        if max_length is not None:
            warnings.warn("Argument max_length does nothing and is deprecated.", DeprecationWarning)
        if empty is not None:
            warnings.warn("Argument empty does nothing and is deprecated.", DeprecationWarning)

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

        obj_parent_modules = path.split(".")
        objects = [obj_parent_modules.pop(-1)]

        while True:
            try:
                parent_module_path = ".".join(obj_parent_modules)
                parent_module = importlib.import_module(parent_module_path)
                break
            except ImportError:
                if len(obj_parent_modules) == 1:
                    raise ImportError("No module named '%s'" % obj_parent_modules[0])
                objects.insert(0, obj_parent_modules.pop(-1))

        current_object = parent_module
        for obj in objects:
            current_object = getattr(current_object, obj)
        return current_object

    def decode_environ(self, value):
        """
        Try to load JSON or return pure string, if JSONDecodeError is raised.

        Args:
            (string):

        Returns:
            string:
        """
        try:
            value = super().decode_environ(value)
        except json.decoder.JSONDecodeError:
            value = str(value)
        return value


# Callable path settings ------------------------------------------------------
class CallablePathSetting(ObjectSetting):
    """
    Callable path setting.

    This setting value should be string containing a dotted path to a callable.
    """

    def validate(self, value):
        """
        Check whether the value is path to a callable.

        We disregard the raw value and use transformed value instead.
        """
        super().validate(value)
        transformed_value = self.value
        if not callable(transformed_value):
            raise ValidationError("Value %(value)s is not a callable.", params={"value": transformed_value})


# Nested settings -------------------------------------------------------------
class NestedDictSetting(DictSetting):
    """
    Nested dict setting.

    Environment variables are not passed to inner settings.
    """

    def __init__(self, settings, *args, **kwargs):
        """
        Initialization method.

        Args:
            settings (dict): subsettings.
            name (str): the name of the setting.
            default (dict): default value given to the setting.
            required (bool): whether the setting is required or not.
            prefix (str):
                the setting's prefix (overrides ``AppSettings.Meta`` prefix).
            call_default (bool): whether to call the default (if callable).
            transform_default (bool): whether to transform the default value.
            validators (list of callables): list of additional validators to use.
            key_type: the type of the dict keys.
            value_type (type): the type of dict values.
            min_length (int): minimum length of the iterable (included).
            max_length (int): maximum length of the iterable (included).
            empty (bool): whether empty iterable is allowed. Deprecated in favor of min_length.
        """
        super().__init__(*args, **kwargs)
        for subname, subsetting in settings.items():
            if subsetting.name == "":
                subsetting.name = subname
            subsetting.parent_setting = self
        self.settings = settings

    def get_value(self):
        """
        Return dictionary with values of subsettings.

        Returns:
            dict: values of subsettings.
        """
        try:
            self.raw_value
        except (AttributeError, KeyError) as err:
            self._reraise_if_required(err)
            default_value = self.default_value
            if self.transform_default:
                return self.transform(default_value)
            return default_value
        else:
            # If setting is defined, load values of all subsettings.
            value = {}
            for key, subsetting in self.settings.items():
                value[key] = subsetting.get_value()
            return value

    def check(self):
        """
        Validate the setting value.

        Raises:
            AttributeError: if the setting is missing and required.
            ValueError: (or other Exception) if the raw value is invalid.
        """
        super().check()
        errors = []  # type: List[str]
        try:
            raw_value = self.raw_value
        except (AttributeError, KeyError):
            # If not required and not passed
            pass
        else:
            if raw_value is not None:
                for subsetting in self.settings.values():
                    try:
                        subsetting.check()
                    except ValidationError as error:
                        errors.extend(error.messages)
                if errors:
                    raise ValidationError(errors)


class NestedSetting(NestedDictSetting):
    """Deprecated alias for NestedDictSetting."""

    def __init__(self, *args, **kwargs):
        """
        Initialization method.

        Args:
            settings (dict): subsettings.
            name (str): the name of the setting.
            default (dict): default value given to the setting.
            required (bool): whether the setting is required or not.
            prefix (str):
                the setting's prefix (overrides ``AppSettings.Meta`` prefix).
            call_default (bool): whether to call the default (if callable).
            transform_default (bool): whether to transform the default value.
            validators (list of callables): list of additional validators to use.
            key_type: the type of the dict keys.
            value_type (type): the type of dict values.
            min_length (int): minimum length of the iterable (included).
            max_length (int): maximum length of the iterable (included).
            empty (bool): whether empty iterable is allowed. Deprecated in favor of min_length.
        """
        super().__init__(*args, **kwargs)
        warnings.warn("NestedSetting is deprecated in favor of NestedDictSetting.", DeprecationWarning)


class NestedListSetting(IterableSetting):
    """
    Nested list setting.

    Environment variables are not passed to inner settings.
    """

    def __init__(self, inner_setting, *args, **kwargs):
        """
        Initialization method.

        Args:
            inner_setting (Setting): setting that should be applied to list items.
                NestedDictSetting is not supported at the moment.
            name (str): the name of the setting.
            default (dict): default value given to the setting.
            required (bool): whether the setting is required or not.
            prefix (str):
                the setting's prefix (overrides ``AppSettings.Meta`` prefix).
            call_default (bool): whether to call the default (if callable).
            transform_default (bool): whether to transform the default value.
            validators (list of callables): list of additional validators to use.
            key_type: the type of the dict keys.
            value_type (type): the type of dict values.
            min_length (int): minimum length of the iterable (included).
            max_length (int): maximum length of the iterable (included).
            empty (bool): whether empty iterable is allowed. Deprecated in favor of min_length.
        """
        super().__init__(*args, **kwargs)
        if not inner_setting.name:
            inner_setting.name = self.name
        inner_setting.parent_setting = self
        self.inner_setting = inner_setting

    def get_value(self):
        try:
            value = self.raw_value
        except (AttributeError, KeyError) as err:
            self._reraise_if_required(err)
            default_value = self.default_value
            if self.transform_default:
                return self.transform(default_value)
            return default_value
        else:
            return_value = []
            for index, item in enumerate(value):
                self.inner_setting.nested_list_index = index
                return_value.append(self.inner_setting.get_value())
            return tuple(return_value)

    def check(self):
        """Check the nested list setting itself and all its items."""
        super().check()
        try:
            value = self.raw_value
        except (AttributeError, KeyError) as err:
            self._reraise_if_required(err)
        else:
            errors = []  # type: List[str]
            for index, item in enumerate(value):
                try:
                    self.inner_setting.nested_list_index = index
                    self.inner_setting.check()
                except ValidationError as error:
                    errors.extend(error.messages)
            if errors:
                raise ValidationError(errors)

    def transform(self, value):
        """Transform each item in the list."""
        return tuple(self.inner_setting.transform(item) for item in value)


class FileSetting(Setting):
    """
    File setting.

    Value of this setting is a pathlib.Path instance.
    """

    def __init__(
        self,
        name="",
        default=None,
        required=False,
        prefix="",
        call_default=True,
        transform_default=False,
        validators=(),
        mode=None,
    ):
        """
        Initialization method.

        Note that attribute ``mode`` is used in ``FileValidator``. For more information check its documentation.

        Args:
            name (str): the name of the setting.
            default (object): default value given to the setting.
            required (bool): whether the setting is required or not.
            prefix (str):
                the setting's prefix (overrides ``AppSettings.Meta`` prefix).
            call_default (bool): whether to call the default (if callable).
            transform_default (bool): whether to transform the default value.
            validators (list of callables): list of additional validators to use.
            mode (optional int): Required permission for the file. None means no validation (f.e. file does not exist
                yet), other values might consist of inclusive OR between F_OK, R_OK, W_OK and X_OK constants. When
                checking read, write or execute permission, file existence (F_OK) is implicitly required. For more
                information check ``os.access`` documentation (https://docs.python.org/3/library/os.html#os.access).
        """
        super().__init__(
            name=name,
            default=default,
            required=required,
            prefix=prefix,
            call_default=call_default,
            transform_default=transform_default,
            validators=validators,
        )
        if mode is not None:
            self.validators.append(FileValidator(mode))

    def transform(self, value):
        """Transform value to Path instance."""
        return Path(super().transform(value))
