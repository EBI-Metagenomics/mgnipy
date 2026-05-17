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
# <button title="Make live" style="display:inline-flex;align-items:center;gap:0.4rem;padding:0.5rem 1rem;border:0;border-radius:100px;background:linear-gradient(135deg,#0f766e,#14b8a6);color:white;box-shadow:0 6px 18px rgba(15,118,110,.25);cursor:pointer;font-size:1rem;" class="thebe-button" onclick="initThebe()">Activate Notebook</button>
#
# On this page, which also serves as a runnable notebook (link above ^), we again demonstrate the basic usability of MGni.py to search the [Studies resource](https://www.ebi.ac.uk/metagenomics/api/v2/#/Studies/list_mgnify_studies) for some studies of interest (e.g., tomaotos)
#
# ---
#
# ## 🎯 The Goal: Get a list of MGnify studies of tomato rhizospheres
#
# Let's request tomato rhizosphere study metadata from the  MGnify Studies API.

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

# %% tags=["hide-output"]
# make the get request
await filtered_studies.abulk_fetch()

# look at our list of studies
filtered_studies.to_df()

# %% [markdown]
# ### Getting their study details
#
# From our filtered list of studies we can use `.get_detail()` to iteratively get their details from the [**get_mgnify_study** MGnify API endpoint](https://www.ebi.ac.uk/metagenomics/api/v2/#/Studies/get_mgnify_study)

# %%
# get details for all studies (this will make multiple requests until all details are fetched)
while True:
    # get details for the next study
    det = filtered_studies.get_detail()
    # if no more studies to fetch details for, break the loop
    if det is None:
        print("Finished fetching details for all studies.")
        break

# %% [markdown]
# We can take a look at all study metadata details which are stored to
#
# - `.details`: the `mgnipy.StudyDetail` instances
# - `.details_rsults`: a dictionary where each item is a accession: detail
# - `.details_df`: a pd.DataFrame where each study metadata detail is a row

# %% tags=["hide-output"]
filtered_studies.details_df

# %% [markdown]
# ## 🎯 Next Steps: Getting their MGnify analyses
#
# Using the StudyDetail instances we can also get a list of all their
# - MGnify analyses i.e., `mgnipy.V2.proxies.Analyses` instance
# - publications `mgnipy.V2.proxies.Publications`
# - samples `mgnipy.V2.proxies.Samples`
#

# %% [markdown]
#
# For example lets take a look at the study "MGYS00006204".

# %% [markdown]
# ### Step-by-step example: `MGYS00006204`

# %%
# getting the StudyDetail for the specific study
example_study_details = filtered_studies["MGYS00006231"]

# this is a helper method to list all relationships for the study
example_study_details.list_relationships()

# %% [markdown]
# we can access them as attributes form the StudyDetail. When called the requests will automatically be made to the MGnify API

# %%
example_study_pub_list = example_study_details.publications
print(example_study_pub_list)

example_study_sample_list = example_study_details.samples
print(example_study_sample_list)

example_study_analysis_list = example_study_details.analyses
print(example_study_analysis_list)

# %% [markdown]
# taking a look at the analyses metadata

# %% tags=["hide-output"]
example_study_analysis_list.to_df()

# %% [markdown]
# then we can get the details and so on

# %% [markdown]
# ### On Repeat: Getting all analyses metadata
#
# - loop through every study in `filtered_studies.detail`
# - for each study get the details on all sample analyses appending to a list `analyses_details`
# - then we will take a look as a dataframe

# %% tags=["hide-output"]
import asyncio

study_details_dict = filtered_studies.details

analyses_details = []

for study_id, study_detail in study_details_dict.items():

    # verbose
    print(f"Study {study_id}")

    # populating list of analyses for the study
    study_analyses_list = study_detail.analyses

    # get the analyses details
    while True:
        # get details for the next analysis
        det = await study_analyses_list.aget_detail()
        # adding a delay to avoid overwhelming the API
        await asyncio.sleep(0.5)
        # if no more analyses to fetch details for, break the loop
        if det is None:
            print("Finished fetching details for all analyses.")
            break

    print(f"Number of analyses for study {study_id}: {len(study_analyses_list)}\n")

    analyses_details.append(study_analyses_list.details_df)

# %% [markdown]
# let's look at all the sample analyses metadata in one df

# %% tags=["hide-output"]
import pandas as pd

# concat the list of analyses details dataframes into one dataframe
tomato_analyses = pd.concat(analyses_details)
# take a look
print(tomato_analyses.shape)
tomato_analyses.head()
