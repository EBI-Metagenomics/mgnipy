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
# # Getting MGnify data
#
# The [MGnify API](https://www.ebi.ac.uk/metagenomics/api/v2/) provides access to MGnify analyses datasets and important metadata such as biome, sample, study, run, analysis details. On this page we demonstrate how to:
#
# - **Get** the metadata using `MGnifier`
# - **Get** the datasets as a `MGazine`
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
# Recall the typical workflow (from [What is MGni.Py?](https://mgnipy.mgnify.org/notebooks/getting-started/1_what_is_mgnipy.html)):
#
# > 1. Start up a `mgnipy.MGnipy` client with your desired configuration
# > 
# > 2. Search in MGnify resources using a MGnifier glass
# > 
# > 3. Receive a MGazine of MGnify datasets
#
# which we will follow in this notebook

# %% [markdown]
# ## 1. `mgnipy.MGnipy` to init session

# %%
from mgnipy import MGnipy

MG = MGnipy(cache_dir=None)

# %% [markdown]
# ## 2. `MGnifier` to query MGnify
#
# for this example we will search MGnify `.studies` for a list of pea studies. 
#
# After we `.get()` the list we will populate each of the study's details / metadata using `.enrich_details()`

# %%
# access studies MGnifier and pass search params (build query set)
pea_studies = MG.studies(biome_lineage="root:Host-associated:Plants", search="pea")

# check out the request url
pea_studies.explain()


# %% [markdown]
# now executing the query url(s). If there were multiple urls in the query set then we could also use `.get_all()` rather than iteratively `.get`ting page by page.

# %%
# MG as client context manager
with MG:
    # get a page of pea study list
    pea_studies.get()
    # now filling with metadata
    pea_studies.enrich_details()

# %% [markdown]
# We can access the detailed metadata via `.metadata` attribute which will return a [`MGnifyMetadata`](TODO) instance that allows you to view as a list, polars or pandas dataframe. 

# %% tags=["hide-output"]
# accessing metadata
meta = pea_studies.metadata

# as pandas dataframe
meta.to_pandas(expand_nested_dicts=True)

# %% [markdown]
# ## 3. `MGazine` of MGnify datasets
#
# To access the study's mgazine use `.datasets`
#
# - Notice how in study details printed above there is a "downloads" field with information about the data. 
#
# - this "downloads" information is used by [`mgnipy.MGazine`](TODO) to allow us to download or read them into our notebook.
#
# - To access the study's mgazine use `.datasets`
#
# - the __str__ representaiton of mgazine gives us a peak into the pipeline versions within, number of downloads and the short description categories

# %% tags=["hide-output"]
# access study mgazine
MZ = pea_studies.datasets

# print for more info
print(MZ)

# also can view more as df
MZ.downloads_df()

# %% [markdown]
# You can read in whole or stream in chunks a dataset by passing its `alias` or `url` to `MGazine.stream()`

# %% tags=["hide-output"]
alias = "ERP014435_GO-slim_abundances_v3.0.tsv"
# reading in above file
df_go = MZ.stream(
    alias=alias,
    chunksize=None,  # default to read in all, set int for chunked reading
    df_engine="pandas",  # or polars
)

df_go.head()

# %%
# run accessions as a list
run_ids = df_go.columns[3:].to_list()
# check it out
print(run_ids)

# %% [markdown]
# you can also `.download()` or `.download_all()` of the files to a directory of your choosing

# %%
MZ.download(alias=alias, to_dir="downloads")

# %% [markdown]
# ---
#
# ## Wrap Up:
#
# This page was a quick start demonstration of:
#
# 1. ✅ Start up a `mgnipy.MGnipy` client with your desired configuration
#
# 2. ✅ Querying MGnify using a `MGnifier` glass
#
# 3. ✅ Accessing the resulting `MGazine` of MGnify datasets
#
# **Next** we will see how we can collect even more metadata for the above list of `run_ids` using  mgnipy's `MGnetizer` and `BioSampler` helpers. 
