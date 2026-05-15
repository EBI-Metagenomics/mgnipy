export MGNIPY_AUTHENTICATION_OFF=1
export SPHINX_APIDOC_OPTIONS="members,undoc-members,inherited-members,show-inheritance"

jupytext dev/*.ipynb --sync
jupytext tutorials/getting-started/*.ipynb --sync

#jupytext tutorials/demos/get_all_analyses_for_study.ipynb --sync

# Generating the rst files for the API reference. This is needed for autodoc during sphinx-build to work.
# Note: does not use conf.py
sphinx-apidoc --force \
    --separate --module-first --remove-old -t _templates \
    -d 1 -o reference ../mgnipy

# build the docs
sphinx-build --keep-going --fresh-env --builder html ./ ./_build/
