# -*- coding: utf-8 -*-

u"""Django AppSettings package."""

__version__ = '0.1.0'

class AppSettingsExample(object):
    """
    Application settings class.

    This class provides static getters for each setting, and also an instance
    ``load`` method to load every setting in an instance.
    """

    DEFAULT_RESPONSE = False
    SKIP_IMPLICIT = False
    LOG_ACCESS = True
    LOG_PRIVILEGES = True
    LOG_HIERARCHY = True

    def load(self, settings=None):
        """
        Load settings in self.

        Args:
        settings (list): list of settings to load (strings).
        """
        if settings is not None:
            for setting in settings:
                setattr(self, setting.upper(), getattr(
                    AppSettings, 'get_%s' % setting.lower())())
            return
        self.DEFAULT_RESPONSE = AppSettings.get_default_response()
        self.SKIP_IMPLICIT = AppSettings.get_skip_implicit()
        self.LOG_ACCESS = AppSettings.get_log_access()
        self.LOG_PRIVILEGES = AppSettings.get_log_privileges()
        self.LOG_HIERARCHY = AppSettings.get_log_hierarchy()

    @staticmethod
    def check():
        """Run every check method for settings."""
        AppSettings.check_default_response()
        AppSettings.check_skip_implicit()
        AppSettings.check_log_access()
        AppSettings.check_log_privileges()
        AppSettings.check_log_hierarchy()

    @staticmethod
    def check_default_response():
        """Check the value of given default response setting."""
        default_response = AppSettings.get_default_response()
        if not isinstance(default_response, bool):
            raise ValueError('DEFAULT_RESPONSE must be True or False')

    @staticmethod
    def get_default_response():
        """Return default response setting."""
        return getattr(settings, 'CERBERUS_DEFAULT_RESPONSE',
                       AppSettings.DEFAULT_RESPONSE)

    @staticmethod
    def check_skip_implicit():
        """Check the value of given skip implicit setting."""
        skip_implicit = AppSettings.get_skip_implicit()
        if not isinstance(skip_implicit, bool):
            raise ValueError('SKIP_IMPLICIT must be True or False')

    @staticmethod
    def get_skip_implicit():
        """Return skip implicit setting."""
        return getattr(settings, 'CERBERUS_SKIP_IMPLICIT',
                       AppSettings.SKIP_IMPLICIT)

    @staticmethod
    def check_log_access():
        """Check the value of given log access setting."""
        log_access = AppSettings.get_log_access()
        if not isinstance(log_access, bool):
            raise ValueError('LOG_ACCESS must be True or False')

    @staticmethod
    def get_log_access():
        """Return log access setting."""
        return getattr(settings, 'CERBERUS_LOG_ACCESS',
                       AppSettings.LOG_ACCESS)

    @staticmethod
    def check_log_privileges():
        """Check the value of given log privileges setting."""
        log_privileges = AppSettings.get_log_privileges()
        if not isinstance(log_privileges, bool):
            raise ValueError('LOG_PRIVILEGES must be True or False')

    @staticmethod
    def get_log_privileges():
        """Return log privileges setting."""
        return getattr(settings, 'CERBERUS_LOG_PRIVILEGES',
                       AppSettings.LOG_PRIVILEGES)

    @staticmethod
    def check_log_hierarchy():
        """Check the value of given log hierarchy setting."""
        log_hierarchy = AppSettings.get_log_hierarchy()
        if not isinstance(log_hierarchy, bool):
            raise ValueError('LOG_HIERARCHY must be True or False')

    @staticmethod
    def get_log_hierarchy():
        """Return log hierarchy setting."""
        return getattr(settings, 'CERBERUS_LOG_HIERARCHY',
                       AppSettings.LOG_HIERARCHY)
