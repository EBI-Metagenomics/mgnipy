# `mgnipy.MGnifier`s as API Resource `proxies`
> **The main idea 🗝️ :**  
> `mgnipy.MGnipy().studies` is the exact same as `mgnipy.V2.proxies.Studies()`which is just a `mgnipy.MGnifier(resource="studies")` with added `studies`-specific functions.

And this is the same for all of the resource proxies (analyses, analysis, study, samples, etc.) not just "studies" in the above example. 

---

## A `MGnifier` glass

Like how a magnifying glass 🔍 is often associated with searching/querying, the `mgnipy.MGnifier` class is the interface for building, executing and then caching MGnify API queries. 

### ✅ Builds query sets
Using `MGnifier`, users can specify a resource endpoint and parameters, which get translated (built) into a request url or series of request urls (e.g., due to pagination) called a `QuerySet`

### ✅ Query planning and inspection
Prior to executing the queries, MGnifier has several built-in methods to estimate and preview the number of requests (pages) to be made, such as `.preview()` `.dry_run()` `.explain()`

### ✅ Execute the queries
MGnifier adopts a `QueryExecutor` which handles the executing and caching (via `DiskCheckpointer` mixin) of the query sets. 
There is support for:
- Single-page access e.g. `.page(n)` , `.get()`
- Bulk retrieval e.g. `.bulk_fetch()`

### ✅ Parse responses into structured data
Also used by MGnifier is `mixins.ResultsHandler` which helps to transform the API list and detail responses into usable metadata in familiar data structures, such as dataframes `to_df()`, lists and dictionaries. 

## What is the `proxies` module

Each resource/endpoint proxy is basically an API endpoint-specific `MGnifier` instance. 

e.g., `mgnipy.MGnipy().studies` is the same as `mgnipy.V2.proxies.Studies()` which is `mgnipy.MGnifier(resource="studies")` plus added functionality that is specific to the studies endpoint!!

### Available API Endpoints and Proxies

`mgnipy` exposes a set of "proxy" classes that map directly to MGnify API resources. Each resource typically has two proxy types:

1. **List proxies** (e.g. `Studies`, `Samples`, `Analyses`) which represent collection/list endpoints (e.g. `/studies`, `/samples`).
2. **Detail proxies** (e.g. `StudyDetail`, `SampleDetail`, `AnalysisDetail`) are used to fetch metadata for a single resource (by accession or id) 

These proxies live in the `mgnipy.V2.proxies` subpackage and mirror the API surface documented at https://www.ebi.ac.uk/metagenomics/api/v2/.

#### Brief mapping (proxy → API):

- `Studies` → GET `/studies` (list). See API: https://www.ebi.ac.uk/metagenomics/api/v2/#/Studies/get_mgnify_studies
- `StudyDetail` → GET `/studies/{accession}` (detail). See API: https://www.ebi.ac.uk/metagenomics/api/v2/#/Studies/get_mgnify_study
- `Samples` → GET `/samples` (list). See API: https://www.ebi.ac.uk/metagenomics/api/v2/#/Samples/get_mgnify_samples
- `SampleDetail` → GET `/samples/{accession}` (detail). See API: https://www.ebi.ac.uk/metagenomics/api/v2/#/Samples/get_mgnify_sample
- `Runs` → GET `/runs` and `RunDetail` → `/runs/{accession}`
- `Assemblies` → GET `/assemblies` and `AssemblyDetail` → `/assemblies/{accession}`
- `Analyses` → GET `/analyses` and `AnalysisDetail` → `/analyses/{accession}`
- `Publications` → GET `/publications` and `PublicationDetail` → `/publications/{pubmed_id}`
- `Genomes` / `Catalogues` → catalogue and genome endpoints (catalogues list, genomes within catalogues)
- `Biomes` → GET `/biomes` and `BiomeDetail` → `/biomes/{biome_lineage}`


## Examples

Using the high-level `MGnipy` client:

```python
from mgnipy import MGnipy

mg = MGnipy()

# list studies matching a query
studies = mg.studies(search="tomato")

# get a detail for a specific study accession
study = mg.study("MGYS00001234") 
```

Using proxies directly:

```python
from mgnipy.V2.proxies import Studies, Study

# MGnifyList
studies = Studies(search="tomato")

# MGnifyDetail
study = Study("MGYS00001234")
```

## Where to read more

- Upstream API reference: https://www.ebi.ac.uk/metagenomics/api/v2/
- Proxy source code: `mgnipy/V2/proxies` (see `studies.py`, `samples.py`, etc.)
