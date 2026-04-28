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
# # &#x1F5C3; Find all MGnify Analyses for a given Study
#
# On this page, we show how to navigate MGnify resources starting from a study and moving to the analyses associated with it using MGni.py.
#
# [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ebi-metagenomics/mgnipy/blob/main/docs/tutorials/getting-started/study-analyses-simple.ipynb)
#
# ## Introduction
#
# It is a common pattern when retrieving data from MGnify: you begin with one biological entity, inspect its details, explore the relationships it exposes, and then traverse those relationships to access related records.
#
# With MGni.py you can use proxies and their links rather than manually constructing API requests and preprocessing.
#
# By the end, you will know how to:
# - load a study by accession
# - fetch the study details from MGnify
# - inspect the relationships available on a study object
# - traverse from a study to its related analyses
# - retrieve and organize analysis details in a convenient tabular form
#
# In this example we start from a single study, but the workflow and traversal could be applied to the other resources.
#
# ---

# %%
# uncomment below if colab
# #!pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple mgnipy
# #!pip install asyncio

# %% [markdown]
# ## Starting from a Study Accession
#
# For this demonstration we use the study accession [`MGYS00010442`](https://www.ebi.ac.uk/metagenomics/v6-early-data-release/studies/MGYS00010442/overview), but you can replace it with any other public study accession to explore different data.

# %%
study_accession: str = "MGYS00010442"

# %% [markdown]
# Here we import and init MGnipy

# %%
import asyncio  # optional, for async requests
import pandas as pd  # also not necessary, only for demo and type annotation
import mgnipy  # for type annotation

from mgnipy import MGnipy

# init
MG = MGnipy()

# access study resource
study = MG.study(study_accession)

# check it out
print(study)

# %% [markdown]
# let's go ahead and get the given study's details then

# %% tags=["hide-output"]
await study.aget()

# check it out
study.to_list()

# %% [markdown]
# ### What relationships exist with our study?
#
# From the study detail we can list their analyses. We can check what other relationshiops are supported using `.list_relationships()`

# %%
study.list_relationships()

# %% [markdown]
# ## To listing MGnify Analyses of the study
#
# Alright back to finding the analyses. We can access the list of associated MGnify Analyses via `.analyses` attribute.
#
# When we call the list endpoint we are lazily building (not yet getting) the queries.
#
# We can take a look at the requests that would be made at `get()` or `aget()` using the `.explain()` helper method.

# %%
# traverse to analyses for the given study detail
study_analyses_list = study.analyses
print(type(study_analyses_list))

# moer info about the endpoint
study_analyses_list.describe_endpoint()

# preview how many analyses to retrieve
study_analyses_list.explain()

# %% [markdown]
# And now if we want to execute the list queries:

# %%
# async get
await study_analyses_list.aget()

# check it out
study_analyses_list.to_df().head()


# %% [markdown]
# We can get the details for each of the analyses in multiple ways. the easiest would be to access from our `study_analyses_list` instance via indexing.
#
# > **Note**: When calling by index we do not need to manually execute `get()` or `aget()`. This will automatically be completed at the calling of the element.

# %%
# to start let's get detail forfirst analysis

# by index
first_analysis = study_analyses_list[0]
# display(first_analysis.to_df())

# or by accession
first_analysis = study_analyses_list["MGYA01021267"]
display(first_analysis.to_df())  # same same as above

# more info about the analysis detail
print("Type: \n", type(first_analysis), "\n")
print("Endpoint description: ")
first_analysis.describe_endpoint()
print("\nAnalysis details: \n", first_analysis)

# %% [markdown]
# Also we can get the AnalysisDetail's for each in our Analyses list by iterating over it, it being e.g.`study_analyses_list`. (sync and async support)
#
# > **Note**: When interating over we do not need to manually execute `get()` or `aget()`. Similar to indexing, this will automatically be completed at the calling of the element.

# %%
# init a dict to store details for all analyses
analysis_detail_dfs: dict[str, pd.DataFrame] = {}

# get the details as dfs
async for analysis in study_analyses_list:
    analysis_detail_dfs[analysis.identifier] = analysis.to_df()

# concat into one df
df_analysis_details = pd.concat(analysis_detail_dfs, ignore_index=True)
# check it out
df_analysis_details.head()

# %% [markdown]
# Alternatively, MGnifyList proxxies (e.g., studies, analyses, samples etc. plural) also have option to `collect_details()` or `.acollect_details()` which will return a list or dict of the associated `MGnifyDetail` proxies (e.g., study, analysis)

# %%
# or if you want to keep them as objects, you can do
analysis_details: dict[str, mgnipy.V2.proxies.AnalysisDetail] = (
    await study_analyses_list.acollect_details(
        fetch=True, by_id=True  # not lazily  # else as a list
    )
)

# for example for further relaionship traversal
# annotations = analysis_details['MGYA01021267'].annotations

# %% [markdown]
# ## Next &#x23ED;
#
# We explore multiple relationship traversal: Getting all metadata from study > samples > runs > analyses
