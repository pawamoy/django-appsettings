=========
Changelog
=========

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
