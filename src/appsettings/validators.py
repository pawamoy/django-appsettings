"""Basic set of setting validators."""
import os

from django.core.exceptions import ValidationError


class TypeValidator(object):
    """Validator which checks type of the value."""

    message = "Value %(value)s is not of type %(type)s."

    def __init__(self, value_type, message=None):
        self.value_type = value_type
        if message:
            self.message = message

    def __call__(self, value):
        if not isinstance(value, self.value_type):
            params = {"value": value, "type": self.value_type.__name__}
            raise ValidationError(self.message, params=params)


class ValuesTypeValidator(object):
    """Validator which checks types of iterable values."""

    message = "Element %(value)s is not of type %(type)s."

    def __init__(self, value_type, message=None):
        self.value_type = value_type
        if message:
            self.message = message

    def __call__(self, value):
        for element in value:
            if not isinstance(element, self.value_type):
                params = {"value": element, "type": self.value_type.__name__}
                raise ValidationError(self.message, params=params)


class DictKeysTypeValidator(object):
    """Validator which checks types of dict keys."""

    message = "The key %(key)s is not of type %(type)s."

    def __init__(self, key_type, message=None):
        self.key_type = key_type
        if message:
            self.message = message

    def __call__(self, value):
        for key in value:
            if not isinstance(key, self.key_type):
                params = {"key": key, "type": self.key_type.__name__}
                raise ValidationError(self.message, params=params)


class DictValuesTypeValidator(object):
    """Validator which checks types of dict values."""

    message = "Item %(key)s's value %(value)s is not of type %(type)s."

    def __init__(self, value_type, message=None):
        self.value_type = value_type
        if message:
            self.message = message

    def __call__(self, value):
        for key, element in value.items():
            if not isinstance(element, self.value_type):
                params = {"key": key, "value": element, "type": self.value_type.__name__}
                raise ValidationError(self.message, params=params)


class FileValidator(object):
    """Validator which checks file existence and permissions."""

    message = "Insufficient permissions for the file %(value)s."

    def __init__(self, mode, message=None):
        """
        Validator initialization.

        Args:
            mode (optional int): Required permission for the file. Values might consist of inclusive OR between F_OK,
                R_OK, W_OK and X_OK constants. When checking read, write or execute permission, file existence (F_OK) is
                implicitly required. For more information check ``os.access`` documentation
                (https://docs.python.org/3/library/os.html#os.access).
            message (str): Override default ``ValidationError`` message.
        """
        self.mode = mode
        if message:
            self.message = message

    def __call__(self, value):
        """Validate the ``value``."""
        if not os.access(value, self.mode):
            raise ValidationError(self.message, params={"value": value})
