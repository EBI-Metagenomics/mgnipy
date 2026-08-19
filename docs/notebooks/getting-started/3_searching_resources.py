# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: .venv (3.11.7.final.0)
#     language: python
#     name: python3
# ---

# %% [markdown]
# #  Connecting to the MGnify API
#
# The [MGnify API](https://www.ebi.ac.uk/metagenomics/api/v2/) has many endpoints providing access to multiple types of resources such as studies, samples, analyses, genomes, and more. This notebook shows you how to
#
# 1. **Discover** what resources are available
# 2. **Inspect** what query parameters each resource accepts
# 3. **Build** a set of queries 
#
# ```{margin}
# After clicking the "Activate Notebook" button you can run the cells in this browser. Alternatively, you can also click on the 🚀 to launch in colab or binder. 
# ```
# <button title="Make live" style="display:inline-flex;align-items:center;gap:0.4rem;padding:0.5rem 1rem;border:0;border-radius:20px;background:linear-gradient(135deg,#0f766e,#14b8a6);color:white;cursor:pointer;font-size:1rem;" class="thebe-button" onclick="initThebeSBT()">Activate Notebook</button>
#
# ---

# %%
# uncomment below if colab
# #!pip install mgnipy

# %% [markdown]
#
# ## Starting up a `mgnipy.MGnipy` client 
#
# For more details on configuring mgnipy and the default configuration go to the [config info page](TODO)

# %%
from mgnipy import MGnipy

# init
MG = MGnipy(
    # add a configuration
    cache_dir=None,
)

# print the MGnipy instance to see its configuration (credentials are not printed)
print(MG)

# %% [markdown]
# ## Exploring the available resources
#
# We can learn more about the [MGnify API](https://www.ebi.ac.uk/metagenomics/api/v2/) and its available resources via the `MGnipy` client.

# %%
# to list all avail resources
print(MG.list_resources())

# %% [markdown]
#
# - the plural resources (e.g. `analyses`, `studies`) represent collection/list endpoints from the API 
#     
#     e.g. 
#     - **Studies**: Lists of MGnify studies
#     - **Analyses**: Lists of MGnify pipeline analyses
#
#     Usually we use `MGnifyList` endpoints to search or filter for a list of the resource
#
# - the singular (e.g. `analysis`, `study`) represent a detail endpoint (i.e., getting the details of a single study, analysis, etc) 
#     
#     e.g. 
#     - **Study**: Detailed metadata for a study given its study accession id 
#     - **Analysis**: Detailed metadata for a MGnify Analysis given its MGnify analysis accession id 
#
#     `MGnifyDetail` endpoints are used to get the metadata for a given item. 
#

# %% [markdown]
# A description of the resource and corresponding API endpoint can be viewed using the helper methods `.describe_resource()` for a given one or `.describe_resources()` to see all. 

# %%
print("studies list endpoint:")
MG.describe_resource("studies")

print("\n----------\n")

print("analysis detail endpoint:")
MG.describe_resource("analysis")

# %% [markdown]
# ## Accessing a resource
#
# To use a given endpoint you can access it as an attribute of your `mgnipy.MGnipy` instance (e.g. `MG.<chosen_resource>`) which returns a resource proxy (aka endpoint-specific [MGnifier](TODO))

# %%
# accessing Studies proxy as an attribute of MGnipy instance
studies = MG.studies

# %% [markdown]
# again to help there are helper functions for each resource proxy such as `.list_supported_params()` `.describe_endpoint()`

# %%
# print for more info 
print(studies, "\n----------\n")
# or helper to list supported query params for the endpoint
print(studies.list_supported_params(), "\n----------\n")
# or a helper to describe corresponding API endpoint 
studies.describe_endpoint()

# %% [markdown]
# Notice how the configuration (e.g. `cache_dir=None`) was automatically passed to the proxy instance 🙌

# %% [markdown]
# ## Building a query set
#
# Using the supported params we can refine our query of the resource. For example, for `Studies` list we can `.filter` by `search` and `has_analyses_from_pipeline` 
#
# We can pass our search params: 
# 1. when calling the resource e.g. `MG.studies(<param>=<value>)` or by
# 2. using `.filter(<param>=<value>)` after

# %%
# MGnifyList example with studies endpoint
# 1. at init of resource
filtered_studies = MG.studies(search="chicken")
filtered_studies.explain()

# or
print("\n----------\n")

# 2. filter method 
filtered_studies = studies.filter(search="chicken")
filtered_studies.explain()

# %% [markdown]
# ```{tip}
# `explain` provides a preview of the set of query urls to be called to fulfil our search and populate the Studies list
# ```
#
# `MGnifyDetail`s can also be "filtered" but basically only by accession/id. For example:

# %%
# MGnifyDetail example with .study
# 1. at init of resource 
study = MG.study(accession="MGYS00000653")
# 2. filter method
study = MG.study
study = study.filter(accession="MGYS00000653")
study.explain()

# %% [markdown]
# ---
#
# ## Wrap Up: 
#
# This page was a quick start demonstration of:
#
# 1. ✅ Start up a `mgnipy.MGnipy` client with your desired configuration
#
# 2. ✅ Search in MGnify resources using a `MGnifier` glass
#
# 3. ⬜ _Receive a MGazine of MGnify datasets_ (go to next page)
