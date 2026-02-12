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
# # Demo: Retrieving Mgnify tomato samples
#
# <!-- [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ebi-metagenomics/mgnipy/blob/main/docs/tutorial/demo-mgnify-tomatoes.ipynb) -->

# %% [markdown]
# In this tutorial we demonstrate how MGniPy can be used to retrieve tomato rhizosphere metagenomics analyses (only sample metadata for now) available on MGnify. 

# %% [markdown]
# ## Searching for studies
#
# We can use a Mgnifier to look in a given resource: 
# - `biomes` to look for studies
# - `studies` to look for samples
# - `samples` to look for runs/assemblies
# - `runs` to look for analyses
# - `analyses` to look for results? 
#

# %%
from mgnipy import Mgnifier

# %% [markdown]
# you can either pass query parameters as dict to `params` or as kwargs. Please refer to [mgnify api docs](https://www.ebi.ac.uk/metagenomics/api/docs/) for the accepted kwargs for now or via attribute `Mgnifier.supported_kwargs`

# %%
# init 
glass = Mgnifier(
    resource='biomes',
    lineage="root:Host-associated:Plants:Rhizosphere",
    search="tomato",
    page_size=3
)

print(glass)

# %% [markdown]
# the mgnifier has been initiated only, no request made yet. 
#
# Next we must plan or preview before carrying out the full request (of all page results) 

# %%
glass.plan()

# %% [markdown]
# previewing is basically the same as planning but returns the first page results as a pandas.DataFrame

# %%
glass.preview()

# %% [markdown]
# nice okay let's collect the rest of the records (the one other page)

# %%
import asyncio
study_meta = await glass.collect()
display(study_meta)

# %% [markdown]
# ## Getting the samples from the studies
#
# We will use `Samplifier` which we can provide with a `presearch` which will automatically pass the resulted accessions and collect the associated samples for. 
#
# But you don't need to do a presearch using mgnifier :) 
#
# you can also pass known accessions/study_accessions as a kwarg to the samplifier.

# %%
from mgnipy.metadata import Samplifier

samplify = Samplifier(
    presearch=glass,
    page_size=5
)
    
print(samplify)

# %% [markdown]
# next we plan or preview again before collecting sample data. here if we preview, it returns a dict of dfs, one for each repeating param

# %%
preview_dict = samplify.preview()

preview_dict['MGYS00006231']

# %% [markdown]
# if the preview looks good and youw ant to proceed to collect all then dont provide specific study_accessions of the above to collect, otherwise do.

# %% tags=["hide-output"]
tomato_samples = await samplify.collect(study_accession=['MGYS00006231'])
# check out rseults
tomato_samples['MGYS00006231'].head(10)

# %%
