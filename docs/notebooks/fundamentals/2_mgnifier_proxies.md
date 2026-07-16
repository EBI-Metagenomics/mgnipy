# MGnify API Endpoint ≈ a `mgnipy.MGnifier`  

In mgnipy, MGnifier's are `proxies` (i.e., "intermediary", "act on behalf of") for the [endpoints](https://www.ebi.ac.uk/metagenomics/api/v2/) (i.e., request url + http protocol) in the MGnify API. 

> **TLDR; `mgnipy.MGnifier`s as API Resource `proxies`🗝️**
> `mgnipy.MGnipy().studies` is the exact same as `mgnipy.V2.proxies.Studies()` which is just a `mgnipy.MGnifier(resource="studies")` with added `studies`-specific functions.

And this is the same for all of the resource proxies (analyses, analysis, study, samples, etc.) not just "studies" in the above example. 

---
## The MGnify RESTful API: A crash course ⏱️

### The "resources" vs. "endpoints"?
- In REST (REpresentational State Transfer) styling, data are modelled as **"resources"** which can either be a singleton (e.g., `study`) or collection (collection of singletons e.g. `studies`) resource. More on RESTful APIs [here](https://restfulapi.net/resource-naming/). 

- As explained in its [docs](https://www.ebi.ac.uk/metagenomics/api/v2/): In MGnigy API v2, collection resources are accessed via **"list" endpoints** e.g.
    - `https://www.ebi.ac.uk/metagenomics/api/v2/studies/` or `.../analyses/`
    - `.../studies/<studyID>/analyses/` (a "sub-collection")
    - `.../samples/<sampleID>/runs/` (another sub-collection)

- and singleton resources via **"detail" endpoints** e.g. `https://www.ebi.ac.uk/metagenomics/api/v2/studies/<studyID>` or `.../analyses/<analysisId>`

### Querying a resource
- Many of the list endpoints can be further queried/filtered :) the acceptable query parameters are clearly documented in the [docs](https://www.ebi.ac.uk/metagenomics/api/v2/) again e.g. [`/studies/` example](https://www.ebi.ac.uk/metagenomics/api/v2/#/Studies/list_mgnify_studies)
- typically the query parameters will appear in the url after a `?` as key-value pairs combined via `&`s
- together the resulting http request url would look something like e.g. 
    - [`https://www.ebi.ac.uk/metagenomics/api/v2/studies/?search=tomato&page=1`](https://www.ebi.ac.uk/metagenomics/api/v2/studies/?search=tomato&page=1) 
    - which requests from the `studies` collection resource, the first page of `study` singleton resources with "tomato" in their title 

### Where are the results or MGnify datasets? 
- The resulting taxonomic and functional annotation datasets from MGnify pipeline analyses can be downloaded via FTP urls
- These ftp urls are provided in the `downloads` field of detail endpoints such as `/analyses/<analysisId>` and `/studies/<studyId>`

---

## A `MGnifier` glass

Like how a magnifying glass 🔍 is often associated with searching/querying, the `mgnipy.MGnifier` class is the interface for building, executing and then caching MGnify API queries. 

### ✅ Builds query sets
Using `MGnifier`, users can specify a resource and query parameters, which get translated (built) into an endpoint (request url or series of request urls (e.g., due to pagination) called a `QuerySet`

### ✅ Query planning and inspection
Prior to executing the queries, MGnifier has several built-in methods to estimate and preview the number of requests (pages) to be made, such as `.preview()` `.dry_run()` `.explain()`

### ✅ Execute the queries
MGnifier adopts a `QueryExecutor` which handles the executing and caching (via `DiskCheckpointer` mixin) of the query sets. 
There is support for:
- Single-page access e.g. `.page(n)` , `.get()`
- Bulk retrieval e.g. `.bulk_fetch()`

### ✅ Parse responses into structured data
Also used by MGnifier is `mixins.ResultsHandler` which helps to transform the API list and detail responses into usable metadata in familiar data structures, such as dataframes `to_pandas()`, lists and dictionaries. 

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
