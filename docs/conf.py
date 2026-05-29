# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "FLARE: The Workflow Orchestration Tool"
copyright = "MIT"
author = "Cameron Harris"
release = "0.1"

source_suffix = ".md"

# The master toctree document.
master_doc = "index"


extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.mathjax",
    "sphinx_togglebutton",
    "sphinxcontrib.autodoc_pydantic",
]

# Show json schema as a toggle
autodoc_pydantic_model_show_json = True
autodoc_pydantic_settings_show_json = False


html_theme = "sphinx_book_theme"
html_logo = "source/_static/flare-logo-1280-640.png"
html_static_path = ["source/_static"]

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["myst_parser"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
