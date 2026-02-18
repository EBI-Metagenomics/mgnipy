# Configuration file for the Sphinx documentation builder.
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
from importlib import metadata
# compatibility with plotly6
os.environ["PLOTLY_RENDERER"] = "notebook"  
# -- Project information -----------------------------------------------------

project = "mgnipy"
copyright = "2025, First Last"
author = "First Last"
PACKAGE_VERSION = metadata.version("mgnipy")
version = PACKAGE_VERSION
release = PACKAGE_VERSION


# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",  # Core extension for generating documentation from docstrings
    "sphinx.ext.viewcode",  # Include links to the source code in the documentation
    "sphinx.ext.napoleon",  # Support for Google and NumPy style docstrings
    "sphinx.ext.intersphinx",  # allows linking to other projects' documentation in API
    "sphinx_new_tab_link",  # each link opens in a new tab
    "myst_nb",  # Markdown and Jupyter Notebook support
    "sphinx_copybutton",  # add copy button to code blocks
    "sphinx.ext.autosummary"
]

exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "jupyter_execute",
    "conf.py",
]

templates_path = ["_templates"]

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
    "use_edit_page_button": True,
    "use_repository_button": True,
    "use_download_button": True,
    "launch_buttons": {
        "colab_url": "https://colab.research.google.com"
        #     "binderhub_url": "https://mybinder.org",
        #     "notebook_interface": "jupyterlab",
    },
    "navigation_with_keys": False,
}
html_js_files = [
    "https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.4/require.min.js"
] #plotly support


# -- Extensions configurations ---------------------------------------------------

## autosummary options
autosummary_generate = True

## autodoc options

autodoc_default_options = {
    'members': True,
    'undoc-members': False,
    'private-members': False,  # Exclude _private attributes
    'special-members': False,  # Exclude __special__ methods
    'inherited-members': True,  # Exclude inherited members
    'show-inheritance': True,  # Show class inheritance diagram
    'member-order': 'bysource',  # Order members by source code order
}

autodoc_typehints = 'description'

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

## Intersphinx options
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pandas": ("https://pandas.pydata.org/pandas-docs/stable/", None),
    "anndata": ("https://anndata.readthedocs.io/en/stable/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
}


# -- Setup for sphinx-apidoc -------------------------------------------------

# Read the Docs doesn't support running arbitrary commands like tox.
# sphinx-apidoc needs to be called manually if Sphinx is running there.
# https://github.com/readthedocs/readthedocs.org/issues/1139

if os.environ.get("READTHEDOCS") == "True":
    from pathlib import Path

    PROJECT_ROOT = Path(__file__).parent.parent
    print(f"PROJECT_ROOT: {PROJECT_ROOT}")
    PACKAGE_ROOT = PROJECT_ROOT / "mgnipy"
    CLIENT_ROOT_V1 = PROJECT_ROOT / "openapi" / "mgni-py-v1" / "mgni_py_v1"
    CLIENT_ROOT_V2 = PROJECT_ROOT / "openapi" / "mgni-py-v2" / "mgni_py_v2"

    def run_apidoc(_):
        from sphinx.ext import apidoc

        apidoc.main(
            [
                "--force",
                "--implicit-namespaces",
                "--module-first",
                "--separate",
                "-o",
                str(PROJECT_ROOT / "docs" / "reference" / "mgnipy"),
                str(PACKAGE_ROOT),
                str(PACKAGE_ROOT / "*.c"),
                str(PACKAGE_ROOT / "*.so"),
            ]
        )

        apidoc.main([
            "--force",
            "--implicit-namespaces",
            "--module-first",
            "--separate",
            "-o", str(PROJECT_ROOT / "docs" / "reference" / "mgni-py-v1"),
            str(CLIENT_ROOT_V1),
            str(CLIENT_ROOT_V1 / "*.c"),
            str(CLIENT_ROOT_V1 / "*.so"),
        ])

        apidoc.main([
            "--force",
            "--implicit-namespaces",
            "--module-first",
            "--separate",
            "-o", str(PROJECT_ROOT / "docs" / "reference" / "mgni-py-v2"),
            str(CLIENT_ROOT_V2),
            str(CLIENT_ROOT_V2 / "*.c"),
            str(CLIENT_ROOT_V2 / "*.so"),
        ])

    def setup(app):
        app.connect("builder-inited", run_apidoc)
