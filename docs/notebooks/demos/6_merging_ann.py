# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: mgnipy (3.13.13)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Merging datasets
#
# The Goal: Retrieve taxonomic datasets of multiple tomato rhizosphere studies
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
# ## Initiate client and prepare queries

# %%
from mgnipy import MGnipy

# init with a cache dir
MG = MGnipy(
    cache_dir="downloads"
)

# set up search params for studies resource
tomato_studies = MG.studies(
    biome_lineage="root:Host-associated:Plants:Rhizosphere", search="tomato"
)

# preview using helper method
tomato_studies.dry_run()


# %% [markdown]
# ## Execute queries

# %% tags=["hide-output"]
with MG: 
    # make the request 
    tomato_studies.get()

    # get detailed metadata for the studies
    tomato_studies.enrich_details()

# take a look at the study metadata
tomato_studies.metadata.to_pandas(expand_nested_dicts=True).head()

# %% [markdown]
# ## Access the `MGazine` of datasets
#
# - study details have a `mgnipy.MGazine` which allow us to download and interact with study-level datasets outputed from MGnify.
#
# - We can use `mgnipy.MGazine` to download the datasets onto disk or read them into our notebook.
#
# - To access the study's mgazine use `.datasets`
#
# - the __str__ representaiton of mgazine gives us a peak into the pipeline versions within, number of downloads and the short_description categories

# %% tags=["hide-output"]
# access study mgazine
MZ = tomato_studies.datasets

# filter downloads by short description 
ssu = MZ['Taxonomic assignments SSU']

# can check out downloads details as pandas df
ssu.downloads_df()

# %% [markdown]
# Let's preview one of the files. You can read in whole or stream in chunks (via `chunksize`) a dataset by passing its `alias` or `url` to `MGazine.stream()`

# %% tags=["hide-output"]
# read in one of the taxonomic assignment datasets as a pandas df
df_example = ssu.stream(alias=ssu.aliases[0], chunksize=None, df_engine='pandas')

df_example.head()

# %% [markdown]
# ## Merging taxonomic datasets
#
# For taxonomic datasets there is a special MGazine class, `TaxaMGazine`, that helps with merging the datasets and metadata. 
#
# Then you can get the merged dataset as `to_pandas()` `to_polars()` `to_anndata()` for example. 
#
# Otherwise you could manually read in the datasets and then merge them.

# %%
# accessing specialised TaxaMGazine
tmz = ssu.taxonomic

# %% tags=["hide-output"]
# first lazy loading
tmz.load()

# accessing the 5 datasets in one df
tmz.to_anndata()

# %% [markdown]
# Note: 
# - We can see that only the `var` or features (taxonomy) are annotated. The `obs` or observations (runs/samples) are not yet annotated because we did not collect their metadata. 
# - From here we could use a `MGnetizer` to collect all the detailed metadata for the `.runs_accession` in our MGazine. 
# - See the [Getting started -> Collecting more metadata] demo for more info. 

# %%
# tidying up cache
MG.clear_subcaches()
