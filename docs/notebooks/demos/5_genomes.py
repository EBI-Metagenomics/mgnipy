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
# # Downloading genomes 
#
# From the [MGnify API](https://www.ebi.ac.uk/metagenomics/api/v2/) there are multiple endpoints that provide access to MGnify genomes. Using `mgnipy` we can get lists of:
# - `.genomes`
# - `.catalogues`
#
# **and in the details we can get ftp urls for downloading their analyses and sequences :).**
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
# ## Initiate client
#
# For getting started we will initiate our `MGnipy` client with a cache and start building our queries for the genomes endpoint of the MGnify API. 

# %%
from mgnipy import MGnipy 

# Initialize the MGnipy client with a cache directory
MG = MGnipy(cache_dir="genomes")

# Point to genomes endpoint
genomes = MG.genomes()

# Complete dry_run to preview num genomes and possible requests
genomes.dry_run()

# %% [markdown]
# ## Getting genome metadata
#
# Now, let's proceed with executing the queries (or a subset of them via `limit` for this demo)

# %%
# context manager
with MG: 
    # get list of genomes
    genomes.get_all(limit=2)
    # enrich with detailed metadata
    genomes.enrich_details(limit=2)

# %% [markdown]
# Let's take a look at the details we got

# %% tags=["hide-output"]
genomes.metadata.to_pandas()

# %% [markdown]
# ## Downloading data
#
# Great now that we have their details, we can get our `MGazine` of datasets to download or not :) 

# %%
# accessing MGazine of datasets for the 2 MGnify genomes
MZ = genomes.datasets

# can filter to a specific short_description, for example:
MZ_seq = MZ['Nucleic Acid Sequence']

# check it out 
MZ_seq

# %% [markdown]
# From here you can `.download_all()` or `.download()` the files selectively. 

# %% tags=["hide-output"]
# Download all the files in our filtered MGazine MZ_seq to a local directory called "sequences"
MZ_seq.download_all(to_dir="sequences")

# %% [markdown]
# Tip: can also see the associated metadata from the mgazine e.g. `MZ_seq.mgnify_genomes()`

# %% tags=["hide-output"]
MZ_seq.mgnify_genomes.to_pandas()
