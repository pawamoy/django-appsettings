Usage
=====

Declaring your settings
-----------------------

To declare your application settings, create a settings class inheriting from
``appsettings.AppSettings``:

.. code:: python

    import appsettings


    class MySettings(appsettings.AppSettings):
        boolean_setting = appsettings.BooleanSetting(default=False)
        required_setting = appsettings.StringSetting(required=True)
        named_setting = appsettings.IntegerSetting(name='integer_setting')
        prefixed_setting = appsettings.ListSetting(prefix='my_app_')
        nested_setting = appsettings.NestedSetting(settings=dict(
            foo_setting=appsettings.BooleanSetting(prefix='inner_'),
        ))

        class Meta:
            setting_prefix = 'app_'

In this example, we declared six different settings in our class:
``boolean_setting``, ``required_setting``, ``named_setting``,
``prefixed_setting``, ``nested_setting`` and ``foo_setting``
(which is inner setting of ``nested_setting``).

The corresponding variable names in a Django project's settings file will be:

- ``boolean_setting``: ``APP_BOOLEAN_SETTING``, because no name was given.
- ``required_setting``: ``APP_REQUIRED_SETTING``, because no name was given.
- ``named_setting``: ``APP_INTEGER_SETTING``, because a name was given.
- ``prefixed_setting``: ``MY_APP_PREFIXED_SETTING``, because we overrode the class prefix.
- ``nested_setting``: ``APP_NESTED_SETTING``, because no name was given. The corresponding value is a dictionary.
- ``foo_setting``: ``APP_NESTED_SETTING['INNER_FOO_SETTING']``, because ``foo_setting``
  is inner setting of ``nested_setting`` and prefix was given.

We could as well give both name and prefix to customize entirely the corresponding
variable name in the settings file.

Using a callable as default value
'''''''''''''''''''''''''''''''''

Sometimes you may want to pass a callable as a default value. To ensure that the
callable is called, or to prevent it, use the ``call_default`` parameter:

.. code:: python

    from datetime import datetime
    import appsettings


    class MySettings(appsettings.AppSettings):
        # expect a datetime value, allow calling
        first_access = appsettings.Setting(default=datetime.now, call_default=True)

        # expect a function returning current time, prevent calling
        now_function = appsettings.Setting(default=datetime.now, call_default=False)


``call_default`` is True by default on every setting class except ``ObjectSetting``.

.. important::

    Note that ``call_default`` is only used when the related setting is missing
    from the project settings!

Using environment variables
'''''''''''''''''''''''''''

Nowadays it became more and more popular to read settings from the environment.
This functionality is supported as well. If the setting is found in environment, its
value is used and takes precedence over any value present in the settings module.
By default, all values are parsed as JSON, see other supported values in description
of individual setting classes.

Anyway, you can override the environ value parsing on your own. It is done by the
``decode_environ(self, value)`` method.

Example
-------

.. code:: python

    import os
    from appsettings import AppSettings, StringSetting

    class MySettings(AppSettings):
        example = StringSetting()

    os.environ['EXAMPLE'] = 'Example value'
    settings = MySettings()
    print(settings.example)  # >>> 'Example value'


Checking the settings
---------------------

The best place to check your application settings is in your
application configuration class:

.. code:: python

    import django
    import appsettings


    class AppSettings(appsettings.AppSettings):
        string_list = appsettings.ListSetting(item_type=str,
                                              empty=False,
                                              required=True,
                                              max_length=4)

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
        setting.check()


Using the settings in your code
-------------------------------

Once your settings class is ready, you will be able to instantiate it to
benefit from its simplicity of use and its caching feature:

.. code:: python

    # let say you declared your Settings class in apps.py
    from .apps import Settings

    settings = Settings()

    print(settings.string_list[0])
    print(settings.now_function())
    print(settings.first_access.day)

