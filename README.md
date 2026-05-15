# MGni.py

MGni.py (pronounced MAG-nee-pie) is a Python wrapper for the [MGnify API](https://www.ebi.ac.uk/metagenomics/api/docs/). It provides a high-level, Pythonic interface to query metagenomics data and metadata from the MGnify database.

## Features

- **Simple, Pythonic API** — Query MGnify studies, samples, analyses, etc. using an intuitive syntax
- **Sync and Async support** — Built on `httpx` with async/await support
- **Data export** — Multiple output formats including pandas and polars DataFrames
- **Caching** — Option for disk caching to reduce redundant API calls and allow resuming

## Available API Endpoints

- **Studies**: MGnify studies (collections of samples, runs, assemblies and analyses derived from ENA studies/projects).
- **Samples**: MGnify samples (based on ENA/BioSamples; individual biological samples).
- **Runs**: Sequencing runs (ENA run accessions; individual sequencing runs of a sample).
- **Assemblies**: Metagenome assemblies (equivalent to ENA assemblies for one or more runs).
- **Analyses**: Pipeline analyses (results of running MGnify pipelines on runs or assemblies; includes taxonomic and functional annotations).
- **Publications**: Publications that describe or analyse MGnify Studies/datasets.
- **Genomes**: Annotated draft genomes (isolates or MAGs) arranged in biome-specific catalogues.
- **Biomes**: List all biomes in the MGnify database.

#### Note on private data:

- To access your private data in any of these API endpoints you just need your MGnify user and password to obtain a valid sliding auth token via the [MGnify Authentication endpoints](https://www.ebi.ac.uk/metagenomics/api/v2/#/Authentication/token_obtain_sliding).
- `mgnipy.MGnipyConfig` takes care of getting and caching the auth token so that you can easily access your private data using MGni.py :)

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

# Create the main client, with default configuration
mg = MGnipy()

# See available endpoints
mg.list_resources()
```

### Query resources with filtering

```python
# Search for studies keyword
studies = mg.studies(
    search="disease"
)

# Can preview requests before fetching
studies.explain()

# get page by page via .get(), getting 3 pages
for _ in range(3)
    studies.get()

# or via .page(), getting another 3 pages
for i in range(4,7):
    studies.page(i)

# OR potentially all at once in large batches (also async option .abulk_fetch())
studies.bulk_fetch()
```

### Multiple output formats

```python
pd_df = studies.to_df()

# As polars DataFrame
pl_df = studies.to_polars()

# as json
results_json = studies.to_json()
```

## Additional Documentation

- [MGnify API Docs](https://www.ebi.ac.uk/metagenomics/api/v2)
- [openapi-python-client](https://github.com/openapi-generators/openapi-python-client)
- [package docs](https://mgnipy.mgnify.org/)

## Development

see [Contributing.md](Contributing.md)

## License

TODO

## Citation

TODO
