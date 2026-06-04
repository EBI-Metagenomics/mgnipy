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
# # Finding Parkinson's disease taxonomic analyses
#
# In this notebook we aim to imitate the analyses in ["`ABaCo` demo: Parkinson’s disease gut microbiome"](https://mona-abaco.readthedocs.io/en/latest/tutorial/demo-parkinson.html) where the aim was to "integrate the 9 studies while preserving key distinctions from the two patient states (Parkinson’s v.s. Healthy)."
#
# ```{margin}
# After clicking the "Activate Notebook" button you can run the cells in this browser. Alternatively, you can also click on the 🚀 to launch in colab or binder. 
# ```
# <button title="Make live" style="display:inline-flex;align-items:center;gap:0.4rem;padding:0.5rem 1rem;border:0;border-radius:20px;background:linear-gradient(135deg,#0f766e,#14b8a6);color:white;cursor:pointer;font-size:1rem;" class="thebe-button" onclick="initThebeSBT()">Activate Notebook</button>
#
# ---

# %%
# uncomment if colab
# # !pip install mgnipy

# %%
import logging 
logging.basicConfig(level=logging.WARNING)

# %% [markdown]
# ## Searching for studies
#
# To start we configure our MGnipy client and access the MGnify API Studies resource. 
#
# We will filter our query to studies of the gut microbiome that mention "parkinson"s disease. 
#
# We can preview the resulting query urls via `.explain()`

# %%
from mgnipy import MGnipy 

mg = MGnipy(cache_dir='downloads')

pd_studies = mg.studies(
    search='parkinson',
    biome_lineage='root:Host-associated:Human:Digestive system:Large intestine:Fecal',
)

pd_studies.explain()

# %% [markdown]
# looks good. we can proceed with actually executing the list query/queries via .get(). To enrich our list of studies with metadata details we can do this in bulk using `.enrich_details()` or asynchronously via `.aenrich_details()`

# %% tags=["hide-output"]
# populate study list
pd_studies.get()
# enrich studies with metadta
await pd_studies.aenrich_details()

# or even save to file if you prefer
study_meta = pd_studies.details_df(expand_nested_dicts=True)

# check it out 
study_meta.head()

# %% [markdown]
# ## Using `MGazine` to explore the study datasets
#
# we can access the mgazine of datasets via `.datasets` attribute. The study details we retrieved above will also be passed on to the mgazine

# %%
# access mgazine
mz = pd_studies.datasets

# take a look
print(mz)

# %% [markdown]
# For the ABaCo demo we will use the taxonomic analyses and we will use v4 onwards due to differences in pipeline versions and specifically SILVA databases that were used for the taxonomic analysis

# %% tags=["hide-output"]
# can add magazines
mz_taxa = mz['Summary of SILVA-SSU taxonomies'] + mz.v5['Taxonomic assignments SSU']   

# print still works
print(mz_taxa)

# studies details are preserved
import pandas as pd
display(pd.DataFrame(mz_taxa.studies_details))

# %% [markdown]
# ## (Lazy)Loading into one taxonomic dataset

# %% tags=["hide-output"]
# lazyload the mgnify taxanomic assignments datasets
mz_taxa.load()

# calling to_pandas or to_polars will collect the data and return a dataframe
mz_taxa.to_polars().head()

# %% [markdown]
# ## Enriching with metadata
#
# ### taxonomic info

# %%
mz_taxa.taxonomic_metadata()

# %% [markdown]
# if we take a look at the metadata it will be empty

# %%
mz_taxa.metadata().head()

# %%
mz_taxa.to_anndata()

# %% [markdown]
# however we can add additional metadata that we collected manually, or taxacurator can help some

# %% tags=["hide-output"]
# getting some runs metdata, can run this cell multi times
await mz_taxa.aenrich_runs(limit=200)

# check it out
df_runs = pd.DataFrame(mz_taxa.runs_details)
print(df_runs.shape)
display(df_runs.head())

# %%
mz_taxa.enrich_biosamples(limit=10, incl_ena=True)

# check it out
df_biosam = pd.DataFrame(mz_taxa.biosamples_details)
print(df_biosam.shape)
display(df_biosam.head())

# %%
# PICK UP HERE

# %%
# from abaco.dataloader import DataPreprocess, one_hot_encoding
# # Load Parkinson's disease dataset
# path_to_dataset = 'data/dataset_parkinson.csv'
# batch_col = "study_code"
# bio_col = "phenotype"
# id_col = "samples"

# # Convert data path into compatible pd.DataFrame
# df_parkinson = DataPreprocess(
#     path_to_dataset,
#     factors = [
#         id_col,
#         batch_col,
#         bio_col
#     ]
# ).dropna()

# # see if there are 3 categorical and n numeric columns (should be an extra column for location)
# print(df_parkinson.info())
