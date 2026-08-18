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
# # Collecting more metadata
#
# In MGni.py there are helpers for collecting metdata from [MGnify](https://www.ebi.ac.uk/metagenomics/) or [BioSamples](https://www.ebi.ac.uk/biosamples/) for a list of MGnify accessions. 
#
# On this page we will learn how to: 
# - **Collect metadata** from MGnify using `mgnipy.collect.MGnetizer`
# - **Collect metadata** from BioSamples using `mgnipy.collect.BioSampler`
#
# This is especially useful if you already know the list of MGnify items that you would like the detailed metadata for such as a list of study accessions. Additionally, when you already have a MGnify dataset of samples and would like to get more metadata starting from the Run accessions which we will demonstrate below. 
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
# We'll pick up from the previous page where we had downloaded the "ERP014435_GO-slim_abundances_v3.0.tsv" dataset from MGnify. 

# %% tags=["hide-output"]
import pandas as pd 

# read in GO-slim abundances file
df_go = pd.read_csv("downloads/ERP014435_GO-slim_abundances_v3.0.tsv", sep="\t")

# get run accessions as a list
run_ids = df_go.columns[3:].to_list()

# sanity check
df_go.head()

# %% [markdown]
# ## The `MGnetizer`
#
# The run accessions/ids can be passed to a `MGnetizer` to collect their detailed metadata. MGnetizer's are a lot like MGnifiers:
# - they can be accessed as attributes from MGnipy client, inheriting the configuration
# - they build the set of queries lazily which you can explore via `.explain()` before executing them

# %% tags=["hide-output"]
from mgnipy import MGnipy 

# init client
MG = MGnipy(
    cache_dir = None
)

# init mgnetizer
mnet = MG.mgnetizer(
    resource="run", 
    all_ids=run_ids
)

# check out query set
mnet.explain()

# %% [markdown]
# now actually executing the above with `.enrich()` or `.aenrich()`

# %%
with mnet:
    mnet.enrich()

# %% [markdown]
# again we can access the metadata via `.metadata`

# %% tags=["hide-output"]
# as df
run_md = mnet.metadata.to_pandas(expand_nested_dicts=False)
# check it out
run_md.head()

# %% [markdown]
# ## The `BioSampler`
#
# The above sample accessions can be passed to a `BioSampler` to collect even more metadata from the [BioSamples](https://www.ebi.ac.uk/biosamples/) database.
#
# BioSamplers can also be accessed from the MGnipy instance, inheriting config.

# %%
bios = MG.biosampler(sample_ids=run_md["sample_accession"].to_list())
print(bios)

# %% [markdown]
# Note: if wanting to pass runs accessions above instead (e.g., `MG.biosampler(sample_ids=run_ids)`) then `.enrich(incl_ena=True)`
#
# now that we have built the queries we can execute them 

# %%
with bios: 
    bios.enrich()

# %% tags=["hide-output"]
bios.metadata.to_pandas(expand_nested_dicts=False).head()

# %% [markdown]
# From here of course you can take over to merge the sets of MGnify metadata and Biosamples metadata. 
#
# However mgnipy has a helper class that combines a MGnify dataset with its metadata:
#
# ---
#
# ## `MTG` MGic (the) Gatherer
# The MGic gatherer (MTG) takes a dataset as pandas or polars dataframe and MGnify or BioSamples metadata and combines them into a single object. 
#
# MTG can be used to enrich the dataset with metadata, and to convert the dataset into different formats such as pandas, polars, or anndata.
#

# %%
MTG = MG.mtg(
    dataset=df_go, 
    var_cols=["description", "category"],
    var_index="GO",
    obs_index="name_of_your_chosing"
    #mgnify_runs=mnet.metadata.to_list() #can pass here or assign the sets later
)

# can assign the sets at any time after init
MTG.mgnify_runs = mnet.metadata.to_list()
MTG.biosamples_metadata = bios.metadata.to_list()

# info
print(MTG)

# %% [markdown]
# ### Example 1. to `polars`

# %% tags=["hide-output"]
# the original but as a polars df
#MTG.to_polars()

# the feature matrix 
#MTG.X(df_engine="polars") # default is pandas

# the features metadata
#MTG.var_metadata(df_engine="polars")

# the obs (samples) metadata
MTG.obs_metadata(df_engine="polars")

# %% [markdown]
# ### Example 2. to `anndata`
#
# as an annotated dataframe which keeps data matrices aligned with the corresponding metadata -- even when transforming the data so that there are added matrix layers.

# %% tags=["hide-output"]
# to anndata object
an_df = MTG.to_anndata()

# the feature matrix 
#an_df.to_df() # or an_df.X

# the features metadata
#an_df.var

# the obs (samples) metadata
an_df.obs

# %%
# exporting to h5ad file 
fname="example_collectors.h5ad"
an_df.obs = an_df.obs.astype(str) #workaround for h5ad export issue with mixed types in obs
an_df.write_h5ad(fname)

# %%
import anndata as ad 
# read in data
back = ad.read_h5ad(fname)
# check it out
back

# %% [markdown]
# ---
#
# ## Wrap Up:
#
# We started with only a MGnify dataset that included a list of run accessions. 
#
# This page was a quick start demonstration of:
#
# 1. ✅ Using `MGnetizer`s to collect metadata from MGnify
#
# 2. ✅ Collecting even more metadata from BioSamples with `BioSampler`
#
# 3. ✅ Merging the dataset with the rich metadata using `MTG`