Nested settings
'''''''''''''''

Django AppSettings provides two types of nested settings:
``NestedListSetting`` and ``NestedDictSetting``.

Nested list settings
^^^^^^^^^^^^^^^^^^^^

You can use nested list settings to generalize ordinary flat setting to a list.
All you have to do is pass an instance of that setting as ``inner_setting`` attribute.
You can even add custom validators and other attributes to that inner setting.
However, ``name``, ``default``, ``call_default``, ``transform_default``, ``required``
and ``prefix`` attributes makes no sense for the inner setting and are silently ignored.
Let's say that we want to create setting that contains list of integers.
We can express it thus:

.. code:: python

   import appsettings

   class MySettings(appsettings.AppSettings):
      int_list = appsettings.NestedListSetting(
         inner_setting=appsettings.IntegerSetting()
      )

Of course, we could just use ``ListSetting`` with ``item_type=int``.
However, ``NestedListSetting`` can be applied to any flat setting, e.g. ``ObjectSetting``.
Transformation and validation of the inner setting is applied to each of the list items individually.

Furthemore, you can also use ``NestedListSetting`` in another ``NestedListSetting`` to arbitrary depth.

.. warning::

   It is not possible to use ``NestedDictSetting`` as inner setting in ``NestedListSetting`` at the moment.
   However, it is possible to use ``NestedListSetting`` inside ``NestedDictSetting`` without limitation.

Nested dict settings
^^^^^^^^^^^^^^^^^^^^

If you want to define nested dict settings, such as django setting ``DATABASES``,
you may utilize ``NestedDictSetting``. Those are a little bit complicated, so
we'll explain them using simple example:

.. code:: python

    import appsettings


    class MySettings(appsettings.AppSettings):
        api = appsettings.NestedDictSetting(
            prefix='our_'
            settings=dict(
                server=appsettings.StringSetting(prefix='my_', required=True),
                port=appsettings.IntegerSetting(default=80, name='magic'),
            )
        )

        class Meta:
            setting_prefix = 'app_'

Attributes of the parent does not affect the attributes of the child and vice
versa. Child settings ignore the metaclass prefix. Lets see, what happens with
different configurations:

*  Empty configuration would be valid, because ``api`` setting is not required.
   In this case, ``api`` default value would be used, which is empty
   dictionary.

*  Configuration ``OUR_API={}`` would be invalid, because required item
   ``MY_SERVER`` representing subsetting ``server`` is ommited.

*  Configuration ``OUR_API={'MY_SERVER': 'localhost', 'MAGIC': 42}`` would be
   valid:

   .. code:: python

        settings = MySettings()
        print(settings.api)  # {'server': 'localhost', 'port': 42}
        print(setting.api['server'])  # 'localhost'
        print(setting.api['port'])  # 42

As you can see, value of nested dict setting is represented as a dictionary with
values of all the subsettings included. If you define other items in the
dictionary corresponding to nested setting, those other items are ignored.

Testing the settings
--------------------

When you instantiate your settings class with ``settings = Settings()``,
the ``invalidate_cache`` method of the instance is automatically connected
to the ``setting_changed`` signal sent by Django. It means that you can test
different values for your settings without worrying about invalidating the
cache each time.

.. code:: python

    from django.test import SimpleTestCase, override_settings
    from my_app.apps import Settings


    class MainTestCase(TestCase):
        def setUp(self):
            self.settings = Settings()

        def test_some_settings(self):
            # first fetch
            assert self.settings.string_list[0] == 'hello'

            # django will send setting_changed signal, cache will be cleaned
            with override_settings(MY_APP_STRING_LIST=['hello world!']):
                assert len(self.settings.string_list) == 1

            # signal sent again
            with override_settings(MY_APP_STRING_LIST=['good morning', 'world', '!']):
                assert len(self.settings.string_list) == 3

            # signal is also sent when with clause ends
            assert self.settings.string_list[0] == 'hello'

        # it works the same way with decorator
        @override_settings(MY_APP_STRING_LIST=['bye'])
        def test_string_list(self):
            assert 'bye' in self.settings.string_list

Customize setting validation
----------------------------

.. note:: New in version 0.4.

You may need to customize the setting validation.
Individual ``Settings`` use validation similar to Django form fields.

The easiest way is to pass additional validators when defining a setting.

.. code:: python

    import appsettings
    from django.core.validators import EmailValidator

    setting = appsettings.StringSetting(validators=(EmailValidator(), ))

A more robust method is to create a subclass and define a ``default_validators``.

.. code:: python

    import appsettings
    from django.core.validators import EmailValidator

    class EmailSetting(StringSetting):
        default_validators = (EmailValidator(), )

The finest-grained customization can be obtained by overriding the ``validate()`` method.

.. code:: python

    import re
    import appsettings


    class RegexSetting(appsettings.Setting):
        def validate(self, value):
            re_type = type(re.compile(r'^$'))
            if not isinstance(value, (re_type, str)):
                # Raise ValidationError
                raise ValidationError('%(value)s is not a string or a compiled regex (use re.compile)',
                                      params={'value': value})


    setting = RegexSetting()


Transforming setting values
'''''''''''''''''''''''''''

You may want your setting to be less strict about types, but make sure it
always return the same type of object. This is what the transform method is
here for:

.. code:: python

    import re
    import appsettings


    # our setting class
    class RegexSetting(appsettings.Setting):
        def __init__(
                self, name='', default=re.compile(r'^$'), **kwargs):
            super().__init__(name=name, default=default, **kwargs)

        def transform(self, value):
            # ensure it always returns a compiled regex
            if isinstance(value, str):
                value = re.compile(value)
            return value


    setting = RegexSetting()


You can also control whether the default value has to be transformed or not
with the ``transform_default`` parameter. Using the above example, you could
then instantiate your setting like this:

.. code:: python

    setting = RegexSetting(default=r'^my (regular)? expression$',
                           transform_default=True)


You can as well combine ``call_default`` and ``transform_default``:

.. code:: python

    def regex_string_generator():
        return r'^my (regular)? expression$'

    setting = RegexSetting(default=regex_string_generator,
                           call_default=True,
                           transform_default=True)

.. important:: Transformation is always done **after** calling the default value.
