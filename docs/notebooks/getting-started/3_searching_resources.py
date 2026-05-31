# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: .venv (3.11.14)
#     language: python
#     name: python3
# ---

# %% [markdown]
# #  Accessing MGnify API Resources
#
# The MGnify API provides access to multiple types of resources (or endpoints) such as studies, samples, analyses, runs, and more. This notebook shows you how to
#
# 1. **Discover** what resources are available
# 2. **Inspect** what query parameters each resource accepts
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
# For more details on configuring mgnipy and the detault configuration go to the "congifuration" page

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
# We can learn more about the MGnify API and its available resources via the `MGnipy` client.

# %%
# to list all avail resources
MG.list_resources()

# %% [markdown]
#
# For more detail here we can describe the resource using the helper method `.describe_resource()` or `.describe_resources()`

# %%
print("studies list endpoint:")
MG.describe_resource("studies")

print("\n----------\n")

print("analysis detail endpoint:")
MG.describe_resource("analysis")

# %% [markdown]
# Each of the listed resource proxies above is a `MGnifier` that maps directly to a MGnify API endpoint. More information on the proxies can be found on the [proxies page](https://mgnipy.mgnify.org/notebooks/fundamentals/2_mgnifier_proxies.html), but at a glance:
#
# - the plural resources (e.g. `analyses` `studies`) represent collection/list endpoints from the API 
#     
#     e.g. 
#     - **Studies**: Lists of MGnify studies
#     - **Analyses**: Lists of MGnify pipeline analyses on runs or assemblies
#
#     Usually we use `MGnifyList` endpoints to search or filter for a list of the resource
#
# - the singular (e.g. `analysis` `study`) represent a detail endpoint (i.e., getting the details of a single study, analysis, etc) 
#     
#     e.g. 
#     - **Study**: Details/metadata for a study given its study accession id 
#     - **Analysis**: Details/metadata for a MGnify Analysis given its MGnify analysis accession id 
#
#     `MGnifyDetail` endpoints are used to get the metadata for a given item. 
#
# - typically one would:
#     1. first acquire a MGnifyList of `Studies` 
#     2. and then for each item (study) in `Studies` get their MGnifyDetail `StudyDetail`
#

# %% [markdown]
# ## Accessing a Resource
#
# To use a given endpoint you can access it as an attribute of your `mgnipy.MGnipy` instance. 
#
# By using `MGnipy().<chosen_resource>` the resource proxy (aka endpoint-specific MGnifier) is automatically configured

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
# ## Searching a Resource
#
# Using the supported params we can filter our `MGnifyList`s. 
#
# For example, for `Studies` list we can `.filter` by `search` and `has_analyses_from_pipeline` 
#
# We can pass our search params either: 
# 1.  using `.filter()` **after** accessing the resource from MGnipy (as we had a few cells earlier) OR
# 2.  **during** accessing the resource from MGnipy (see cell below)
#
# Note: `explain` provides a preview of the urls to be called to fulfil our search and populate the Studies list

# %%
# MGnifyList example with studies endpoint
# 1. filter method 
filtered_studies = studies.filter(search="chicken")
filtered_studies.explain()
# or
print("\n----------\n")

# 2. directly with query params in the MGnipy instance attribute
filtered_studies = MG.studies(search="chicken")
filtered_studies.explain()

# %% [markdown]
# Note: `MGnifyDetail`s can also be "filtered" but basically only by accession/id... For example

# %%
# MGnifyDetail example with .study
# 1. filter method 
study = MG.study()
study = study.filter(accession="MGYS00000653")
study.explain()

# or
print("\n----------\n")

# 2. directly with query params in the MGnipy instance attribute
study = MG.study(accession="MGYS00000653")
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
# 2. ✅ Search in MGnify resources using a MGnifier glass
#
# 3. ❌ ~~Receive a MGazine of MGnify datasets~~ (go to next page)

# %% [markdown]
#
