# Contributing code

Install the code with development and docs dependencies:

```bash
uv sync --all-groups
```

## Format code and sort imports

```bash
black .
isort .
```

## lint code

```bash
ruff check .
```

## Run tests

```bash
pytest
```

There are 2 options for putting tests. 
1. Tests in the tests folder. 
3. Simple doctests under examples of function docstrings e.g.
    ```
    ...docstring text...
    
    Examples
    --------
    >>> prints_hello_world()
    hello world

    ...docstring text continued...
    ```
    Note: if you want to include a docstring example without running as a test then append ` # doctest: +SKIP ` to the line of code. 

## Sync notebooks with jupytext

For easier diffs, you can use jupytext to sync notebooks in the `docs/tutorial` directory with the percent format.

```bash
jupytext --sync docs/tutorial/*.ipynb
```

This is configured in the [`.jupytext`](docs/tutorial/.jupytext) file in that directory.
