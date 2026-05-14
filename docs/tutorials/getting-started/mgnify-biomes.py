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
# # 🔎 Intro to querying MGnify Resources
#
# [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ebi-metagenomics/mgnipy/blob/main/docs/tutorials/getting-started/mgnify-biomes.ipynb)
#
# On this page, which also serves as a runnable notebook (link above ^), we demonstrate the basic usability of MGni.py to see what items (e.g., biomes) are available in a given resource (e.g., the Biomes [endpoint of the MGnify API v2](https://www.ebi.ac.uk/metagenomics/api/v2/#/Miscellaneous/list_mgnify_biomes))
#
# ---
#
# ## 🎯 The Goal: Get a list of MGnify Biomes
#
# The [GOLD ecosystem classifications](https://bioportal.bioontology.org/ontologies/GOLDTERMS) organize environmental samples into a hierarchical taxonomy of biome types—from broad categories like "Engineered" to specific environments like "Plant rhizosphere."
#
# This demo will show you how to:
#
# 1. **Prepare queries** — Learn different ways to initialize and configure your API requests using MGnipy or direct proxies
# 2. **Preview before fetching** — Use filtering and preview methods (preview, dry_run, explain) to confirm your query before retrieving results
# 3. **Fetch results** — Execute requests using iterative get(), specific page(), or bulk_fetch() methods (sync or async)
# 4. **Monitor progress** — Track your requests and check completion status
#
# By the end, we hope you'll be comfortable querying the MGnify resource -- or specifically the biomes resource at least

# %%
# uncomment below if colab
# #!pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple mgnipy
# #!pip install asyncio

# %% [markdown]
# We can initiate using `mgnipy.MGnipy` or `proxies.Biomes`

# %% [markdown]
# ## 🖍️ The start: Preparing queries

# %% [markdown]
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
#
# > &#x1F4A1; **Tip:** See [Configuration page](TODO) for more setup details &#x1F6E0;.

# %%
from mgnipy import MGnipy

# init
mg = MGnipy(
    # configuration
    cache_dir=None,  # set to None to disable caching, or specify a directory for caching
)

# access proxy
biomes = mg.biomes

# checking it out
print(biomes)

# %% [markdown]
# In the `print` we can see that we have not initiated any query parameters.
#
# If you would like to know what params are supported for the endpoint there is a helper method you can use: `.list_supported_params()`

# %%
# if not sure what kwargs suupported
print("Supported kwargs for biomes: ", biomes.list_supported_params())

# %% [markdown]
# also like [describe_resources()](https://mgnipy.mgnify.org/tutorials/getting-started/available-resources.html) there is a `describe_endpoint()` with even more info about the endpoint based on the [openapi.json spec](https://www.ebi.ac.uk/metagenomics/api/v2/openapi.json)

# %%
biomes.describe_endpoint()

# %% [markdown]
# Let's add some search params via `.filter()`

# %%
biomes = biomes.filter(
    page_size=5,
    max_depth=6,
)

# check it out again
print(biomes)

# %% [markdown]
# Great we can see that the query string (i.e., after `?`s) has been updated with our given parameters

# %% [markdown]
# ### Option 2. Proxies such as `mgnipy.V2.proxies.Biomes`
#
# - Alternatively, you can also instantiate and configure one resource proxy at a time via the available `mgnipy.V2.proxies` &#x1F60A;
#
# - it all works the same since `mgnipy.V2.proxies.Biomes` is what is returned via:
#
#     ```python
#     # init client
#     mg = MGnipy()
#     # get biomes proxy
#     biomes_proxy = mg.biomes
#     ````

# %%
from mgnipy.V2.proxies import Biomes

biomes = Biomes(
    config={
        "cache_dir": None
    },  # set to None to disable caching, or specify a directory for caching
    page_size=5,
)

# and can filter as well
biomes = biomes.filter(
    max_depth=6,
)
print(biomes)

# %% [markdown]
# ## 👓 Previewing your requests
#
# There is an optional but recommended step to
# - `.preview()` the first page of results as a `pandas.DataFrame`,  or
# - `.dry_run()` to print the number of pages and records to request
# - `.explain()` to print the planned request urls
#
# *before* `.get()`ting all the result pages.

# %%
# checking out first 5 request urls to be made
biomes.explain(head=5)
# or
# biomes.dry_run()
# or
biomes.preview()

# %% [markdown]
# ## 📨 Carry out requests to list endpoints
# If happy with the plan, proceed with the async or sync get requests.
#
# There are multiple options:
#
# - `.get()` or `.aget()` like next() iteratively carries out one page/request at a time per call. Returning the page dict or `None` when iteration is complete
# - `page()` or `.apage()` pass specific `page_num`
# - `.bulk_fetch()` or `abulk_fetch()` fetch the pages in bulk sync or asynchronously

# %% [markdown]
# ### Option 1. `.get()` iteratively
# For a demo of this we will make the first 5 requests.
#
# > **NOTE:** There are protective (for API and user memory) limits to the number of requests that can be made in one bulk fetch call or iteration. However, the requests can be continued using `.continue_interator()` or `.resume()` see [caching notebook](TODO) for more details.

# %%
# getting first 5
for _ in range(5):
    biomes.get()

# %% [markdown]
# For each option there is an async option

# %%
for _ in range(5):
    await biomes.aget()

# %% [markdown]
# and you can take a look at the results as you go &#x1f600; :

# %%
# by page, e.g. page 5
biomes.results[5]

# %%
# or by records, first 2 records
biomes.to_list()[:2]
# or via .records iterator
# list(biomes.records)[:2]

# %% [markdown]
# Specific to the biomes, results can also be visualized as a tree "print" "hshow" or "vshow"

# %%
biomes.show_tree()

# %% [markdown]
# ### Option 2. get a specific `page()`
#
# - Will make the request and also returns the items/records in a list like above.
# - When calling page() on an alrady completed request, the api call is not repeated and instead the output is a page from the cache

# %%
biomes.page(3)

# %% [markdown]
# ### Option 3. `bulk_fetch()` of all requests (with safety limits)
#
# can handle multiple requests via
# - specifying a list of pages to `.bulk_fetch(pages=<list_of_pages>)`
# - or by not specifying pages you can continually call on the method which will let the bulk fetch handle the batching whilst considering `limit=<num_items`
#
# Especially before fetching in bulk we should take a look at the total number of requests/pages.

# %%
# let's first checkout num requests
print("Number of requests:", biomes.num_requests)
# or better yet do a dry_run
biomes.dry_run()

# %% [markdown]
# Now we can get some data sync or async:

# %%
# synchronously fetch first 50 items/records
biomes.bulk_fetch(
    limit=50,  # number of items/records to fetch
)

# %%
# and async
await biomes.abulk_fetch(limit=50)

# %% [markdown]
# ## ⏳ Checking progress
#
# As we saw earlier in the notebook we can take a look at results as we go along. For a concise update on progress you can use `.progress` and `.last_successful_page`

# %%
biomes.progress

# %%
biomes.last_successful_page

# %%
# no cache for this isntance but we can clear anywahys
biomes.clear_cache()
