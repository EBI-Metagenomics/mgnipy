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
# # &#x1F50D; Explore MGnify Biomes 	&#x1F3DE;
#
# [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ebi-metagenomics/mgnipy/blob/main/docs/tutorials/getting-started/mgnify-biomes.ipynb)
#
# ## Introduction
#
# The [GOLD ecosystem classifications](https://bioportal.bioontology.org/ontologies/GOLDTERMS) organize environmental samples into a hierarchical taxonomy of biome types—from broad categories like "Engineered" to specific environments like "Plant rhizosphere."
#
# This demo will show you how to:
#
# 1. **Query biomes** — Discover available biome classifications and explore the hierarchy
# 2. **Preview before fetching** — Use filtering and preview methods to confirm your query before retrieving full results
# 3. **Access results flexibly** — Retrieve biome data as lists, DataFrames, or hierarchical trees
# 4. **Navigate relationships** — Follow links between biomes and associated studies
#
# By the end, we hope you'll be comfortable querying the MGnify biome resource to find relevant studies.

# %%
# uncomment below if colab
# #!pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple mgnipy
# #!pip install asyncio

# %% [markdown]
# We can initiate using `mgnipy.MGnipy` or `proxies.Biomes`

# %% [markdown]
# ## The start: Preparing queries
#
# ### Option 1. `mgnipy.MGnipy`
#
# The `MGnipy` client offers a unified interface to access various MGnify API endpoints, including biomes. This approach is convenient if you want to manage multiple types of queries or resources through a single client object.
#
# - Instantiate `MGnipy` to configure your API access and manage requests.
# - Use `.biomes` to create a biome query with your desired parameters.
# - Use `list_parameters()` to see all available filters and options.
# - The `filter()` method allows you to refine your query further.
# - The `explain()` method previews the constructed API URLs and the first few results.
#
# This method has an additional helper function to list and describe available resources

# %%
from mgnipy import MGnipy

# init
mg = MGnipy(
    # configuration
)

# access proxy
biomes = mg.biomes
print("Initial url: ", biomes.request_url)

# %%
mg.describe_resources("biomes")

# %% [markdown]
# If you would like to know what params are supported for the endpoint there is a helper method you can use: `.list_supported_params()`

# %%
# if not sure what kwargs suupported
print("Supported kwargs for biomes: ", biomes.list_supported_params())

# %% [markdown]
# also like describe_resources() there is a `describe_endpoint()`

# %%
biomes.describe_endpoint(as_dict=True)

# %% [markdown]
# and then can pass as kwargs to `.filter()`

# %%
biomes = biomes.filter(
    page_size=15,
    max_depth=6,
)
print("Filtered url: ", biomes.request_url)

# %% [markdown]
# ### Option 2. Proxies
#
# The `Biomes` proxy provides a direct way to query biome information from the MGnify API. You can customize your query using various parameters such as `page_size` and `max_depth` to control the number of results and the depth of the biome hierarchy. You can use the same filtering and previewing methods as with the proxy, such as `filter()`, `list_parameters()`, and `explain()`.

# %%
from mgnipy.V2.proxies import Biomes

biomes = Biomes(
    page_size=50,
)
print("Init url: ", biomes.request_url)
# if not sure what kwargs suupported
print("Supported kwargs for biomes: ", biomes.list_supported_params())
# and then
biomes = biomes.filter(
    page_size=15,
    max_depth=6,
)
print("Filtered url: ", biomes.request_url)

# %% [markdown]
# ## Previewing your requests
#
# There is an optional intermediary step to
# - `.preview()` the first page of results,  or
# - `.dry_run()` to print the number of pages and records to request
# - `.explain()` to print the planned request urls
# before `.get()`ting all the result pages.

# %%
biomes.explain(head=5)
# or
# biomes.dry_run()
# or
# biomes.preview()

# %% [markdown]
# ## Carry out requests
# If happy with the plan, proceed with the async or sync get requests.

# %%
# asynchronously get the data
await biomes.aget()

# %% [markdown]
# ## Exploring the results
#
# Different means to access the retireved results

# %% [markdown]
# ### as a list

# %%
biomes.to_list()[:5]

# %% [markdown]
# ### as a pandas dataframe

# %%
biomes.to_df().head()

# %% [markdown]
# ### as a dictionary
# where each key is a page

# %%
# look at first 5 records of page 1
biomes.results[1][:5]

# %% [markdown]
# Specific to the biomes, results can also be visualized as a tree "print" "hshow" or "vshow"

# %% tags=["hide-output"]
biomes.show_tree()

# %% [markdown]
# ## Extra: Finding studies for a given biome

# %%
# getting the biome_detail for a specific biome
a_biome = biomes["root:Engineered:Biogas plant:Wet fermentation"]
# what relationships can we traverse from biome detail?
a_biome.list_relationships()

# %%
# lazily access the studies list related to this biome (basically prepping query)
their_studies_list = a_biome.studies

# preview the requests that will be made to get the studies list
their_studies_list.explain()

# asynchronously get the studies list
await their_studies_list.aget()

# look at results
their_studies_list.to_df().head()
