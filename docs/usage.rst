Usage
=====

Declaring your settings
-----------------------

To declare your application setting, create a settings class inheriting from
``appsettings.AppSettings``:

.. code:: python

    import appsettings


    class MySettings(appsettings.AppSettings):
        boolean_setting = appsettings.BooleanSetting(default=False)
        required_setting = appsettings.StringSetting(required=True)
        named_setting = appsettings.IntegerSetting(name='integer_setting')
        prefixed_setting = appsettings.ListSetting(prefix='my_app_')

        class Meta:
            setting_prefix = 'app_'

In this example, we declared four different settings in our class:
``boolean_setting``, ``required_setting``, ``named_setting``, and
``prefixed_setting``.

The corresponding variable names in a Django project's settings file will be:
- ``boolean_setting``: ``APP_BOOLEAN_SETTING``, because no name was given.
- ``required_setting``: ``APP_REQUIRED_SETTING``, because no name was given.
- ``named_setting``: ``APP_INTEGER_SETTING``, because a name was given.
- ``prefixed_setting``: ``MY_APP_PREFIXED_SETTING``, because we overrode the class prefix.

We could as well give both name and prefix to customize entirely the corresponding
variable name in the settings file.

Using a callable as default value
'''''''''''''''''''''''''''''''''

Sometimes you may want to pass a callable as a default value. To ensure the
callable is called, or to prevent it, use the ``call_default`` parameter:

.. code:: python

    from datetime import datetime
    import appsettings


    class MySettings(appsettings.AppSettings):
        # expect a time value, allow calling
        first_access = appsettings.Setting(default=datetime.now, call_default=True)

        # expect a function returning current time, prevent calling
        now_function = appsettings.Setting(default=datetime.now, call_default=False)


``call_default`` is True by default on every setting class except ``ObjectSetting``.

.. important::

    Note that ``call_default`` is only used when the related setting is missing
    from the project settings!

Checking the settings
---------------------

In my opinion, the best place to check your application settings is in your
application configuration class:

.. code:: python

    import django
    import appsettings


    class AppSettings(appsettings.AppSettings):
        string_list = appsettings.ListSetting(item_type=str, empty=False, required=True, max_length=4)

        class Meta:
            setting_prefix = 'my_app_'


    class AppConfig(django.apps.AppConfig):
        name = 'my_app'
        verbose_name = 'My Application'

        def ready(self):
            # check every settings at startup, raise one exception
            # with all errors as one message
            AppSettings.check()

In the above example, if ``MY_APP_STRING_LIST`` is not defined, or if it is not
a list object, or if it's empty, or if it has more than 4 elements,
``AppSettings.check()`` will raise a ``ImproperlyConfigured`` exception.
If you had more settings declared in your settings class, then the
``ImproperlyConfigured`` exception would be raised with a message being a
concatenation of the first exception for each setting checked.

You can also check each setting individually, for example:

.. code:: python

    for setting in AppSettings.settings.values():
        setting_object.check()

If the setting's value is invalid, it will raise an exception
(usually ``ValueError``).

Using the settings in your code
-------------------------------

Testing the settings
--------------------

Writing your own setting class
------------------------------

Writing your own type checker
-----------------------------
