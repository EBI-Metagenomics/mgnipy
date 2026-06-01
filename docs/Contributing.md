# Contributing code

Install the code with development and docs dependencies:

```bash
uv sync --all-groups
```

## Prior to PR: 
### Format code and sort imports

```bash
black mgnipy
isort mgnipy
```

### lint code

```bash
ruff check mgnipy
```

### Run tests

```bash
pytest mgnipy tests
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

### Update docs 
See the [docs/README.md](docs/README.md)