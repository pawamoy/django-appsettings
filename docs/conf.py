# -*- coding: utf-8 -*-

"""Sphinx configuration file."""

from __future__ import unicode_literals

import os

import sys
import django
from django.conf import settings

sys.path.insert(0, os.path.join(os.path.abspath('..'), 'src'))
settings.configure(
    INSTALLED_APPS=[
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sites',
    ],
    SITE_ID=1
)
django.setup()


extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.coverage',
    'sphinx.ext.doctest',
    'sphinx.ext.extlinks',
    'sphinx.ext.ifconfig',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
]

autodoc_default_flags = [
    'members',
    'special-members',
    'show-inheritance'
]

if os.getenv('SPELLCHECK'):
    extensions += 'sphinxcontrib.spelling',
    spelling_show_suggestions = True
    spelling_lang = 'en_US'

source_suffix = '.rst'
master_doc = 'index'
project = u'Django AppSettings'
year = '2017'
author = u'Timothee Mazzucotelli'
copyright = '{0}, {1}'.format(year, author)
version = release = u'0.7.2'

pygments_style = 'trac'
templates_path = ['.']
extlinks = {
    'issue': ('https://github.com/pawamoy/django-appsettings/issues/%s', '#'),
    'pr': ('https://github.com/pawamoy/django-appsettings/pull/%s', 'PR #'),
}

html_theme = 'sphinx_rtd_theme'

html_last_updated_fmt = '%b %d, %Y'
html_split_index = False
html_sidebars = {
   '**': ['searchbox.html', 'globaltoc.html', 'sourcelink.html'],
}
html_short_title = '%s-%s' % (project, version)

html_context = {
    'extra_css_files': [
        '_static/extra.css',
    ],
}

html_static_path = [
    "extra.css",
]

napoleon_use_ivar = True
napoleon_use_rtype = False
napoleon_use_param = False
suppress_warnings = ["image.nonlocal_uri"]
