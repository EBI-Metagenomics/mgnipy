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
# # 🕵️‍♀️ Searching for MGnify Studies
#
# [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ebi-metagenomics/mgnipy/blob/main/docs/tutorials/getting-started/demo-mgnify-tomatoes.ipynb)
#
# On this page, which also serves as a runnable notebook (link above ^), we again demonstrate the basic usability of MGni.py to search the [Studies resource](https://www.ebi.ac.uk/metagenomics/api/v2/#/Studies/list_mgnify_studies) for some studies of interest (e.g., tomaotos)
#
# ---
#
# ## 🎯 The Goal: Get a list of MGnify studies of tomato rhizospheres
#
# WIP
#

# %%
# uncomment below if colab
# #!pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple mgnipy
# #!pip install asyncio

# %%
from mgnipy import MGnipy

MG = MGnipy()

tomato_studies = MG.studies(
    biome_lineage="root:Host-associated:Plants:Rhizosphere", search="tomato"
)

# tomato_studies.explain()

# %% [markdown]
# Choose your entry resource proxy

# %%
# init
MG = MGnipy(
    # configuration
)

# helper
MG.list_resources()


# %% [markdown]
# you can either pass query parameters as dict to `params` or as kwargs.

# %%
# studies resource proxy
studies = MG.studies

# helper
studies.list_supported_params()

# %%
# set up query
filtered_studies = studies.filter(
    biome_lineage="root:Host-associated:Plants:Rhizosphere", search="tomato"
)

# preview before getting all pages
filtered_studies.dry_run()

# %%
# make the get request
await filtered_studies.abulk_fetch()

# look at our list of studies
filtered_studies.to_df()

# %% [markdown]
# ## Getting the study details
#
# From our filtered list of studies we can use `.get_detail()` to iteratively get their details from the [**get_mgnify_study** MGnify API endpoint](https://www.ebi.ac.uk/metagenomics/api/v2/#/Studies/get_mgnify_study)

# %%
while True:
    det = filtered_studies.get_detail()
    if det is None:  # no more details to fetch
        print("Finished fetching details for all studies.")
        break

# %% [markdown]
# We can take a look at all study metadata details which are stored to
#
# - `.collected_details`: the `mgnipy.StudyDetail` instances
# - `.collected_details_rsults`: a dictionary where each item is a accession: detail
# - `.collected_details_df`: a pd.DataFrame where each study metadata detail is a row

# %%
filtered_studies.collected_details_df

# %% [markdown]
# ## Now getting analyses for the given studies
#
# We can see what relationships

# %%
study_details = filtered_studies.collected_details

study_details["MGYS00010296"].list_relationships()

# %%
study_details["MGYS00010296"].analyses
