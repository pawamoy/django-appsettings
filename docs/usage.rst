Usage
=====

``Setting`` class
-----------------

A ``Setting`` is described by a ``name``, a ``default`` value, and a ``prefix``.
The prefix and the name form the full name of the setting. This full name is used
to declare it in the project's settings. Prefix is generally the name of the
application or project, but it can be left empty. Also name will by default
be the variable name in uppercase.

.. code:: python

    # same as verbosity_level = Setting(prefix='verbose_app_')
    verbosity_level = Setting(name='verbosity_level', prefix='verbose_app_')

    # in project's settings (must be uppercase)
    VERBOSE_APP_VERBOSITY_LEVEL = 'extremely_verbose'

The default value is used if the setting was not declared. The setting
can also be declared ``required``, and it that case it makes no sense to give
it a default value (but it's tolerated). By default, settings are all optional
(``required=False``). A setting that is required and not declared will raise
an ``AttributeError``.

A setting disposes of four methods:

- ``get_raw``: get the setting given in project's settings;
- ``get``: return the result of ``transform``;
- ``check``: check the setting (not transformed).
- ``transform``: get the raw setting and apply transformation.

When sub-classing ``Setting`` to define a custom setting,
override ``check`` and ``transform`` methods like this:

.. code:: python

    class RegexSetting(Setting):
        def check():
            value = self.get_raw()
            if value != self.default:  # always allow default to pass
                re_type = type(re.compile(r'^$'))
                if not isinstance(value, (re_type, str)):
                    raise ValueError('%s must be a a string or a compiled regex '
                                     '(use re.compile)' % self.full_name)

        def transform(self):
            value = self.get_raw()
            if isinstance(value, str):
                value = re.compile(value)
            return value


``AppSettings`` class
---------------------

The ``AppSettings`` class is just a container for settings.
Additionally, it provides a ``check`` method to check every
declared settings. You can also pass a setting prefix for every setting in
a meta class. Instantiating an ``AppSettings`` will replace every settings
by their transformed value.

Here is an example of settings declaration in ``apps.py``:

.. code:: python

    from django.apps import AppConfig
    import appsettings as aps

    class MyAppConfig(AppConfig):
        name = 'my_app'
        verbose_name = 'My Application'

        def ready(self):
            # check every settings at startup, raise one exception
            # with all errors in its message
            AppSettings.check()


    class AppSettings(aps.AppSettings):
        always_use_ice_cream = aps.BooleanSetting(default=True)
        attr_name = aps.StringSetting(name='SETTING_NAME')
        regex = RegexSetting()  # declared before

        # if you need to import a python object (module/class/method)
        imported_object = aps.ImportedObjectSetting(default='app.default.object')

        class Meta:
            setting_prefix = 'ASH_'  # settings must be prefixed with ASH_

In the rest of your code
------------------------

.. code:: python

    from .apps import AppSettings

    # instantiation will load and transform every settings
    app_settings = AppSettings()
    app_settings.attr_name == 'something'

    # or, and in order to work with tests overriding settings
    AppSettings.always_use_ice_cream.get()  # to get ASH_ALWAYS_USE_ICE_CREAM setting dynamically
    my_python_object = AppSettings.imported_object.get()

Running ``AppSettings.check()`` will raise an ``ImproperlyConfigured``
exception if at least one of the settings' ``check`` methods raised an
exception. It will also print all caught exceptions.
