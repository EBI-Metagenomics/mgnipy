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
# # Download study analyses
#
# In this demonstration we will download the analyses for a given MGnify study. 
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
# For this example we come with a MGnify study accession of interest: `MGYS00005116`. Thus, we will use the `study`-specific mgnifier to retrieve its details. 
#
# ```{margin}
# See the *Merging datasets* notebook to retrieve multiple studies' analyses. 
# ```

# %% [markdown]
# ## Initiate client and get study metadata

# %%
from mgnipy import MGnipy

study_accession = "MGYS00005116"

# init (cache optional)
MG = MGnipy(cache_dir=None)

# study mgnifier for building our query
study = MG.study(study_accession)

# executing the query to get study details 
with MG: 
    study.get()

# taking a look at the metadata for the study
study.metadata()

# %% [markdown]
# ## Download study datasets
#
# We can download datasets via the returned `MGazine` of datasets. Can `.download()` one dataset at a time, filter down list of datasets to download, or `.download_all()`.

# %%
# access mgazine
MZ = study.datasets

# filter to pipeline version 4.1 for example 
mz_4_1 = MZ['v4_1']
# download all 
mz_4_1.download_all(to_dir="temp_example")

# %% [markdown]
#
