# Docs creation

The tutorials/demos act as tests - if the notebooks/py don't execute then the docs build will fail. 

## Steps

1. install project and doc dependencies in a venv
    ```bash
    # uncomment for venv 
    #uv venv
    #source .venv/bin/activate

    uv sync --all-groups
    ```

2. dev the documentation in module docstrings or as markdown or jupyter notebook in docs folder

3. update the [.mgnipy/docs/index.md](index.md) file if needed (e.g. adding tutorial)

4. `cd` into *docs* dir and run the helper [`sphinx_build.sh`](sphinx_build.sh) script OR run the contained steps manually:

    a) if jupyter notebook sync jupytext e.g.
    ```bash
    jupytext --sync <path-to-notebook-or-notebooks>/*.ipynb
    ```
    
    b) build the package reference files and run sphinx to create a local html version. e.g.
    ```bash
    # pwd: docs
    # apidoc
    sphinx-apidoc --force --implicit-namespaces --module-first -o reference ../mgnipy
    # build docs
    sphinx-build -n -W --keep-going -b html ./ ./_build/
    ```

## Readthedocs
The documentation can be hosted on readthedocs. The [yaml](../.readthedocs.yaml) is in the root dir of the project.


## Tips:

### checking out the build locally
Based on the above code block, the docs build is in a *_build/* folder. In that folder you will find an index.html file. Open it in your preferred browser to explore


### Sync notebooks with jupytext
For easier diffs, you can use jupytext to sync notebooks in the `docs/tutorial` directory with the percent format.
```bash
jupytext --sync docs/tutorial/*.ipynb
```
This is configured in the [`.jupytext`](docs/tutorial/.jupytext) file in that directory.
