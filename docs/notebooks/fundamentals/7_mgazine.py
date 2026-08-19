# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: .venv (3.11.7.final.0)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # `MGazine` of MGnify data
#
# ```{margin}
# After clicking the "Activate Notebook" button you can run the cells in this browser. Alternatively, you can also click on the 🚀 to launch in colab or binder.
# ```
# <button title="Make live" style="display:inline-flex;align-items:center;gap:0.4rem;padding:0.5rem 1rem;border:0;border-radius:20px;background:linear-gradient(135deg,#0f766e,#14b8a6);color:white;cursor:pointer;font-size:1rem;" class="thebe-button" onclick="initThebeSBT()">Activate Notebook</button>
#
# ## What is a `mgnipy.MGazine`?
#
# Study and Analysis details include **'downloads'** fields which contain information such as types, short descriptions, urls etc about the datasets outputed from MGnify pipelines.
#
# `mgnipy.MGazine` as well as more analysis-specific classes such as `TaxaMGazine` and `DWCTaxaMGazine` can be used to download the datasets onto disk or read them into our notebooks.
#
# For downloading, MGazine supports the downloading of all filetypes. For streaming (via `mixins.StreamMixin`), the supported filetypes are:
#
# - TSV/CSV — stream_pandas (pandas) or stream_polars (polars) (handles gzipped TSV/CSV).
# - TXT — stream_txt (full text or line-chunks).
# - HTML — stream_html (opens in browser).
# - FASTA / GFF / BIOM — stream_fasta, stream_gff, stream_biom (scikit-bio generators).
# - JSONL / NDJSON — stream_jsonl (pandas or polars).
# - Tree / Newick — stream_tree (scikit-bio).
# - Other — JSON files under other are streamed via stream_json; binary/unsupported types should be downloaded.
#
# ---
#
# ## Accessing a MGazine from a `MGnifier` search
#
# Recalling,
# 1. Start up a `mgnipy.MGnipy` client with your desired configuration
# 2. Search in MGnify resources using a `mgnipy.MGnifier` glass
# 3. **Receive a `mgnipy.MGazine` of MGnify datasets**
#
# For step 2 specifically the following mgnifiers can output a mgazine:
# - `proxies.Study`
# - `proxies.Analysis`
# - `proxies.Studies`
# - `proxies.Analyses`
#
# In this demonstration we will get the `MGazine` of a single study, but this would be the same for a multi-study collection of `proxies.Studies`

# %% tags=["hide-output"]
from __future__ import annotations

from mgnipy import MGnipy

# 1. init with default config
MG = MGnipy()

# 2. search up a study/analysis detail or a list of studies/analyses and get their details
study = MG.study("MGYS00010442")
with MG:
    study.get()

# %% [markdown]
# MGazines for a given study or analysis detail can be accessed via their `.datasets` attributes

# %%
# access the study's mgazine
mz = study.datasets

# check it out
print(mz)

# %% [markdown]
# As we see above, the __str__ representaiton of mgazine gives us a peak into the pipeline versions within, number of downloads and the short_description categories
#
# ## Navigating and filtering a `MGazine`
#
# Built in to mgazine, you can filter the mgazine to a specific pipeline versions and short_descriptions which will return a mgazine again but filtered or a curated mgazine with additional functionalities if available ✨.
#
# You can filter by passing them as you would an index into square brackets i..e, __getitem__

# %%
# above we saw that v6 is the only one so this will return the same basically
ssu = mz["v6"]["Summary of SILVA-SSU taxonomies"]

print(ssu)
# also checking out downloads detials as df
ssu.downloads_df()

# %% [markdown]
# ## Downloading datasets
#
# You can pass the `url` or `alias` if wanting to `.download()` or explore/read in via `.stream()` ONE download file/dataset.
#
# You can look at the file aliases as a list via `.aliases` attribute, also shown in "alias" column in `.downloads_df()`
#
# The urls are also in a column in `.downloads_df()` but there are also helpers `.url_list` and `.url_dict` which provide {alias: url}

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
# ## Reading in a dataset `.stream()`
#
# `.stream() `resolves a download alias or URL and returns the appropriate streaming handler for the file type. It supports returning either a full object (when `chunksize` is `None`) or an iterator of chunks when chunksize is provided.

# %%
df = ssu.stream(alias=one_alias, df_engine="pandas")
df.head()

# %% [markdown]
# ## ✨ Bonus section: The `TaxaMGazine`
#
# There are analysis type-specific mgazines, such as this TaxaMGazine
#
# for example, we can also combine the taxonomic assignment results into one dataframe e.g. `.to_pandas()`, `.to_polars`, `.to_anndata()`

# %% tags=["hide-output"]
taxo = ssu.taxonomic

taxo.load()

taxo.to_pandas().head()

# %% [markdown]
# also annotated dataframes

# %%
taxo.to_anndata()

# %% [markdown]
# tidy up

# %%
MG.clear_subcaches()
