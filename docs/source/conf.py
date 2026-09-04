# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

sys.path.insert(0, os.path.abspath('../src'))

project = 'RobeRT-py'
copyright = '2026, Juan Sobalvarro'
author = 'Juan Sobalvarro'
release = '1.4.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
]

intersphinx_mapping = {'python': ('https://docs.python.org/3', None)}

autodoc_typehints = 'description'

# nitpick_ignore = [
#     ('py:class', 'robert.ServerResponse'),
#     ('py:class', 'robert.JointTarget'),
#     ('py:class', 'robert.RobTarget'),
#     ('py:class', 'robert.Zone'),
# ]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']


locale_dirs = ['locale/']   # path is example but recommended.
gettext_compact = False
