# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: mgnipy
#     language: python
#     name: python3
# ---

# %% [markdown]
# # What biomes are available in MGnify? 
#
# In this notebook we visualize the [biome classifications](https://bioportal.bioontology.org/ontologies/GOLDTERMS) of metagenome projects available on mgnify. 
#
# We can use the BiomesMgnifier.

# %%
from mgnipy.V2 import BiomesMgnifier

# prepare url
glass = BiomesMgnifier(
    #biome_lineage="root:Host-associated:Plants:Rhizosphere",
    page_size=50,
    max_depth=6, #max
)

# what are the kwargs supported?
#glass.supported_kwargs

# checkout url
print(glass) #or glass.request_url

# %% [markdown]
# There is an optional intermediary step to `.plan()` or `.preview()` the first page of results before `.get()`ting all the result pages.

# %%
# checking 
glass.plan()

# %% [markdown]
# If happy with the plan, proceed with the async get requests. 

# %%
import asyncio

# asynchronously get the data
df_biomes = await glass.get()

# %% [markdown]
# Results returned as a pandas dataframe

# %%
# check it out
df_biomes.head()

# %% [markdown]
# The results can also be visualized as a tree "print" "hshow" or "vshow"

# %% tags=["hide-output"]
glass.show_tree()
