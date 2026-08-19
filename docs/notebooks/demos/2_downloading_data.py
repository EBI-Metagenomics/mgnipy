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
# # Getting MGnify datasets
#
# The [MGnify API](https://www.ebi.ac.uk/metagenomics/api/v2/) provides access to MGnify analyses datasets and important metadata such as biome, sample, study, run, analysis details. 
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
#
# ## 🎯 The Goal: Retrieve taxonomic datasets of tomato rhizosphere studies
#
# Let's request tomato rhizosphere datasets and metadata from MGnify API.
#
# Recall the typical workflow (from [What is MGni.Py?](https://mgnipy.mgnify.org/notebooks/getting-started/1_what_is_mgnipy.html)):
#
# 1. Start up a `mgnipy.MGnipy` client with your desired configuration
#
# 2. Search in MGnify resources using a MGnifier glass
#
# 3. Receive a MGazine of MGnify datasets
#
# which we will follow in this notebook

# %%
from mgnipy import MGnipy

# 1. init with default config
MG = MGnipy(
    cache_dir="downloads"
)

# 2.a) setup studies mgnifier (build queries)
tomato_studies = MG.studies(
    biome_lineage="root:Host-associated:Plants:Rhizosphere", search="tomato"
)


# %% tags=["hide-output"]
with MG: 
    # 2.b) execute the list query (get the study list)
    tomato_studies.get_all()

    # 2.c) get the study list (execute all detail queries)
    tomato_studies.enrich_details()

# take a look at the studies details results as a pandas df
tomato_studies.metadata.to_pandas(expand_nested_dicts=True)

# %% [markdown]
# ## 3. Accessing the `MGazine` of datasets
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

# print for more info
print(MZ)

# also can view more as df
MZ.downloads_df()

# %% [markdown]
# You can read in whole or stream in chunks a dataset by passing its `alias` or `url` to `MGazine.stream()`

# %%
MZ.stream(
    alias = MZ.aliases[5],
    chunksize=None, # default to read in all, set int for chunked reading
).head()

# %% [markdown]
# You can filter by short descriptioins by passing them as you would an index into square brackets i..e, __getitem__

# %%
ssu = MZ['Taxonomic assignments SSU']
print(ssu)

# now with additional taxonomic helpers
tax = ssu.taxonomic

# %% [markdown]
# The [MGazine informtion page](https://mgnipy.mgnify.org/notebooks/fundamentals/7_mgazine.html) also delves into how to download as well as other options for reading in the files
#
# We will carry on with our filtered TaxaMGazine given [our goal](#-the-goal-retrieve-taxonomic-datasets-of-tomato-rhizosphere-studies) for now. 
#
# for example, we can also combine the taxonomic assignment results into one dataframe e.g. `.to_pandas()`, `.to_polars`, `.X()`

# %% tags=["hide-output"]
# first loading
tax.load()

# accessing the 5 datasets in one df
tax.to_polars().head()

# %%
# also as an annotated dataframe (AnnData)
tax.to_anndata()

# %% [markdown]
# We can see that only the `var` or features (taxonomy) are annotated. The `obs` or observations (runs/samples) are not yet annotated because we did not collect their metadata. 
#
# From here we could use a `MGnetizer` to collect all the detailed metadata for the `.runs_accession` in our MGazine. See the following notebooks for more information

# %%
# tidying up cache
MG.clear_subcaches()

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
# 3. ✅ Receive a MGazine of MGnify datasets
