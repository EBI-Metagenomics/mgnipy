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
# # MGnify List vs. Detail endpoints
#
# The [MGnify API](https://www.ebi.ac.uk/metagenomics/api/v2) has 2 types of endpoints: 
#
# 1. **list** endpoints which return a (paginated) list of records (dicts) in brief from a MGnify resource
# 2. **detail** endpoints which return a single record (dict) in lots of detail
#
# The list endpoints can accept different search params to filter down the list (e.g., "search", "biome_lineage", "page_size"). In contrast, the detail endpoints only accept a single accession/id. 
#
# In MGni.py, the MGnifier's that correspond to 
# 1. list endpoints are plural e.g. `MG.samples`
# 2. detail endpoints are singular e.g. `MG.sample`
#
# ```{margin}
# After clicking the "Activate Notebook" button you can run the cells in this browser. Alternatively, you can also click on the 🚀 to launch in colab or binder. 
# ```
# <button title="Make live" style="display:inline-flex;align-items:center;gap:0.4rem;padding:0.5rem 1rem;border:0;border-radius:20px;background:linear-gradient(135deg,#0f766e,#14b8a6);color:white;cursor:pointer;font-size:1rem;" class="thebe-button" onclick="initThebeSBT()">Activate Notebook</button>
#
# ---

# %%
from mgnipy import MGnipy

# init client
MG = MGnipy(cache_dir=None)

# check out the endpoints
print(MG.list_resources())

# %% [markdown]
# From `list_resources()` we see plural vs. singular terms e.g. `analyses` vs. `analysis`. 
#
# The plural attributes are list and singular are detail endpoints:

# %%
# accessing a list endpoint
studies_list = MG.studies(search='diabetes')
print(studies_list)
# now getting the list
with MG: 
    studies_list.get() # or .get_all()

display(studies_list.search_results.to_pandas().head())

# accessing a detail endpoint
a_study_detail = MG.study("MGYS00006805")
print(a_study_detail)
# now getting the record
with MG: 
    a_study_detail.get()

display(a_study_detail.search_results.to_pandas())

# %% [markdown]
# ## From list to detailed list
#
# After getting a list of records from a list endpoint, one can beef up the list with additional metadata by using the "child" detail endpoint: e.g. `samples` to `sample`, `assemblies` to `assembly`, etc
#
# there is a method `.enrich_details()` for MGnifyList's that help with this which will iteratively get the list of MGnifyDetails. 

# %%
# populating the list 
with MG: 
    studies_list.enrich_details(limit=3) #can set to None to get all

# checking out the detailed metdata
studies_list.metadata.to_pandas(expand_nested_dicts=True)

# %% [markdown]
# For the enriched studies we can get their MGnifyDetail object via indexing:

# %%
# e.g. int
a_study_detail = studies_list[0]

# or by accession/id
a_study_detail = studies_list['MGYS00006805']
print(a_study_detail)

# %% [markdown]
# or get all of the details as a dict:

# %%
studies_list.mgnify_details

# %% [markdown]
# ## from detail to lists
#
# If you noticed from the prints of the `StudyDetail`s above there are "Supported relationships" which link to other MGnifyLists. 
#
# This means that from a study you can get their collection of samples for example. 

# %%
a_study_detail.list_relationships()

# %% [markdown]
# when we access the relationship, we will automatically `get` the MGnifyList of `.search_results`
#
# However, if we want to enrich with even more detailed `.metadata` we still do the `.enrich_details`

# %%
with MG: #context manager
    # access the samples list for a given study
    a_study_samples = a_study_detail.samples 
    # enrich the samples list further with details
    a_study_samples.enrich_details(limit=4) #can set limit to None to get all

# look at detailed samples list so far
a_study_samples.metadata.to_pandas(expand_nested_dicts=True)

# %% [markdown]
#
