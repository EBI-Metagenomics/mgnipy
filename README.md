# MGni.py

MGni.py (pronounced MAG-nee-pie) is a lightweight python client and toolkit for the [MGnify API](https://www.ebi.ac.uk/metagenomics/api/v2/).

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

- **FAIR**: More findable MGnify analyses and metadata, returned in familiar metagenomics data formats (e.g., GFF, [Darwin Core](https://dwc.tdwg.org/), Dataframes[[pandas](https://pandas.pydata.org/docs/), [polars](https://docs.pola.rs/), [anndata](https://anndata.scverse.org/en/stable/)])
- **Simplifies API interactions:** Let MGni.Py handle the complexity of building, executing, and parsing API calls so you can focus on the data!
- **Fast:** MGni.Py uses caching to speed up API expolation, as well as supports both sync and async API calls

## [Available API Endpoints](https://www.ebi.ac.uk/metagenomics/api/v2/#/)

- **Studies**: MGnify studies are based on ENA studies/projects, and are collections of samples, runs, assemblies, and analyses associated with a certain set of experiments.
- **Samples**: MGnify samples are based on ENA/BioSamples samples, and represent individual biological samples.
- **Runs**: Sequencing runs (ENA run accessions; individual sequencing runs of a sample).
- **Assemblies**: Metagenome assemblies (equivalent to ENA assemblies for one or more runs).
- **Analyses**: MGnify analyses are runs of a standard pipeline on an individual sequencing run or assembly. They can include collections of taxonomic and functional annotations.
- **Publications**: Publications (e.g. journal articles) may describe or analyse the content of MGnify Studies or their corresponding datasets in ENA.
- **Genomes**: MGnify Genomes are annotated draft genomes based on either isolates, or metagenome-assembled genomes (MAGs). They are arranged in biome-specific catalogues.
- **Biomes**: The hierarchical [GOLD ecosystem classifications](https://bioportal.bioontology.org/ontologies/GOLDTERMS) biomes represented in MGnify.

### **Note:** Private Data

- To access your private data in any of these API endpoints you just need your MGnify user and password to obtain a valid sliding auth token via the [MGnify Authentication endpoints](https://www.ebi.ac.uk/metagenomics/api/v2/#/Authentication/token_obtain_sliding).
- for example you can put your login credentials in a `.env` file in your working directory (see [.env.example](https://github.com/EBI-Metagenomics/mgnipy/blob/a9dfdfbb3f669569473e11c7a7c9cf460e6c7d11/.env.example)) and 
- `mgnipy.MGnipyConfig` takes care of getting and caching the auth token so that you can easily access your private data using MGni.py 🎉

- for example you can put your login credentials in a `.env` file in your working directory (see [.env.example](https://github.com/EBI-Metagenomics/mgnipy/blob/a9dfdfbb3f669569473e11c7a7c9cf460e6c7d11/.env.example)) and 
- `mgnipy.MGnipyConfig` takes care of getting and caching the auth token so that you can easily access your private data using MGni.py 🎉


## Installation

### From PyPI
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
# get page by page via .get(), getting 3 pages
for _ in range(3)
    studies.get()

# or via .page(), getting another 3 pages
for i in range(4,7):
    studies.page(i)

# OR potentially all at once in large batches (also async option .abulk_fetch())
studies.bulk_fetch()

# then can enrich with detailed metadata
studies.enrich_details()
```

#### Viewing the metadata
```python
# as pandas
pd_metadata = studies.to_df()

# As polars DataFrame
pl_metadata = studies.to_polars()
pl_metadata = studies.to_polars()

# as json
json_metadata = studies.to_json()

# with all details
detailed_metadata = studies.details_df()
```

### 🗃️ 3. Explore a `mgnipy.MGzine` of datasets

```python
# accessing the mgazine of datasets
mgazine = studies.datasets

# preview
print(mgazine)
```

### Downloading the data
```python
# download file by file 
mgazine.download(to_dir="downloads_folder", alias="mgnify_file_alias.fasta.gz")

# or download all 
mgazine.download_all(to_dir="downloads_folder")
```

### Reading in the data
```python
# support for tsv, csv, txt, jsonl
taxa_table = mgazine.stream(alias="mgnify_file_alias.tsv", df_engine="polars")

# support for fasta, gff, biom via skbio
skbio_fasta = mgazine.stream(alias="mgnify_file_alias.fasta.gz")
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
