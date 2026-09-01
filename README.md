# MGni.py

MGni.py (🔉[IPA:'mæɡni-paɪ'](https://ipa-reader.com/?text=m%C3%A6%C9%A1ni-pa%C9%AA)) is a lightweight python client and toolkit for the [MGnify API v2](https://www.ebi.ac.uk/metagenomics/api/v2/).

<p align="center">
    <a href="https://pypi.org/project/mgnipy/">
        <img src="https://img.shields.io/pypi/v/mgnipy?label=PyPI" alt="PyPI">
    </a>
    <a href="https://pypi.org/project/mgnipy/">
    <img src="https://github.com/EBI-Metagenomics/mgnipy/actions/workflows/cicd.yml/badge.svg" alt="cicd.yml">
    </a>
    <a href="https://mgnipy.mgnify.org/">
        <img src="https://github.com/EBI-Metagenomics/mgnipy/actions/workflows/gh-pages.yml/badge.svg" alt="GitHub Pages docs">
    </a>
    <a href="https://www.gnu.org/licenses/gpl-3.0.en.html">
        <img src="https://img.shields.io/badge/License-GPLv3-blue.svg" alt="License: GPL v3">
    <br>
    <img src="https://img.shields.io/badge/python-3.11%20--%203.13-blue" alt="Python 3.11 to 3.13">
    <img src="https://img.shields.io/github/issues/EBI-Metagenomics/mgnipy" alt="GitHub issues">
    <img src="https://img.shields.io/github/license/EBI-Metagenomics/mgnipy" alt="GitHub license">
    <img src="https://img.shields.io/github/last-commit/EBI-Metagenomics/mgnipy" alt="GitHub last commit">
    <img src="https://img.shields.io/github/stars/EBI-Metagenomics/mgnipy" alt="GitHub stars">
</p>

![mgnipy schematic](docs/assets/mgnipy_figure.gif)

## Contents

- [Features](#features)
- [Available API Endpoints](#available-api-endpoints)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Additional Documentation](#additional-documentation)
- [Development](#development)
- [License](#license)
- [Citation](#citation)

## Features

- **FAIR**: More findable MGnify analyses and metadata, returned in familiar metagenomics data formats (e.g., GFF, [Darwin Core](https://dwc.tdwg.org/), Dataframes [[pandas](https://pandas.pydata.org/docs/), [polars](https://docs.pola.rs/), [anndata](https://anndata.scverse.org/en/stable/)])
- **Simplifies API interactions:** Let MGni.Py handle the complexity of building, executing, and parsing API calls so you can focus on the data!
- **Fast:** MGni.Py uses caching to speed up API expolation, as well as supports both sync and async API calls

## [Supported MGnify API resources](https://docs.mgnify.org/src/docs/portal.html)

- **[Studies](https://docs.mgnify.org/src/docs/portal.html#studies)**
- **[Samples](https://docs.mgnify.org/src/docs/portal.html#samples)**
- **[Publications](https://docs.mgnify.org/src/docs/portal.html#publications)**
- **[Genomes](https://docs.mgnify.org/src/docs/portal.html#genomes)**
- **[Catalogues](https://www.ebi.ac.uk/metagenomics/api/v2/#/Genomes/list_genome_catalogues)**
- **[Runs](https://www.ebi.ac.uk/metagenomics/api/v2/#/Runs)**
- **[Assemblies](https://www.ebi.ac.uk/metagenomics/api/v2/#/Assemblies)**
- **[Analyses](https://www.ebi.ac.uk/metagenomics/api/v2/#/Analyses)**
- **[Biomes](https://www.ebi.ac.uk/metagenomics/api/v2/#/Miscellaneous/list_mgnify_biomes)** ([GOLD ecosystem classifications](https://bioportal.bioontology.org/ontologies/GOLDTERMS))

> [!NOTE] 
> 
> **Accessing your private data**
> - To access your private data in any of these API endpoints you just need your MGnify user and password to obtain a valid sliding auth token via the [MGnify Authentication endpoints](https://www.ebi.ac.uk/metagenomics/api/v2/#/Authentication/token_obtain_sliding).
> - for example you can put your login credentials in a `.env` file in your working directory (see [.env.example](https://github.com/EBI-Metagenomics/mgnipy/blob/a9dfdfbb3f669569473e11c7a7c9cf460e6c7d11/.env.example)) and 
> - `mgnipy.MGnipyConfig` takes care of getting and caching the auth token so that you can easily access your private data using MGni.py 🎉

## Installation

### From PyPI

```bash
pip install mgnipy
```


### Development installation

```bash
git clone https://github.com/EBI-Metagenomics/mgnipy.git
cd mgnipy
uv sync --all-groups  # or: pip install -e ".[dev,docs]"
```

## Quick Start

### 🚀 1. Initialize `mgnipy.MGnipy`

```python
from mgnipy import MGnipy

# Create the main client, with default configuration
mg = MGnipy()

# See available endpoints
mg.list_resources()
```

### 🔎 2. Search resources with a `mgnipy.MGnifier`

#### Building the query set
```python
# Search for studies keyword
studies = mg.studies(
    search="disease"
)

# Can preview requests before fetching
studies.explain()
```

#### Executing the queries
```python
# client context manager
with MG: 

    # get page by page via .get()
    studies.get()
    # or via .page(), getting a specific pg num 
    studies.page(2)
    # OR potentially all at once in large batches (also async option .aget_all())
    studies.get_all()

    # then can enrich list with detailed metadata
    studies.enrich_details()
```

#### Viewing the search results
```python
# the mgnify list (without details)
study_list = studies.search_results
# detailed metadata, e.g. with enriched details
detailed_study_list = studies.metadata

# e.g. as dataframes
pl_metadata = detailed_study_metadata.to_polars()
pd_metadata = detailed_study_metadata.to_pandas()

# e.g. as json
json_metadata = detailed_study_metadata.to_json()
```

### 🗃️ 3. Explore a `mgnipy.MGazine` of datasets
```python
# accessing the mgazine of datasets
mgazine = studies.datasets

# preview
print(mgazine)
```

### Downloading datasets from MGnify
```python
# download file by file 
mgazine.download(
    alias="mgnify_file_alias.fasta.gz", 
    to_dir="downloads_folder"
)

# or download all 
mgazine.download_all(to_dir="downloads_folder")
```

### Reading in datasets from MGnify
```python
# support for tsv, csv, txt, jsonl
taxa_table = mgazine.stream(
    alias="mgnify_file_alias.tsv", 
    df_engine="polars"
)

# support for fasta, gff, biom via skbio
skbio_fasta = mgazine.stream(alias="mgnify_file_alias.fasta.gz")
```

## Additional Documentation

- [Interactive OpenAPI documentation](https://www.ebi.ac.uk/metagenomics/api/v2)
- [MGnify. 2026. “RESTful API.” July 13.](https://docs.mgnify.org/src/docs/api.html)
- [MGnify. 2026. “Website and Portal.” July 13.](https://docs.mgnify.org/src/docs/portal.html)
- [mgnipy package docs](https://mgnipy.mgnify.org/)
- [openapi-python-client](https://github.com/openapi-generators/openapi-python-client)


## Development

see [Contributing.md](https://mgnipy.mgnify.org/Contributing.html)

## License

This project is licensed under the GNU General Public License v3.0 or later (GPL-3.0-or-later). See the included [LICENSE](./LICENSE) file for full terms.

## Citation

If you use MGni.py in your work, please cite the project:

MGnipy contributors (2026). MGni.py: a lightweight Python client and toolkit for the MGnify API. Version 0.2.1. https://github.com/EBI-Metagenomics/mgnipy

BibTeX:
```bibtex
@software{mgnipy2026,
  author = {MGnipy contributors},
  title = {MGni.py: a lightweight Python client and toolkit for the MGnify API},
  year = {2026},
  version = {0.2.1},
  url = {https://github.com/EBI-Metagenomics/mgnipy}
}
```

> [!IMPORTANT]
> Also cite MGnify when using MGnify data or analyses: 
> https://docs.mgnify.org/src/docs/about.html#how-to-cite
