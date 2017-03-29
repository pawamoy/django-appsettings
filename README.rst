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

Usage
=====

With recent Django versions, it is recommended to put your settings in an
``apps.py`` module of your Django app, though you can put it wherever you want.
The following is just an example.

.. code:: python

    from django.apps import AppConfig
    import appsettings as aps

    class MyAppConfig(AppConfig):
        name = 'my_app'
        verbose_name = 'My Application'

        def ready(self):
            AppSettings.check()


    class AppSettings(aps.AppSettings):
        always_use_ice_cream = aps.BooleanSetting(default=True)
        attr_name = aps.StringSetting(name='SETTING_NAME')

        # if you have complex treatment to do on setting
        complex_setting = aps.Setting(transformer=custom_method, checker=custom_checker)

        # if you need to import a python object (module/class/method)
        imported_object = aps.ImportedObjectSetting(default='app.default.object')

        class Meta:
            setting_prefix = 'ASH'  # settings must be prefixed with ASH

Then in other modules:

.. code:: python

    from .apps import AppSettings

    # instantiation will load and transform every settings
    app_settings = AppSettings()
    app_settings.attr_name == 'something'

    # or, and in order to work with tests overriding settings
    AppSettings.get_always_use_ice_cream()  # to get ASH_ALWAYS_USE_ICE_CREAM setting dynamically
    my_python_object = AppSettings.get_imported_object()

You can access settings directly from the settings class, but also from the
settings instances:

.. code:: python

    my_setting = AppSettings.my_setting
    my_setting.get()  # get and transform
    my_setting.check()  # get and check
    my_setting.get_raw()  # just get the value in django settings

.. warning::

    After instantiating an AppSettings class, the settings won't be
    instances of Setting anymore but the result of their ``get`` method.

    .. code:: python

        appsettings = AppSettings()
        appsettings.my_setting == AppSettings.my_setting        # False
        appsettings.my_setting == AppSettings.my_setting.get()  # True
        appsettings.my_setting == AppSettings.get_my_setting()  # True

Running ``AppSettings.check()`` will raise an ``ImproperlyConfigured``
exception if at least one of the settings' ``check`` methods raised an
exception. It will also print all caught exceptions.

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
