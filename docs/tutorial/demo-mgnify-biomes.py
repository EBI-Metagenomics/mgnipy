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
# # Explore MGnify Biomes
#
# [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ebi-metagenomics/mgnipy/blob/main/docs/tutorial/demo-mgnify-biomes.ipynb)
#
# In this demo we explore: What [biome classifications](https://bioportal.bioontology.org/ontologies/GOLDTERMS) can we find in MGnify? using mgnipy.
#
# We will:
# 1. Initialize a biome query with either the Biomes proxy or the MGnipy client.
# 2. Filter and preview request URLs before fetching full results.
# 3. Run asynchronous requests to retrieve biome data efficiently.
# 4. Inspect results as a list and visualize them as a hierarchical biome tree.

# %%
# uncomment below if colab
# #!pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple mgnipy
# #!pip install asyncio

# %% [markdown]
# We can use the proxies.Biomes or MGnipy.

# %% [markdown]
# ## Option 1. Proxies
#
# The `Biomes` proxy provides a direct way to query biome information from the MGnify API. You can customize your query using various parameters such as `page_size` and `max_depth` to control the number of results and the depth of the biome hierarchy.
#
# - Use `list_parameters()` to see all available filters and options.
# - The `filter()` method allows you to refine your query further.
# - The `explain()` method previews the constructed API URLs and the first few results.
#
# This approach is useful if you want fine-grained control over the API request and wish to explore the available biome data interactively.

# %%
from mgnipy.V2.proxies import Biomes

biomes = Biomes(
    page_size=50,
)
print("Init url: ", biomes.request_url)
# if not sure what kwargs suupported
print("Supported kwargs for biomes: ", biomes.list_parameters())
# and then
biomes = biomes.filter(
    page_size=15,
    max_depth=6,
)
print("Filtered url: ", biomes.request_url)

# %% [markdown]
# ## Option 2. MGnipy
#
# The `MGnipy` client offers a unified interface to access various MGnify API endpoints, including biomes. This approach is convenient if you want to manage multiple types of queries or resources through a single client object.
#
# - Instantiate `MGnipy` to configure your API access and manage requests.
# - Use `.biomes` to create a biome query with your desired parameters.
# - You can use the same filtering and previewing methods as with the proxy, such as `filter()`, `list_parameters()`, and `explain()`.
#
# This method is ideal for users who prefer an object-oriented workflow and may want to extend their analysis to other MGnify resources beyond biomes.

# %%
from mgnipy import MGnipy

# init
mg = MGnipy(
    # configuration
)

# access proxy
biomes = mg.biomes(
    page_size=50,
)
print("Init url: ", biomes.request_url)
# if not sure what kwargs suupported
print("Supported kwargs for biomes: ", biomes.list_parameters())
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
# If happy with the plan, proceed with the async get requests.

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

# %%
their_studies = biomes[5].studies

# %%
their_studies.explain(head=5)

# %%
their_studies.get()

# %%
study_detail = their_studies[0]
