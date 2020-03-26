"""Test settings validators."""
import os
import stat
import tempfile

import pytest
from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from appsettings import (
    DictKeysTypeValidator,
    DictValuesTypeValidator,
    FileValidator,
    TypeValidator,
    ValuesTypeValidator,
)


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


class FileValidatorTestCase(SimpleTestCase):
    """Test FileValidator."""

    def test_exists_success(self):
        with tempfile.NamedTemporaryFile() as fd:
            FileValidator(os.F_OK)(fd.name)

    def test_exists_error(self):
        fd = tempfile.NamedTemporaryFile()
        fd.close()
        with pytest.raises(ValidationError, match=r"Insufficient permissions for the file .+\."):
            FileValidator(os.F_OK)(fd.name)

    def test_error_message(self):
        fd = tempfile.NamedTemporaryFile()
        fd.close()
        with pytest.raises(ValidationError, match=r"My own message for .*!"):
            FileValidator(os.F_OK, "My own message for %(value)s!")(fd.name)

    def test_read_perm_success(self):
        with tempfile.NamedTemporaryFile() as fd:
            FileValidator(os.R_OK)(fd.name)

    def test_read_perm_error(self):
        with tempfile.NamedTemporaryFile() as fd:
            current_perms = stat.S_IMODE(os.lstat(fd.name).st_mode)
            os.chmod(fd.name, current_perms & ~stat.S_IRUSR)
            with pytest.raises(ValidationError, match=r"Insufficient permissions for the file .+\."):
                FileValidator(os.R_OK)(fd.name)

    def test_write_perm_success(self):
        with tempfile.NamedTemporaryFile() as fd:
            FileValidator(os.W_OK)(fd.name)

    def test_write_perm_error(self):
        with tempfile.NamedTemporaryFile() as fd:
            current_perms = stat.S_IMODE(os.lstat(fd.name).st_mode)
            os.chmod(fd.name, current_perms & ~stat.S_IWUSR)
            with pytest.raises(ValidationError, match=r"Insufficient permissions for the file .+\."):
                FileValidator(os.W_OK)(fd.name)

    def test_exec_perm_success(self):
        with tempfile.NamedTemporaryFile() as fd:
            current_perms = stat.S_IMODE(os.lstat(fd.name).st_mode)
            os.chmod(fd.name, current_perms | stat.S_IXUSR)
            FileValidator(os.X_OK)(fd.name)

    def test_exec_perm_error(self):
        with tempfile.NamedTemporaryFile() as fd:
            with pytest.raises(ValidationError, match=r"Insufficient permissions for the file .+\."):
                FileValidator(os.X_OK)(fd.name)

    def test_all_permissions(self):
        with tempfile.NamedTemporaryFile() as fd:
            current_perms = stat.S_IMODE(os.lstat(fd.name).st_mode)
            os.chmod(fd.name, current_perms | stat.S_IXUSR)
            FileValidator(os.R_OK | os.W_OK | os.X_OK)(fd.name)
