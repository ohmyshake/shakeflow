# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

import datetime

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

import shakeflow

sys.path.insert(0, os.path.abspath(".."))


# -- Project information -----------------------------------------------------

project = "SHAKEFLOW"
year = datetime.date.today().year
copyright = f"2023-{year}, Fu Yin"
author = "Fu Yin"

# The full version, including alpha/beta/rc tags
release = shakeflow.__version__


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.githubpages",
    "autoapi.extension",
    "jupyter_sphinx",
    "sphinx.ext.autosectionlabel",
    "sphinx_copybutton",
]

# Autosummary pages will be generated by sphinx-autogen instead of sphinx-build
autoapi_dirs = ["../shakeflow"]
autodoc_typehints = "description"
autoapi_python_class_content = "init"
autoapi_member_order = "groupwise"
autoapi_keep_files = True
autosectionlabel_maxdepth = 4

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "pydata_sphinx_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_baseurl = "yinfu.info"
