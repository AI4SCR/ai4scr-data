# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath(".."))


# -- Project information -----------------------------------------------------

project = "blueprint"
copyright = "IBM Corp. 2022"
author = "IBM blueprint team"

# -- Generate API (auto) documentation ------------------------------------------------


def run_apidoc(app):
    """Generage API documentation"""
    import better_apidoc

    better_apidoc.APP = app
    better_apidoc.main(
        [
            "better-apidoc",
            "-t",
            os.path.join(".", "_templates"),
            "--force",
            "--no-toc",
            "--separate",
            "-o",
            os.path.join(".", f"{project}_api"),
            os.path.join("..", f"{project}"),
        ]
    )


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
    "sphinx_autodoc_typehints",
    "sphinx_rtd_theme",
    "myst_parser",
    "sphinx.ext.intersphinx"  # external documentations
]

# Add mappings to external docs used for cross references

intersphinx_mapping = dict(
    urllib3=('https://urllib3.readthedocs.org/en/latest', None),
    anndata=('https://anndata.readthedocs.io/en/stable/', None),
    bbknn=('https://bbknn.readthedocs.io/en/latest/', None),
    cycler=('https://matplotlib.org/cycler/', None),
    h5py=('https://docs.h5py.org/en/stable/', None),
    ipython=('https://ipython.readthedocs.io/en/stable/', None),
    leidenalg=('https://leidenalg.readthedocs.io/en/latest/', None),
    louvain=('https://louvain-igraph.readthedocs.io/en/latest/', None),
    matplotlib=('https://matplotlib.org/', None),
    networkx=('https://networkx.github.io/documentation/networkx-1.10/', None),
    numpy=('https://docs.scipy.org/doc/numpy/', None),
    pandas=('https://pandas.pydata.org/pandas-docs/stable/', None),
    pytest=('https://docs.pytest.org/en/latest/', None),
    python=('https://docs.python.org/3', None),
    scipy=('https://docs.scipy.org/doc/scipy/reference/', None),
    seaborn=('https://seaborn.pydata.org/', None),
    sklearn=('https://scikit-learn.org/stable/', None)
)

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "links.rst"]

# -- Epilog variable ---------------------------------------------------------
# https://stackoverflow.com/questions/61688403/can-i-keep-all-my-external-links-in-a-separate-file-with-sphinx
rst_epilog =""
# Read link all targets from file
with open('links.rst') as f:
     rst_epilog += f.read()

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]


# -- Extension configuration -------------------------------------------------
add_module_names = False


napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True

coverage_ignore_modules = []
coverage_ignore_functions = []
coverage_ignore_classes = []

coverage_show_missing_items = True

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True


def setup(app):
    app.connect("builder-inited", run_apidoc)
