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
# # The `mgnipy.MGnipy()` client
#
# Here we provide additional information about the `mgnipy.MGnipy()` client
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
# ## Why start with the `mgnipy.MGnipy` client?
#
# - **Unified configuration:** Central `MGnipyConfig` for base URL, credentials, token handling, and cache settings — one place to change behavior
#
# - **Tidier cache invalidation:** All the cache files across all resource endpoints (e.g., `MG.studies`, `MG.analysis`, `MG.biome`) go to a consistent place. The `MG.clear_subcaches()` can then clear all the mgnipy cache files for all different requests made.
#

# %% [markdown]
# ## Quick to start
#
# You can create a single `MGnipy()` instance and then access resource proxies from it. Those resource proxies aka resource endpoint-specific `MGnifier()`s would then share the same configuration of `MGnipy()`

# %%
from mgnipy import MGnipy

# Create a default client (will pick up .env if present)
MG = MGnipy()

# for example we can access the samples MGnify resource easily
samples = MG.samples
# some info
print(samples)
# more info
samples.describe_endpoint()

# %% [markdown]
# ## API helpers
#
# We can also learn more about the MGnify API using the `mgnipy.MGnipy` client.
#
# - `MG.list_resources()` returns the available endpoint names. 
#
# - `MG.describe_resource()` to read parameter docs extracted from the OpenAPI spec.
#

# %%
# List known resources (strings like 'samples', 'studies', 'analyses')
print(MG.list_resources())

# Describe a resource
MG.describe_resources(MG.list_resources()[0])

# %% [markdown]
# ## Quick cleanup 
#
# The `MG.clear_subcaches()` will clear all the mgnipy cache files, no matter if they were from `MG.studies` vs. `MG.analysis` vs. `MG.biome` etc, in the universal `MG.cache_dir`.
#

# %%
MG.clear_subcaches()
