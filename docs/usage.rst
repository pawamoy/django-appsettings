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

If the setting's value is invalid, it will raise an exception
(usually ``ValueError``).

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

If you want to define nested settings, such as django setting ``DATABASES``,
you may utilize ``NestedSetting``. Those are a little bit complicated, so
we'll explain them using simple example:

.. code:: python

    import appsettings


    class MySettings(appsettings.AppSettings):
        api = appsettings.NestedSetting(
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
        print(settings.api)  # {'server': 'localhost', 'port': 80}
        print(setting.api['server'])  # 'localhost'
        print(setting.api['port'])  # 42

As you can see, value of nested setting is represented as a dictionary with
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

Writing your own type checker
'''''''''''''''''''''''''''''

.. warning:: Checkers are deprecated, use validators instead.

The third way to customize how the setting is checked is to create
a new ``TypeChecker`` class:

.. code:: python

    import re
    import appsettings


    # option 1: passing a specific base_type (can be a tuple with several types)
    class RegexTypeChecker1(appsettings.TypeChecker):
        def __init__(self):
            re_type = type(re.compile(r'^$'))
            super(BooleanTypeChecker, self).__init__(base_type=(str, re_type))


    setting1 = appsettings.Setting(checker=RegexTypeChecker1())


    # option 2: completely overriding the __call__ method
    class RegexTypeChecker2(appsettings.TypeChecker):
        def __call__(self, name, value):
            re_type = type(re.compile(r'^$'))
            if not isinstance(value, (re_type, str)):
                # raise whatever exception
                raise ValueError('%s must be a a string or a compiled regex '
                                 '(use re.compile)' % name)


    setting2 = appsettings.Setting(checker=RegexTypeChecker2())


    # option 3: combining both type checker and setting class
    class RegexSetting(appsettings.Setting):
        def __init__(
                self, name='', default=re.compile(r'^$'), required=False,
                prefix='', call_default=True, transform_default=False):
            super(RegexSetting, self).__init__(
                name=name, default=default, required=required, prefix=prefix,
                call_default=call_default, transform_default=transform_default,
                checker=RegexTypeChecker1())


    setting3 = RegexSetting()


Extending type checker and setting classes
''''''''''''''''''''''''''''''''''''''''''

.. warning:: Checkers are deprecated, use validators instead.

In the previous example, we combined our own type checker to our own setting
class. But we can extend it furthermore by adding parameters to the type
checker, or by inheriting from previous type checkers.

.. code:: python

    from datetime import datetime
    import re
    import appsettings


    class DateTimeTupleTypeChecker(appsettings.TupleTypeChecker):
        def __init__(
                self, min_length=None, max_length=None, empty=True,
                maximum=None):
            # here we restrict the parent TupleTypeChecker parameters
            # by hard-coding item_type=datetime
            super(DateTimeTupleTypeChecker, self).__init__(
                item_type=datetime, min_length=min_length,
                max_length=max_length, empty=empty)
            # and here we add our custom parameters
            self.maximum = maximum

        # now we are able to extend the check
        def __call__(self, name, value):
            super(DateTimeTupleTypeChecker, self).__call__(name, value)
            if isinstance(self.maximum, datetime):
                for i, item in enumerate(value):
                    if item > self.maximum:
                        raise ValueError(
                            'item %d (%s) in setting %s '
                            'is above maximum %s' % (
                                i, item, name, self.maximum))


    class DateTimeTupleSetting(appsettings.Setting):
        def __init__(
                self, name='', default=lambda: tuple(), prefix='',
                required=False, call_default=True, transform_default=False,
                **checker_kwargs):
            # we simply hook our type checker into our setting class
            super(DateTimeTupleSetting, self).__init__(
                name=name, default=default, required=required, prefix=prefix,
                call_default=call_default, transform_default=transform_default,
                checker=DateTimeTupleTypeChecker(**checker_kwargs))


    setting = DateTimeTupleSetting(
        name='dates_to_remember', default=lambda: (datetime.now(), ),
        min_length=1, maximum=datetime(year=2030, month=1, day=1)


    # and the related setting would be
    DATES_TO_REMEMBER = (
        datetime(year=2017, month=11, day=30),  # the day I wrote this line
    )


Transforming setting values
'''''''''''''''''''''''''''

You may want your setting to be less strict about types, but make sure it
always return the same type of object. This is what the transform method is
here for:

.. code:: python

    import re
    import appsettings


    # our type checker
    class RegexTypeChecker(appsettings.TypeChecker):
        def __init__(self, **kwargs):
            re_type = type(re.compile(r'^$'))
            # allow both str and re_type types
            super(BooleanTypeChecker, self).__init__(base_type=(str, re_type))


    # our setting class
    class RegexSetting(appsettings.Setting):
        def __init__(
                self, name='', default=re.compile(r'^$'), required=False,
                prefix='', call_default=True, transform_default=False,
                **checker_kwargs):
            super(RegexSetting, self).__init__(
                name=name, default=default, required=required, prefix=prefix,
                call_default=call_default, transform_default=transform_default,
                checker=RegexTypeChecker(**checker_kwargs))

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
