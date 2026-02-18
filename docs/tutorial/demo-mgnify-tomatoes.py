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
# # Demo: Retrieving Mgnify tomato samples
#
# [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ebi-metagenomics/mgnipy/blob/main/docs/tutorial/demo-mgnify-tomatoes.ipynb)

# %%
# uncomment below if colab
# #!pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple mgnipy
# #!pip install asyncio

# %% [markdown]
# In this tutorial we demonstrate how mgnipy can be used to retrieve tomato rhizosphere metagenomics analyses (only sample metadata for now) available on MGnify. 

# %% [markdown]
# ## Spying into the metadata using a `Mgnifier`
# We can use a Mgnifier to get metadata for resources: 
# - `studies` with option to filter by biome, pipeline ver, and search terms
# - `samples` for a given study accession
# - `analyses` for a given study accession
# - `genomes` given its accession

# %%
from mgnipy.V2 import StudiesMgnifier

# %% [markdown]
# you can either pass query parameters as dict to `params` or as kwargs. Please refer to [mgnify api docs](https://www.ebi.ac.uk/metagenomics/api/v2/) for the accepted kwargs for now or via attribute `Mgnifier.supported_kwargs`

# %%
# init 
glass = StudiesMgnifier(
    biome_lineage="root:Host-associated:Plants:Rhizosphere",
    search="tomato",
    page_size=5
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
# nice okay let's get the rest of the records (the 3 other pages)

# %% tags=["hide-output"]
import asyncio
study_meta = await glass.get()

# check it out
display(study_meta)

# %% [markdown]
# The matching study accessions can be accessed via attribute `.accessions`

# %% [markdown]
# ## Getting the samples from the studies
#
# We can use `SamplesMgnifier` to get the sample accessions for those study accessioins. 

# %% tags=["hide-output"]
from mgnipy.V2 import SamplesMgnifier

# init
by_study = {}
for acc in glass.accessions:
    lens = SamplesMgnifier(
        study_accession=acc
    )
    # verbose
    print(lens.plan())
    # get sample metadata 
    by_study[acc] = await lens.get()
    # spacing
    print("\n\n")

# %% [markdown]
# it wanting all in one df

# %%
import pandas as pd

# concat
tomato_samples = pd.concat(by_study)

# check it out
tomato_samples.sample(5)

# %% [markdown]
# ## Getting the analyses from the studies
#
# We can use `AnalysesMgnifier` to get the analyses metadata for the study accessioins. 

# %%
from mgnipy.V2 import AnalysesMgnifier

# init
analyses_by_study = {}
for acc in glass.accessions:
    lens = AnalysesMgnifier(
        study_accession=acc
    )
    # verbose
    print(lens.plan())
    # get analyses metadata, but here only first 2 pages for demo purposes 
    analyses_by_study[acc] = await lens.get(pages=[1,2])
    # spacing
    print("\n\n")

# %% [markdown]
# it wanting all in one df

# %%
# currently no results

# # concat
# tomato_analyses = pd.concat(analyses_by_study)

# # check it out
# tomato_analyses.sample(5)
