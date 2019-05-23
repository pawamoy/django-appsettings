=========
Changelog
=========

0.5.1 (2019-05-23)
==================

- Fix default values for empty arguments.

0.5.0 (2018-12-03)
==================

- Deprecate setting checkers in favor of validators, similarly to Django form fields.


0.4.0 (2018-07-25)
==================

- Add ``NestedSetting`` for easy management of nested settings.

0.3.0 (2017-11-30)
==================

Going from alpha to beta status. Logic has been reworked.

- An instance of a subclass of ``AppSettings`` will now dynamically get
  settings values from project settings, and cache them. This allows to use
  the instance the same way in code and tests, without performance loss. See
  issue `#16`_.
- Cache is invalidated when Django sends a ``setting_changed`` signal (i.e.
  when using ``TestCase`` or ``override_settings``). See issue `#16`_.
- Setting main class now accepts callable as default value, and two new
  parameters to keep control on its behavior: ``call_default``, which tells
  if the default value should be called (if callable) or not, and
  ``transform_default``, which tells if the default value should be transformed
  as well by the ``transform`` method. See issue `#17`_.
- Settings type checkers now have custom parameters like ``max_length``,
  ``empty`` or ``key_type``, that can be passed directly through the settings
  classes as keyword arguments. Check the documentation for more information.
- Settings classes have been rewritten more explicitly, using class inheritance
  instead of hard-to-debug generators. Composed types like float lists or
  boolean sets have been removed in favor of more flexible list, set and tuple
  types which now accept an optional ``item_type`` parameter.
- ``ImportedObjectSetting`` has been renamed ``ObjectSetting``, and now
  supports object paths down to arbitrary level of nesting. Before, it only
  supported object paths down to classes or functions, now you can for example
  give it the path to a constant in a class within a class, itself contained
  in a module within a package. It will work as long a the deepest module is
  importable through ``importlib.import_module`` and each object down to the
  last is obtainable through ``getattr`` method.

Many thanks to `ziima`_ for having shared good ideas and thoughts!

.. _#16: https://github.com/Genida/django-appsettings/issues/16
.. _#17: https://github.com/Genida/django-appsettings/issues/17
.. _ziima: https://github.com/ziima

0.2.5 (2017-06-02)
==================

- Add six dependency (now required).
- Rename ``Int`` settings to ``Integer``, and ``Bool`` ones to ``Boolean``.
- Remove metaclass generated getters and checkers.

0.2.4 (2017-05-02)
==================

- Settings are not checked when they default to the provided default value.
- Settings classes received better default values corresponding to their types.

0.2.3 (2017-05-02)
==================

- Add ``full_name`` property to ``Setting`` class.
- Add ``required`` parameter to ``Setting`` class (default ``False``).

0.2.2 (2017-04-17)
==================

- Import settings classes in main module to simplify imports.

0.2.1 (2017-04-17)
==================

- Add ``PositiveInt`` and ``PositiveFloat`` settings.
- Add support for Django 1.11.
- Implement basic settings classes.

0.2.0 (2017-04-17)
==================

- Implement basic Setting class.
- Pin dependencies.
- Change distribution name to ``app-settings``.

0.1.0 (2017-03-23)
==================

- Alpha release on PyPI.
