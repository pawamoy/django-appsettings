"""Test settings validators."""
from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from appsettings import DictKeysTypeValidator, DictValuesTypeValidator, TypeValidator, ValuesTypeValidator


class TypeValidatorTestCase(SimpleTestCase):
    """Test TypeValidator."""

    def test_valid(self):
        TypeValidator(int)(42)
        TypeValidator(float)(4.5)
        TypeValidator(list)([])

    def test_invalid(self):
        with self.assertRaisesMessage(ValidationError, "Value None is not of type int."):
            TypeValidator(int)(None)


class ValuesTypeValidatorTestCase(SimpleTestCase):
    """Test ValuesTypeValidator."""

    def test_valid(self):
        ValuesTypeValidator(int)([42, 14, 1676])
        ValuesTypeValidator(int)({42, 14, 1676})
        ValuesTypeValidator(int)((42, 14, 1676))

    def test_invalid(self):
        with self.assertRaisesMessage(ValidationError, "Element None is not of type int."):
            ValuesTypeValidator(int)([42, None, 1676])


class DictKeysTypeValidatorTestCase(SimpleTestCase):
    """Test DictKeysTypeValidator."""

    def test_valid(self):
        DictKeysTypeValidator(int)({42: "a", 1676: "b"})

    def test_invalid(self):
        with self.assertRaisesMessage(ValidationError, "The key None is not of type int."):
            DictKeysTypeValidator(int)({42: "a", None: "b"})


class DictValuesTypeValidatorTestCase(SimpleTestCase):
    """Test DictValuesTypeValidator."""

    def test_valid(self):
        DictValuesTypeValidator(int)({"a": 42, "b": 1676})

    def test_invalid(self):
        with self.assertRaisesMessage(ValidationError, "Item b's value None is not of type int."):
            DictValuesTypeValidator(int)({"a": 42, "b": None})
