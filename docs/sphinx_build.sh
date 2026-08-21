export SPHINX_APIDOC_OPTIONS="members,undoc-members,inherited-members,show-inheritance"

jupytext notebooks/**/*.ipynb --sync

cp ../Contributing.md Contributing.md

# Generating the rst files for the API reference. This is needed for autodoc during sphinx-build to work.
# Note: does not use conf.py
sphinx-apidoc --force \
    --separate --module-first --remove-old -t _templates \
    -d 1 -o reference ../mgnipy

# build the docs
sphinx-build -vvv --show-traceback --keep-going --fresh-env --builder html ./ ./_build/
