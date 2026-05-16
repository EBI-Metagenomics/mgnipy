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
# # 🗄️ Getting to know the cache
#
# [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ebi-metagenomics/mgnipy/blob/main/docs/tutorials/getting-started/understanding-cache.ipynb)
#
# This page provides a quick guide to the cache handled by `DiskCheckpointer` of the `mgnipy.V2.mixins`.
#
# ---
#
# ## Introduction
#
# Every proxy / resource-specific MGnifier *query* (i.e., of specific params) has its own deterministic cache key / subdirectory in a containing `config.cache_dir`.
#
# The cache subdirs are derived from the resource name plus the query parameters via `hashlib.sha256`
#
# In that subdir there will be a manifest file and a json file per request num.
#
# ### An example of what it looks like:
#
# ```bash
#             the_main_cache_dir/
#             ├── 3fddd8853bdd0204eeaeda6c5b9b42b48c8a25ca4f034132d94eb1f93e01ac48/
#             │   ├── mgnipy_manifest.json
#             │   ├── mgnipy_page_1.json
#             │   ├── mgnipy_page_2.json
#             │   └── ...
#             ├── hash_for_some_other_query/
#             │   ├── mgnipy_manifest.json
#             │   ├── mgnipy_page_1.json
#             │   └── ...
#             └── ...
# ```
#
# ### How writing to cache is handled
#
# - Response items for a given page/request num are stored on disk in correspondible `mgnipy_page_<n>.json`
# - The responses are cached after every made request
# - If the response already exists in the cache (i.e., page_1.json exists) then the response is derived from the cache rather than making another request.
# - A `mgnipy_manifest.json` file stores the query details such as the given params and resource being searched. (more info on the manifest [below](#the-manifest))
#
#
# ### How loading from cache is handled
#
# - At every proxy / resource-specific MGnifier instantiation any existing records in cache are attempted to be loaded into the instance, such as to `MGnifier().results`
# - If you don't want these to be loaded from the cache, then clear it before instantiating the query
#
#
# ### Below are guides for:
# 1. &#x1f6e0; [Configuring the cache](#configuring-the-cache)
# 1. &#x1f5fa; [Finding where the cache is stored](#locating-the-cache)
# 2. &#x1f381; [What type of files are in the cache](#inspecting-cache)
# 2. &#x1f9fd; [Clearing the cache](#clearing-the-cache)
#
# ---

# %% [markdown]
# ## Configuring the cache
#
# The outtermost containing directory can be configured with the `mgnipy.MGnipyConfig` or can be pased as a dict argument to `config`
#
# Only `mgnipy.MGnipy` also will accept config_kwargs.
#
# More information can be found on the [config setup page](TODO)

# %% [markdown]
# ### 💾 Where to save
#
# The default cache_dir is based on [platformdirs](https://pypi.org/project/platformdirs/) but you can choose another path

# %%
# if using MGnipyConfig directly
from mgnipy import MGnipyConfig

config = MGnipyConfig(cache_dir="./tmp")
# which can then be passed to MGnipy or proxies/mgnifier
config

# %% [markdown]
# ### 🚫 Disabling the cache
#
# You can do this easily by configuring `cache_dir` as `None`

# %%
from mgnipy import MGnipy
from mgnipy.V2.proxies import Samples

MG = MGnipy(cache_dir=None)

# or
config = MGnipyConfig(cache_dir=None)
MG = MGnipy(config=config)

# or at proxy level, only config as dict, not as kwargs
samples = Samples(config=config)

# %% [markdown]
# ## Locating the cache
# For your given mgnipy / mgnifier instance this cache directory path can be found using `.cache_dir`

# %% [markdown]
# ### 🗃️ Setting and finding the main cache directory
#
# The cache directory is configured via `mgnipy.MGnipyConfig` of by passing
#
# More information can be found on the [config setup page](TODO)

# %% [markdown]
# you can find the `cache_dir` already from the MGnipy delegator / client:

# %%
from mgnipy import MGnipy

MG = MGnipy(
    # config=config,
    # or
    cache_dir="./tmp"
)

MG.cache_dir

# %% [markdown]
# and also from the resource-specific MGnifiers aka proxies if wanted:

# %%
# init samples proxy
samples = MG.samples
print("general cache dir:", samples.config.cache_dir)

# %% [markdown]
# ### 📁 Finding the sub-cache corresponding to a query
#
# The cache subdirs or cache keys within `config.cache_dir` are derived from the resource name plus the query parameters via `hashlib.sha256`
#
# Here is how to find the full path

# %%
# option 1: .cache_dir
print("Planned cache directory based on params and resource:\n", samples.cache_dir)

# %% [markdown]
# The cache directory path is also included in the string representation of the proxy instance :)

# %%
# option 2: __str__
print(samples)

# %% [markdown]
# ## Inspecting Cache

# %% [markdown]
#
# ### 📜 The Manifest
#
# 1. the MGnify API `resource` the requests were being made to e.g., biomes, biome, studies, analyses
# 2. The query `params` e.g. accession, page_size, search
# 3. `count` of the total items/records for the entire query
#     - for list endpoints this would be the total number of listed items across all paginated responses
#     - for detail endpoints the count would be 1 (as a detail corresponds to a single accession/id) or 0 if no match
# 4. while `total_pages` corresponds to the total number of request urls to obtain all `count` num of items
#     - for list endpoints the total_pages or number of requests is dependent on `count` / page_size param (i.e., max number of items to return for a request, default is `page_size=25` items)
#     - for detail endpoints the total_pages would simply be 1 or 0 again.
#
# ### 🗒️ The pages
#
# - Each page_#.json corresponds to a given request_num
# - if list endpoint then the items are listed in the json
# - if detail endpoint then just one item in page_1.json

# %% [markdown]
# ## Clearing the cache
#
# You can clear specific cache keys / subdirectories
#
# but also ❗ **all subdirectories** in cache via `mgnipy.MGnipy.clear_subcaches()` ❗

# %% [markdown]
# ### 🔥 clearing a single cache key
#
# the cache relevant to a given query instance can be cleared via its `.clear_cache()` method

# %%
samples.clear_cache()

# %% [markdown]
# ### 💥 clear ALL cached queries
#
# I mean proceed at your own risk and be careful what path you pass to `cache_dir`:
#
# - this will delete all **"mgnipy_manifest.json"** and **"mgnipy_page_*.json"** files and
# - remove resulting empty cache key subdirs
#
# in whatever path that is passed via `cache_dir`..
#

# %%
# check path again
MG.cache_dir

# %% [markdown]
# looks right, let's clear

# %%
MG.clear_subcaches()

# %% [markdown]
# ----
#
# That's it really.

# %% [markdown]
#
