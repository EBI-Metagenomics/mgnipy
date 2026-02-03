# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.0
#   kernelspec:
#     display_name: mgnipy
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Demo: Retrieving Mgnify tomatoes
#
# <!-- [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ebi-metagenomics/mgnipy/blob/main/docs/tutorial/demo-mgnify-tomatoes.ipynb) -->

# %% [markdown]
# In this tutorial we demonstrate how MGniPy can be used to retrieve tomato rhizosphere metagenomics analyses available on MGnify. 

# %% [markdown]
# ## Downloading the data

# %%
from mgnipy import Mgnifier

# %%
# init 
glass = Mgnifier(
    db='biomes',
    lineage="root:Host-associated:Plants:Rhizosphere",
    search="tomato",
    page_size=3
)

print(glass)

# %%
glass.preview()

# %%
import asyncio

study_meta = await glass.collect()

display(study_meta)

# %%
