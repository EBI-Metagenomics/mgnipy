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
# # Downloading MGnify Study data
#
# The MGnify API provides access to study and analyses datasets for download. On this page we demonstrate how to:
#
# -  **Discover** what datasets are available
# -  **Download** the datasets
# -  **Stream** or read in the datasets
#
# ```{margin}
# After clicking the "Activate Notebook" button you can run the cells in this browser. Alternatively, you can also click on the 🚀 to launch in colab or binder. 
# ```
# <button title="Make live" style="display:inline-flex;align-items:center;gap:0.4rem;padding:0.5rem 1rem;border:0;border-radius:20px;background:linear-gradient(135deg,#0f766e,#14b8a6);color:white;cursor:pointer;font-size:1rem;" class="thebe-button" onclick="initThebeSBT()">Activate Notebook</button>
#
# ---

# %%
# uncomment below if colab
# #!pip install mgnipy
# #!pip install asyncio

# %%
import logging
logging.basicConfig(level=logging.DEBUG)

# %% [markdown]
#
#
# ## 🎯 The Goal: Retrieve taxonomic datasets of tomato rhizosphere studies
#
# Let's request tomato rhizosphere datasets and metadata from MGnify API.
#
# Recall the typical workflow (from [What is MGni.Py?](https://mgnipy.mgnify.org/notebooks/getting-started/1_what_is_mgnipy.html)):
#
# 1. Start up a `mgnipy.MGnipy` client with your desired configuration
#
# 2. Search in MGnify resources using a MGnifier glass
#
# 3. Receive a MGazine of MGnify datasets
#
# which we will follow in this notebook

# %% [markdown]
# ## 1. and 2. `mgnipy.MGnipy().studies` 
#
# In the below cell we take care of
# - ✅ 1. set up of our MGnipy instance and
# - ✅ 2.a) preparing search for a list of tomato studies using the studies-specific `MGnifier` aka `mgnipy.V2.proxies.studies.Studies`
# - ✅ 2.b) populating list of studies
# - ✅ 2.c) retrieving details (i.e., ALL `StudyDetail`s) for every study in the list 
#

# %% [markdown]
#
# ````{margin} What is happening behind the scenes of:
# **2.b)** .bulk_fetch()
# ```python
# for _ in range(
#     tomato_studies.num_requests
# ):
#     tomato_studies.get()
# ```
#
# **2.c)** .enrich_details()
# ```python
# for _ in range(
#     len(tomato_studies)
# ):
#     tomato_studies.get_detail()
# ```
# ````

# %% tags=["hide-output"]
from mgnipy import MGnipy

# 1. init with default config
MG = MGnipy()

# 2.a) setup studies mgnifier (build queries)
tomato_studies = MG.studies(
    biome_lineage="root:Host-associated:Plants:Rhizosphere", 
    search="tomato"
)

# 2.b) execute the list query (get the study list)
tomato_studies.bulk_fetch()

# 2.c) get the study list (execute all detail queries)
tomato_studies.enrich_details()

# take a look at the studies details results as a pandas df
tomato_studies.to_df(expand_nested_dicts=True)

# %% [markdown]
# ## 3. Accessing the `MGazine` of datasets
#
# - study details have a `mgnipy.MGazine` which allow us to download and interact with study-level datasets outputed from MGnify. 
#
# - We can use `mgnipy.MGazine` to download the datasets onto disk or read them into our notebook. 
#
# - To access the study's mgazine use `.datasets` 
#
# - the __str__ representaiton of mgazine gives us a peak into the pipeline versions within, number of downloads and the short_description categories

# %% tags=["hide-output"]
# access study mgazine
MZ = tomato_studies.datasets

# print for more info 
print(MZ)

# also can view more as df 
MZ.downloads_df

# %% [markdown]
# ### Navigating and filtering a `MGazine`
#
# Built in to mgazine, you can filter the mgazine to a specific pipeline versions and short_descriptions which will return a mgazine again but filtered or a curated mgazine with additional functionalities if available ✨.
#
# FOr accessing a specific pipeline version you can call the veresion as an attribute:

# %%
# above we saw that v5 is the only one so this will return the same basically
v5_data = MZ.v5

# if we print again we will see the same info
print(v5_data)

# %% [markdown]
# You can filter by short descriptioins by passing them as you would an index into square brackets i..e, __getitem__

# %% tags=["hide-output"]
# we want the taxonomic assignments
ssu = v5_data['Taxonomic assignments SSU']

# checking out what it is 
print(type(ssu))
print(ssu)

# downloads_df again 
ssu.downloads_df

# %% [markdown]
# for more options over the filtering of mgazines see the [MGazine informtion page](https://mgnipy.mgnify.org/notebooks/fundamentals/7_mgazine.html). We will carry on with our filtered TaxaMGazine given [our goal](#-the-goal-retrieve-taxonomic-datasets-of-tomato-rhizosphere-studies) for now

# %% [markdown]
# ### Downloading datasets
#
# You can pass the `url` or `alias` if wanting to `.download()` or explore/read in via `.stream()` ONE download file/dataset. 
#
# You can look at the file aliases as a list via `.aliases` attribute, also shown in "alias" column in `.downloads_df`
#
# The urls are also in a column in `.downloads_df` but there are also helpers `.url_list` and `.url_dict` which provide {alias: url}

# %%
# lets try out one 
one_alias = ssu.aliases[0]
print(one_alias)

# downloading to a downloads folder
ssu.download(to_dir="downloads", alias=one_alias) 

# %% [markdown]
# also the option to `download_all()`

# %%
ssu.download_all(to_dir="downloads")

# %% [markdown]
# ### Reading in a dataset `.stream()`
#
# `.stream() `resolves a download alias or URL and returns the appropriate streaming handler for the file type. It supports returning either a full object (when `chunksize` is `None`) or an iterator of chunks when chunksize is provided. 
#
# Supported formats include:
# - TSV/CSV — stream_pandas (pandas) or stream_polars (polars) (handles gzipped TSV/CSV).
# - FASTA / GFF / BIOM — stream_fasta, stream_gff, stream_biom (scikit-bio generators).
# - JSONL / NDJSON — stream_jsonl (pandas or polars).
#
# See [Intro to MGazine page](https://mgnipy.mgnify.org/notebooks/fundamentals/7_mgazine.html) for more information

# %%
df = ssu.stream(alias=one_alias, dataframe_engine="pandas")
df.head()

# %% [markdown]
# ## ✨ Bonus section: The `TaxaMGazine`
#
# There are analysis type-specific mgazines, such as this TaxaMGazine
#
# for example, we can also combine the taxonomic assignment results into one dataframe e.g. `.to_pandas()`, `.to_polars`, `.X()`

# %%
ssu.to_pandas()

# %% [markdown]
# There is also option to enrich with additional metadata! 
#
# 1)  From *already* retrieved `MGnifier` results you can set to `runs_results`, `samples_results`, `studies_results` etc, or
#
# 2) use `.enrich_runs()` etc or `.enrich_biosamples` which will make the get requests for the additional metadata

# %% tags=["hide-output"]
ssu.enrich_runs(limit=None)

# %%
ssu.to_anndata()

# %% [markdown]
# ---
#
# ## Wrap Up: 
#
# This page was a quick start demonstration of:
#
# 1. ✅ Start up a `mgnipy.MGnipy` client with your desired configuration
#
# 2. ✅ Search in MGnify resources using a MGnifier glass
#
# 3. ✅ Receive a MGazine of MGnify datasets
