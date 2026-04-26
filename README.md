# MGni.py

MGni.py (pronounced MAG-nee-pie) is a Python wrapper for the [MGnify API](https://www.ebi.ac.uk/metagenomics/api/docs/). It provides a high-level, Pythonic interface to query metagenomics data and metadata from the MGnify database.

The Python client libraries were auto-generated using [openapi-python-client](https://github.com/openapi-generators/openapi-python-client) and provide data models and methods for API resources using `httpx` and `attrs`.

## Features

- **Simple, Pythonic API** — Query studies, samples, analyses, and genomes with intuitive syntax
- **Async-ready** — Built on `httpx` with async/await support for efficient I/O
- **Data export** — Multiple output formats including pandas DataFrames and AnnData objects
- **Caching** — Automatic caching to reduce redundant API calls
- **Filtering & search** — Powerful filtering with support for custom parameters
- **Biome hierarchy** — Navigate the GOLD ecosystem classification system

## Installation

### From PyPI (stable)

```bash
pip install mgnipy
```

### From TestPyPI (development)

```bash
pip install mgnipy \
--index-url https://test.pypi.org/simple/ \
--extra-index-url https://pypi.org/simple
```

### Development installation

```bash
git clone https://github.com/EBI-Metagenomics/mgnipy.git
cd mgnipy
uv sync --all-groups  # or: pip install -e ".[dev,docs]"
```

## Quick Start

### Initialize and explore

```python
from mgnipy import MGnipy

# Create the main client
mg = MGnipy()

# See available endpoints
print(mg.list_resources())
```

### Query studies with filtering

```python
# Search for studies by biome and keyword
studies = mg.studies(
    biomes_lineage="root:Host-associated:Plants:Rhizosphere",
    search="tomato"
)

# Preview requests before fetching
print(studies.explain())
# or preview first page as df
df = studies.preview()

# Get all results (async here but also sync option)
import asyncio
asyncio.run(studies.aget())
```

### Multiple output formats

```python
pd_df = studies.to_df()

# As polars DataFrame
pl_df = studies.to_polars()

# as json
results_json = studies.to_json()
```

## Configuration

```python
from mgnipy import MGnipy

mg = MGnipy(
    headers={"User-Agent": "my-app/1.0"},
    # Optional: authentication
    auth=("username", "password")
)
```

## Available Endpoints

- Studies — Browse and filter metagenomic studies
- Samples — Query sample metadata
- Runs — Access sequencing run information
- Assemblies — Genome assembly data
- Genomes — Genome-level information
- Analyses — Analysis results and annotations
- And more... — Use `mg.list_resources()` to see all available endpoints

## Documentation

- [MGnify API Docs](https://www.ebi.ac.uk/metagenomics/api/docs/)
- [openapi-python-client](https://github.com/openapi-generators/openapi-python-client)
- [package docs]()

## Development

### Code quality

```bash
# Format and sort imports
black mgnipy
isort mgnipy

# Lint
ruff check mgnipy

# Run tests
pytest mgnipy tests
```

### Contributing

see [Contributing.md](Contributing.md)

## License

TODO

## Citation

TODO
