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
# [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ebi-metagenomics/mgnipy/blob/main/docs/tutorial/demo-mgnify-biomes.ipynb)

# %%
# uncomment below if colab
# #!pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple mgnipy
# #!pip install asyncio

# %% [markdown]
# In this notebook we visualize the [biome classifications](https://bioportal.bioontology.org/ontologies/GOLDTERMS) of metagenome projects available on mgnify. 
#
# We can use the BiomesMgnifier or MGnipy.

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

# %% [markdown]
# ## Or using `mgnipy.MGnipy`
#
# A more readable syntax with the same functionality :) 

# %%
from mgnipy import MGnipy

# init
glass = MGnipy()

# biomes endpoint
biomes = glass.biomes

# instead pass search params to filter method
biomes.filter(
    biome_lineage="root:Host-associated:Plants:Rhizosphere",
)

# check it out 
print(biomes)

# %% [markdown]
# Still can asynchronously get results:

# %%
await biomes.get()

# look at first two
biomes[0:2]

# %% [markdown]
# or like above as a df:

# %%
biomes.to_pandas()

# %% [markdown]
# and viz as tree:

# %%
biomes.show_tree("vshow")
