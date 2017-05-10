==================
Django AppSettings
==================

.. start-badges



|travis|
|codacygrade|
|codacycoverage|
|version|
|wheel|
|pyup|
|gitter|


.. |travis| image:: https://travis-ci.org/Pawamoy/django-appsettings.svg?branch=master
    :target: https://travis-ci.org/Pawamoy/django-appsettings/
    :alt: Travis-CI Build Status

.. |codacygrade| image:: https://api.codacy.com/project/badge/Grade/20c775cc36804ddda8a70eb05b64ce92
    :target: https://www.codacy.com/app/Pawamoy/django-appsettings/dashboard
    :alt: Codacy Code Quality Status

.. |codacycoverage| image:: https://api.codacy.com/project/badge/Coverage/20c775cc36804ddda8a70eb05b64ce92
    :target: https://www.codacy.com/app/Pawamoy/django-appsettings/dashboard
    :alt: Codacy Code Coverage

.. |pyup| image:: https://pyup.io/repos/github/Pawamoy/django-appsettings/shield.svg
    :target: https://pyup.io/repos/github/Pawamoy/django-appsettings/
    :alt: Updates

.. |version| image:: https://img.shields.io/pypi/v/django-app-settings.svg?style=flat
    :target: https://pypi.python.org/pypi/django-app-settings/
    :alt: PyPI Package latest release

.. |wheel| image:: https://img.shields.io/pypi/wheel/django-app-settings.svg?style=flat
    :target: https://pypi.python.org/pypi/django-app-settings/
    :alt: PyPI Wheel

.. |gitter| image:: https://badges.gitter.im/Pawamoy/django-appsettings.svg
    :target: https://gitter.im/Pawamoy/django-appsettings
    :alt: Join the chat at https://gitter.im/Pawamoy/django-appsettings



.. end-badges

Application settings helper for Django apps.

Why another *app settings* app?
Because none of the other suited my needs!

This one is simple to use, and works with unit tests overriding settings.

Quick usage
===========

.. code:: python

    # my_package/apps.py

    from django.apps import AppConfig
    import appsettings as aps


    class AppSettings(aps.AppSettings):
        my_setting = aps.Setting(name='basic_setting', default=25)

        required_setting = aps.Setting(required=True)  # name='REQUIRED_SETTING'

        typed_setting = aps.StringSetting(prefix='string_')
        # -> typed_setting.full_name == 'STRING_TYPED_SETTING'

        custom_setting = RegexSetting()  # -> see RegexSetting class below

        class Meta:
          # default prefix for every settings
          setting_prefix = 'example_'


    class RegexSetting(Setting):
        def check():
            value = self.get_raw()  # should always be called to check required condition
            if value != self.default:  # always allow default to pass
                re_type = type(re.compile(r'^$'))
                if not isinstance(value, (re_type, str)):
                    # raise whatever exception
                    raise ValueError('%s must be a a string or a compiled regex '
                                     '(use re.compile)' % self.full_name)

        def transform(self):
            value = self.get_raw()
            # ensure it always return a compiled regex
            if isinstance(value, str):
                value = re.compile(value)
            return value


    class MyAppConfig(AppConfig):
        name = 'my_app'
        verbose_name = 'My Application'

        def ready(self):
            # check every settings at startup, raise one exception
            # with all errors in its message
            AppSettings.check()


.. code:: python

    # django_project/settings.py
    EXAMPLE_BASIC_SETTING = 26
    EXAMPLE_REQUIRED_SETTING = 'something'

.. code:: python

    # my_package/other_module.py

    from .apps import AppSettings


    regex = AppSettings.custom_setting.get()  # alias for transform()

    # instantiate the class to load each and every settings
    appsettings = AppSettings()
    appsettings.my_setting == 25  # False: 26


**Settings classes:**

- StringSetting: default = ''
- IntegerSetting: default = 0
- PositiveIntegerSetting: default = 0
- BooleanSetting: default = False
- FloatSetting: default = 0.0
- PositiveFloatSetting: default = 0.0
- ListSetting: default = []
- SetSetting: default = ()
- DictSetting: default = {}
- ImportedObjectSetting: default = None

*Are the following settings useful? Please tell me on Gitter.*

- StringListSetting: default = []
- StringSetSetting: default = ()
- IntegerListSetting: default = []
- IntegerSetSetting: default = ()
- BooleanListSetting: default = []
- BooleanSetSetting: default = ()
- FloatListSetting: default = []
- FloatSetSetting: default = ()

License
=======

Software licensed under `ISC`_ license.

.. _ISC: https://www.isc.org/downloads/software-support-policy/isc-license/

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

To run all the tests: ``tox``
