# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: .venv
#     language: python
#     name: python3
# ---

# %% [markdown]
# # MGnify API Endpoint ≈ a `mgnipy.MGnifier`
#
# In mgnipy, MGnifier's are `proxies` (i.e., "intermediary", "act on behalf of") for the [endpoints](https://www.ebi.ac.uk/metagenomics/api/v2/) (i.e., request url + http protocol) in the MGnify API.
#
# > **TLDR; `mgnipy.MGnifier`s as API Resource `proxies`🗝️**
# > `mgnipy.MGnipy().studies` is the exact same as `mgnipy.proxies.Studies()` which is just a `mgnipy.MGnifier(resource="studies")` with added `studies`-specific functions.
#
# And this is the same for all of the resource proxies (analyses, analysis, study, samples, etc.) not just "studies" in the above example.
#
# ---
#
# ## A `MGnifier` glass
#
# Like how a magnifying glass 🔍 is often associated with searching/querying, the `mgnipy.MGnifier` class is the interface for building, executing and then caching MGnify API queries.
#
# ### ✅ Builds query sets
# Using `MGnifier`, users can specify a resource and query parameters, which get translated (built) into an endpoint (request url or series of request urls (e.g., due to pagination) called a `QuerySet`
#
# ### ✅ Query planning and inspection
# Prior to executing the queries, MGnifier has several built-in methods to estimate and preview the number of requests (pages) to be made, such as `.preview()` `.dry_run()` `.explain()`
#
# ### ✅ Execute the queries
# MGnifier adopts a `QueryExecutor` which handles the executing and caching (via `DiskCheckpointer` mixin) of the query sets.
# There is support for:
# - Single-page access e.g. `.page(n)` , `.get()`
# - Bulk retrieval e.g. `.get_all()`
#
# ### ✅ Parse responses into structured data
# Also used by MGnifier is `mixins.ResultsHandler` which helps to transform the API list and detail responses into usable metadata in familiar data structures, such as dataframes `to_pandas()`, lists and dictionaries.
#
# ---
#
# ## The `proxies` subpackage
#
# Each of the different proxies (e.g., `mgnipy.proxies.StudyDetail`, `mgnipy.proxies.Analyses`) are basically an API endpoint-specific `MGnifier` instance.
#
# e.g., `mgnipy.MGnipy().studies` is the same as `mgnipy.proxies.Studies()` which is `mgnipy.MGnifier(resource="studies")` plus added functionality that is specific to the studies endpoint!!
#

# %% [markdown]
# ## Example equivalents
#
# ```{margin}
# After clicking the "Activate Notebook" button you can run the cells in this browser. Alternatively, you can also click on the 🚀 to launch in colab or binder.
# ```
# <button title="Make live" style="display:inline-flex;align-items:center;gap:0.4rem;padding:0.5rem 1rem;border:0;border-radius:20px;background:linear-gradient(135deg,#0f766e,#14b8a6);color:white;cursor:pointer;font-size:1rem;" class="thebe-button" onclick="initThebeSBT()">Activate Notebook</button>
#
# ---

# %% [markdown]
#
# ### Example 1. A `MGnifyList`
#
# #### starting from `MGnipy` client
# ✨ Recommended ✨ Using the high-level `mgnipy.MGnipy` client:

# %%
# uncomment below if colab
# #!pip install mgnipy

# %%
from mgnipy import MGnipy

# init client w/o caching
MG = MGnipy(cache_dir="temp_example")

# build query set
studies = MG.studies(search="tomato")

# preview
studies.explain()

# %% [markdown]
# #### ≈ starting from `proxies` subpackage

# %%
from mgnipy.proxies import Studies

# init
studies2 = Studies(config=dict(cache_dir="temp_example"), search="tomato")

# we can see same query set as above
studies2.explain()

# %% [markdown]
# #### ≈ starting from `MGnifier`

# %%
from mgnipy import MGnifier

# init
studies3 = MGnifier(
    resource="studies", config=dict(cache_dir="temp_example"), search="tomato"
)

# we can see same query set as above
studies3.explain()

# %% [markdown]
#
# ### Example 2. A `MGnifyDetail`
#
# #### starting from `MGnipy` client
# ✨ Recommended ✨ Using the high-level `mgnipy.MGnipy` client:

# %%
# using the MGnipy inited above
study = MG.study("MGYS00010257")
study.explain()

# %% [markdown]
# #### ≈ starting from `proxies` subpackage

# %%
from mgnipy.proxies import StudyDetail

# init
study2 = StudyDetail(config=dict(cache_dir="temp_example"), accession="MGYS00010257")

# we can see same query set as above
study2.explain()

# %% [markdown]
# #### ≈ starting from `MGnifier`

# %%
# init
study3 = MGnifier(
    resource="study", config=dict(cache_dir="temp_example"), accession="MGYS00010257"
)

# we can see same query set as above
study3.explain()

# %% [markdown]
# From the 2 examples above we demonstrated
#
# 1. `mgnipy.MGnipy().studies` is the exact same as `mgnipy.proxies.Studies()` which is just a `mgnipy.MGnifier(resource="studies")` with added `studies`-specific functions.
#
# 2. `mgnipy.MGnipy().study` is the exact same as `mgnipy.proxies.StudyDetail()` which is just a `mgnipy.MGnifier(resource="study")` with added `study`-specific functions.
#
# ...
#
# And this is the same for the other proxies in mgnipy.
