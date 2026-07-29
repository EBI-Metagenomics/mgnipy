# Configuration file for the Sphinx documentation builder.
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import logging

logging.basicConfig(level=logging.WARNING, force=True)
import os
from importlib import metadata

# compatibility with plotly6
os.environ["PLOTLY_RENDERER"] = "notebook"

# -- Project information -----------------------------------------------------

project = "mgnipy"
copyright = "2026, MGnify"
author = "MGnify"
PACKAGE_VERSION = metadata.version("mgnipy")
version = PACKAGE_VERSION
release = PACKAGE_VERSION


# -- General configuration ---------------------------------------------------
warningiserror = False

extensions = [
    "sphinx.ext.autodoc",  # Core extension for generating documentation from docstrings
    "sphinx.ext.viewcode",  # Include links to the source code in the documentation
    "sphinx.ext.napoleon",  # Support for Google and NumPy style docstrings
    "sphinx.ext.intersphinx",  # allows linking to other projects' documentation in API
    "sphinx_new_tab_link",  # each link opens in a new tab
    "myst_nb",  # Markdown and Jupyter Notebook support
    "sphinx_copybutton",  # add copy button to code blocks
    "sphinx.ext.autosummary",
    "sphinx_thebe",
    "sphinx_togglebutton",
]

exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "jupyter_execute",
    "conf.py",
]

# -- Theme configurations ---------------------------------------------------

templates_path = ["_templates"]
html_static_path = ["_static"]
html_css_files = ["custom.css"]
# https://sphinx-book-theme.readthedocs.io/en/stable/index.html
html_theme = "sphinx_book_theme"
html_logo = "assets/mgnipy.svg"
html_favicon = "assets/mgnipy.svg"
html_theme_options = {
    "github_url": "https://github.com/EBI-Metagenomics/mgnipy",
    "repository_url": "https://github.com/EBI-Metagenomics/mgnipy",
    "repository_branch": "main",
    "home_page_in_toc": True,
    "path_to_docs": "docs",
    "show_navbar_depth": 1,
    "collapse_navbar": True,
    "show_toc_level": 3,
    "use_edit_page_button": True,
    "use_repository_button": True,
    "use_download_button": True,
    "launch_buttons": {
        "colab_url": "https://colab.research.google.com",
        "binderhub_url": "https://mybinder.org",
        "notebook_interface": "jupyterlab",
        "thebe": True,
    },
    "navigation_with_keys": True,
    "use_sidenotes": True,
}
html_js_files = [
    "https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.4/require.min.js"
]  # plotly support

# -- Extensions configurations ---------------------------------------------------

## thebe
thebe_config = {
    "selector": "div.highlight",
    # "always_load": True
}

## autosummary options
autosummary_generate = True

## autodoc options
autodoc_typehints = "description"
add_module_names = False

## sphinx_new_tab_link
new_tab_link_show_external_link_icon = True

## myst_nb
# https://myst-nb.readthedocs.io/en/latest/configuration.html
myst_enable_extensions = ["dollarmath", "amsmath"]
# Execution
#  https://myst-nb.readthedocs.io/en/latest/computation/execute.html
nb_execution_mode = "auto"
nb_execution_timeout = -1  # -1 means no timeout
nb_execution_raise_on_error = True  # fail the build if a notebook cell raises an error
# Rendering
nb_merge_streams = True
nb_scroll_outputs = True
nb_output_stderr = "remove"

## Intersphinx options
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pandas": ("https://pandas.pydata.org/pandas-docs/stable/", None),
    "anndata": ("https://anndata.readthedocs.io/en/stable/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
}

## togglebutton
togglebutton_hint = "Click to open. More Info:"
togglebutton_hint_hide = "Click to Hide. More Info:"
