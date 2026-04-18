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

# %%
# %load_ext autoreload
# %autoreload 2
# for dev
# import logging
# logging.basicConfig(level=logging.INFO)

# %% [markdown]
# # Demo: Get all MGnify analyses for a given Study
#
# [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ebi-metagenomics/mgnipy/blob/main/docs/tutorial/demo-mgnify-tomatoes.ipynb)

# %%
# uncomment below if colab
# #!pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple mgnipy
# #!pip install asyncio

# %% [markdown]
# In this tutorial we demonstrate how mgnipy can be used to get all the analyses metadata for a given study [MGYS00010442](https://www.ebi.ac.uk/metagenomics/v6-early-data-release/studies/MGYS00010442/overview)

# %%
from mgnipy import MGnipy
import asyncio  # optional, for async requests
import pandas as pd  # optional

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
# ## Getting the study metadata
#
# Since we know our MGnify study ID we can provide as accession

# %%
study = MG.studies(accession="MGYS00010442")
print(study)

# %% [markdown]
# if you're happy with that then let's actually retrieve the study info

# %%
await study.aget()
# or
# study.get()

# %% [markdown]
# we can take a look at what was returned in numerous view options
# - `.results` response parsed as dict
# - `.to_list()` put the records as dicts in one list
# - `.to_df()` as pandas dataframe
# - `.to_polars()` as polars dataframe
# - `.to_json()` as json

# %%
study.to_df()

# %% [markdown]
# ## Option 1: Find analyses by study id
# without getting sample and run info
#

# %%
study_analyses = study.analyses
# instead get ~10 at a time instead of default ~25
study_analyses = study_analyses.page_size(10)
# preview
study_analyses.explain()

# %% [markdown]
# alright we want this study's analyses

# %%
await study_analyses.aget()

# %% tags=["hide-output"]
study_analyses_details = await study_analyses.acollect_details(
    fetch=True, by_accession=True  # not lazily  # else as a list
)

# %%
df_study_analyses_details = pd.concat(
    [study_analyses_details[x].to_df() for x in study_analyses_details]
)

df_study_analyses_details.head()

# %% [markdown]
# ## Optional: get sample and runs metadata too

# %% [markdown]
# ### Getting the sample metadata
#
# From our given study we can access their samples metadata by traversing their relationship?
#
# We can preview the number of associated sample records to retrieve and the request urls to do that by using `.explain()`

# %%
study_samples = study.samples
# instead get ~10 at a time instead of default ~25
study_samples = study_samples.page_size(10)
# preview
study_samples.explain()

# %% [markdown]
# further we could take a look at the first page using `.preview()`

# %%
study_samples.preview()

# %% [markdown]
# again if we are happy to proceed, then use aget() or get() to retrieve all samples metadata.
#
# for more control you can retrive page by page using .apage() or .page()

# %%
# for example getting page 5 of sample records for our given study
await study_samples.apage(5)
print("Num pages in results: ", len(study_samples.results))

# now lets go ahead and get all
await study_samples.aget()
print("Num pages in results: ", len(study_samples.results))

# %% [markdown]
# **Note:** At first there were 2 pages despite us ony getting one page e.g. 5, because the previewed page 1 previously was cached as to not unnecessarily rerun the same request.
#
# Now let's take a look at the brief sample metadata.

# %%
study_samples.to_df().sample(5)

# %% [markdown]
# We can get more details about each sample, which includes the option to traverse their relationships to associated runs

# %% tags=["hide-output"]
study_samples_details = await study_samples.acollect_details(
    fetch=True, by_accession=True  # not lazily  # else as a list
)

# %%
study_samples_details["SAMEA8156338"].to_df()

# %% [markdown]
# ### And now traversing their runs metadata

# %%
# init the runs proxy for each sample
sample_run_lists = {k: study_samples_details[k].runs for k in study_samples_details}
# now we can get the details for each run proxy


# %% [markdown]
# **Note:** We cannot complete aget() or get() at init. e.g.
# ```
# >>> sample_run_lists = {k: await study_samples_details[k].runs.aget() for k in study_samples_details}
# "AssertionError: Please run .dry_run() or .preview() or .explain()before deciding to collect metadata."
# ```
# This is because there is a safety intermediary step where the built requests must be previewed in some way before retriving all.
#

# %% tags=["hide-output"]
# now we can get the details for each run proxy
for sample in sample_run_lists:
    print(f"Sample: {sample}")
    sample_run_lists[sample].explain()
    await sample_run_lists[sample].aget()
    print(f"Runs for sample {sample}: {len(sample_run_lists[sample].results)}")

# %% tags=["hide-output"]
runs_details = {
    sample: await sample_run_lists[sample].acollect_details(
        fetch=True,  # not lazily
        # by_accession=True # else as a list
    )
    for sample in sample_run_lists
}

# %% [markdown]
# we can take a look at the runs details

# %%
import pandas as pd

df_runs_details = pd.concat([runs_details[run][0].to_df() for run in runs_details])

df_runs_details.head()

# %% [markdown]
# ### And now traversing to analyses metadata

# %%
# init
run_analyses_list = {k: runs_details[k][0].analyses for k in runs_details}
# get analyses metadta for each run
analyses_details = {
    run: await sample_run_lists[run].acollect_details(
        fetch=True,  # not lazily
        # by_accession=True # else as a list
    )
    for run in run_analyses_list
}

# %%
df_analyses_details = pd.concat(
    [analyses_details[a][0].to_df() for a in analyses_details]
)

df_analyses_details.head()

# %% [markdown]
# # stop

# %%

# %%
from mgnipy._shared_helpers.ena_helpers import (
    get_analyses_accession_by_study_accession,
    ENAAnalysisFields,
)

get_analyses_accession_by_study_accession(limit=10)

# %%
ENAAnalysisFields.all_values_as_str()
