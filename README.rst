==================
Django AppSettings
==================

.. start-badges



|travis|
|codacygrade|
|codacycoverage|
|version|
|wheel|
|gitter|


.. |travis| image:: https://travis-ci.org/Genida/django-appsettings.svg?branch=master
    :target: https://travis-ci.org/Genida/django-appsettings/
    :alt: Travis Build Status

.. |codacygrade| image:: https://api.codacy.com/project/badge/Grade/20c775cc36804ddda8a70eb05b64ce92
    :target: https://www.codacy.com/app/Genida/django-appsettings/dashboard
    :alt: Codacy Grade

.. |codacycoverage| image:: https://api.codacy.com/project/badge/Coverage/20c775cc36804ddda8a70eb05b64ce92
    :target: https://www.codacy.com/app/Genida/django-appsettings/dashboard
    :alt: Codacy Coverage

.. |version| image:: https://img.shields.io/pypi/v/django-app-settings.svg?style=flat
    :target: https://pypi.org/project/django-app-settings/
    :alt: PyPI latest release

.. |wheel| image:: https://img.shields.io/pypi/wheel/django-app-settings.svg?style=flat
    :target: https://pypi.org/project/django-app-settings/
    :alt: PyPI Wheel

.. |gitter| image:: https://badges.gitter.im/Genida/django-appsettings.svg
    :target: https://gitter.im/Genida/django-appsettings
    :alt: Join the chat at https://gitter.im/Genida/django-appsettings



.. end-badges

Application settings helper for Django apps.

Why another *app settings* app?
Because none of the other suited my needs!

This one is simple to use, and works with unit tests overriding settings.

Installation
============

::

    pip install django-app-settings

Documentation
=============

`On ReadTheDocs`_

.. _`On ReadTheDocs`: http://django-appsettings.readthedocs.io/

Development
===========

To run all the tests: ``tox``. See `CONTRIBUTING`_.

.. _`CONTRIBUTING`: https://github.com/Genida/django-appsettings/blob/master/CONTRIBUTING.rst

Quick usage
===========

.. code:: python

    # Define your settings class
    import appsettings


    class MySettings(appsettings.AppSettings):
        boolean_setting = appsettings.BooleanSetting(default=False)
        required_setting = appsettings.StringSetting(required=True)
        named_setting = appsettings.IntegerSetting(name='integer_setting')
        prefixed_setting = appsettings.ListSetting(prefix='my_app_')

        class Meta:
            setting_prefix = 'app_'


    # Related settings in settings.py
    APP_INTEGER_SETTING = -24
    MY_APP_PREFIXED_SETTING = []


    # Instantiate your class wherever you need to
    appconf = MySettings()
    assert appconf.boolean_setting is False  # True (default value)
    assert appconf.required_setting == 'hello'  # raises AttributeError
    assert appconf.named_setting < 0  # True
    assert appconf.prefixed_setting  # False (empty list)


    # Values are cached to avoid perf issues
    with override_settings(APP_REQUIRED_SETTING='hello',
                           APP_INTEGER_SETTING=0):
        # ...but cache is cleaned on Django's setting_changed signal
        assert appconf.required_setting == 'hello'  # True
        assert appconf.named_setting < 0  # False


    # You can still access settings through the class itself (values not cached)
    print(MySettings.boolean_setting.get_value())  # explicit call
    print(MySettings.boolean_setting.value)  # with property


    # Run type checking and required presence on all settings at once
    MySettings.check()  # raises Django's ImproperlyConfigured (missing required_setting)
    # MySettings.check() is best called in django.apps.AppConfig's ready method


You can easily create your own Setting classes for more complex settings.

.. code:: python

    import re

    import appsettings
    from django.core.exceptions import ValidationError


    class RegexSetting(appsettings.Setting):
        def validate(self, value):
            re_type = type(re.compile(r'^$'))
            if not isinstance(value, (re_type, str)):
                # Raise ValidationError
                raise ValidationError('Value must be a string or a compiled regex (use re.compile)')

        def transform(self, value):
            # ensure it always returns a compiled regex
            if isinstance(value, str):
                value = re.compile(value)
            return value


Please check the documentation to see even more advanced usage.

License
=======

Software licensed under `ISC`_ license.

.. _ISC: https://www.isc.org/downloads/software-support-policy/isc-license/

