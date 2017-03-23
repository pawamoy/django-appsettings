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

This one will be simple to use, and will work with unit tests overriding settings.

(Future) Usage
==============

This app is an alpha version. Development has just started. I want it to be something like that:

.. code:: python

    # in your application __init__.py

    from appsettings import AppSettingsHelper as Ash

    class AppSettings(Ash):
        always_use_ice_cream = Ash.BooleanSetting(default=True)
        attr_name = Ash.StringSetting(name='SETTING_NAME')

        # if you have complex treatment to do on setting
        complex_setting = Ash.Setting(getter=custom_method, checker=custom_checker)

        # if you need to import a python object (module/class/method)
        imported_object = Ash.ImportedObjectSetting(default='app.default.object')

        class Meta:
            settings_prefix = 'ASH'  # settings must be prefixed with ASH_


    AppSettings.check()  # will check every settings

    # then in your code

    from . import AppSettings

    app_settings = AppSettings()
    app_settings.load()  # to load every settings once and for all
    app_settings.attr_name == 'something'

    # or, and in order to work with tests overriding settings
    AppSettings.get_always_use_ice_cream()  # to get ASH_ALWAYS_USE_ICE_CREAM setting dynamically
    my_python_object = AppSettings.get_imported_object()

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
