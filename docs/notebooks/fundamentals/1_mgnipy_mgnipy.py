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
# - **Client as a context manager**: Helps make sure that any connections are closed via `with` block also has helpers for checking status `.status` and to `.close()`/`.aclose()` 
#
# - **Tidier cache invalidation:** All the cache files across all resource endpoints (e.g., `MG.studies`, `MG.analysis`, `MG.biome`) go to a consistent place. The `MG.clear_subcaches()` can then clear all the mgnipy cache files for all different requests made.
#
#

# %% [markdown]
# ## Quick to start
#
# You can create a single `MGnipy()` instance and then access resource proxies from it. Those resource proxies aka resource endpoint-specific `MGnifier()`s would then share the same configuration of `MGnipy()`

# %%
from mgnipy import MGnipy

# Create a default client (will pick up .env if present)
MG = MGnipy(cache_dir="temp_example")

# details
print(MG)

# check if there is an active session (shouldnt be one)
MG.status

# %% [markdown]
# We can then easily point to the different MGnify API endpoints

# %%
# for example we can access the samples MGnify resource
samples = MG.samples

# some info
print(samples)

# more info
samples.describe_endpoint()

# %% [markdown]
# ## Client as Context Manager
#
# > Context managers allow you to allocate and release resources precisely when you want to. The most widely used example of context managers is the with statement. ...
# [Read more here](https://book.pythontips.com/en/latest/context_managers.html)
#
# MGnipy will take care of closing the clients if you use `with` blocks -- alternatively you can `.close()` manually 
#
# For example:

# %%
# small query to get 3 per page 
modified_search = samples.filter(page_size=3)

with MG: 
    # within this client context, get 3 pages of samples resource
    modified_search.bulk_fetch(limit=2)

modified_search.metadata.to_pandas(expand_nested_dicts=True)

# %% [markdown]
# we can check the status of the client to be sure

# %%
MG.status

# also can manuallly close 
# MG.close()

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
