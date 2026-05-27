# Available API Endpoints

- **Studies**: MGnify studies (collections of samples, runs, assemblies and analyses derived from ENA studies/projects).
- **Samples**: MGnify samples (based on ENA/BioSamples; individual biological samples).
- **Runs**: Sequencing runs (ENA run accessions; individual sequencing runs of a sample).
- **Assemblies**: Metagenome assemblies (equivalent to ENA assemblies for one or more runs).
- **Analyses**: Pipeline analyses (results of running MGnify pipelines on runs or assemblies; includes taxonomic and functional annotations).
- **Publications**: Publications that describe or analyse MGnify Studies/datasets.
- **Genomes**: Annotated draft genomes (isolates or MAGs) arranged in biome-specific catalogues.
- **Biomes**: List all biomes in the MGnify database.

# Available API Endpoints and Proxies

The library exposes a small set of "proxy" classes that map directly to MGnify API resources. Each resource typically has two proxy types:

- *List proxies* (e.g. `Studies`, `Samples`, `Analyses`) which represent collection/list endpoints (e.g. `/studies`, `/samples`).
- *Detail proxies* (e.g. `StudyDetail`, `SampleDetail`, `AnalysisDetail`) which represent per-resource detail endpoints (e.g. `/studies/{accession}`, `/samples/{accession}`).

These proxies live in the `mgnipy.V2.proxies` package and mirror the API surface documented at https://www.ebi.ac.uk/metagenomics/api/v2/.

Brief mapping (proxy → API):

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

Note: exact endpoint names and parameter names are shown in the upstream API docs linked above; the proxies wrap these endpoints and expose Python-friendly helpers.

Where the proxies live

- Package: `mgnipy.V2.proxies`
- Files: `studies.py`, `samples.py`, `runs.py`, `assemblies.py`, `analyses.py`, `publications.py`, `genomes.py`, `biomes.py`, `catalogues.py`

How the proxies behave

- List proxies are callable to add/override query parameters and are iterable (they fetch pages of results). They provide helpers such as `.page()`, `.iter_details`, `.downloads_df`, and `.datasets` where applicable.
- Detail proxies are used to fetch data for a single resource (by accession or id) and expose attributes like `.downloads`, `.metadata`, and convenience download helpers.
- Many proxies include `.filter(...)`/`.params` to build complex queries and `.explain()` helpers to preview the constructed URL.

Examples

Using the high-level `MGnipy` client:

```python
from mgnipy import MGnipy

mg = MGnipy()

# list studies matching a query
studies = mg.studies(search="tomato")  # returns a list-proxy
print(len(studies))

# get a detail for a specific study accession
study = mg.study("MGYS00001234")  # detail factory returns a StudyDetail
print(study.metadata)
```

Using proxies directly:

```python
from mgnipy.V2.proxies import Studies

studies = Studies(params={"search": "soil"})
first = next(studies.iter_details)
print(first["accession"])  # dict-like result for the detail page
```

Where to read more

- Upstream API reference: https://www.ebi.ac.uk/metagenomics/api/v2/
- Proxy source code: `mgnipy/V2/proxies` (see `studies.py`, `samples.py`, etc.)

If you'd like, I can add a small example notebook that demonstrates common workflows (search → iterate details → download files) and link it from the tutorials index.

