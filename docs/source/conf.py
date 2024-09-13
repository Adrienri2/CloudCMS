import os
import sys

# Añade el directorio del proyecto a sys.path
sys.path.insert(0, os.path.abspath('../..'))

# Configura Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'cloudcms.settings'
import django
django.setup()

# -- Project information -----------------------------------------------------
project = 'CloudCMS'
copyright = '2024, Adrián'
author = 'Adrián'
release = '1.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
exclude_patterns = []

language = 'es'

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']