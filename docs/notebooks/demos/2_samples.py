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
# # Finding sample details
#
# From the [MGnify API](https://www.ebi.ac.uk/metagenomics/api/v2/) there are endpoints that provide access to MGnify samples.
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
# For getting started we will initiate our `MGnipy` client with a cache and start building our queries for the samples endpoint of the MGnify API. 

# %%
from mgnipy import MGnipy

# init with cache
MG = MGnipy(cache_dir="temp_example")

# details
print(MG)

# point to samples endpoint
samples = MG.samples

# preview
samples.dry_run()

# %% [markdown]
# Now, let's proceed with executing the queries (or a subset of them for this demo)

# %%
# small query to get 3 per page
modified_search = samples.filter(page_size=3)

with MG:
    # within this client context, get 2 pages of samples resource
    modified_search.get_all(limit=2)
    # and if we want to get details for each sample in the list 
    modified_search.enrich_details()

# check out the metadata
modified_search.metadata.to_pandas(expand_nested_dicts=['metadata'])

# %% [markdown]
# if wanting to cleanup the "temp_example" cache

# %%
#MG.clear_subcaches()
