# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: mgnipy (3.13.13)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Listing biomes
#
# The [GOLD ecosystem classifications](https://bioportal.bioontology.org/ontologies/GOLDTERMS) organize environmental samples into a hierarchical taxonomy of biome types—from broad categories like "Engineered" to specific environments like "Plant rhizosphere."
#
# This demo will show you how to:
#
# 1. **Prepare queries** — Learn different ways to initialize and configure your API requests using MGnipy or direct proxies
# 2. **Preview before fetching** — Use filtering and preview methods (preview, dry_run, explain) to confirm your query before retrieving results
# 3. **Fetch results** — Execute requests using iterative get(), specific page(), or get_all() methods (sync or async)
# 4. **Monitor progress** — Track your requests and check completion status
#
# By the end, we hope you'll be comfortable querying the MGnify resource -- or specifically the biomes resource at least
#
# ```{margin}
# After clicking the "Activate Notebook" button you can run the cells in this browser. Alternatively, you can also click on the 🚀 to launch in colab or binder.
# ```
# <button title="Make live" style="display:inline-flex;align-items:center;gap:0.4rem;padding:0.5rem 1rem;border:0;border-radius:20px;background:linear-gradient(135deg,#0f766e,#14b8a6);color:white;cursor:pointer;font-size:1rem;" class="thebe-button" onclick="initThebeSBT()">Activate Notebook</button>
#
# ---
#

# %%
# uncomment below if colab
# #!pip install mgnipy

# %% [markdown]
# ## Initiating the client
#
# We can initiate using `mgnipy.MGnipy` or `proxies.Biomes`.
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
# > &#x1F4A1; **Tip:** See [Configuration page](https://mgnipy.mgnify.org/notebooks/fundamentals/4_mgnipy_config.html) for more setup details &#x1F6E0;.

# %%
from mgnipy import MGnipy

# init
MG = MGnipy(
    # configuration
    cache_dir=None,  # set to None to disable caching, or specify a directory for caching
)

# access proxy
biomes = MG.biomes

# checking it out
print(biomes)

# %% [markdown]
# ## Preparing queries
#
# Like [describe_resources()](https://mgnipy.mgnify.org/tutorials/getting-started/available-resources.html) there is a `describe_endpoint()` with even more info about the endpoint based on the [openapi.json spec](https://www.ebi.ac.uk/metagenomics/api/v2/openapi.json)

# %%
biomes.describe_endpoint()

# %% [markdown]
# Let's add some search params via `.filter()`

# %%
biomes = biomes.filter(
    page_size=50,
    max_depth=6,
)

# check it out again
print(biomes)

# %% [markdown]
# ## Previewing the query set
#
# There is an optional but recommended step to
# - `.preview()` the first page of results as a `pandas.DataFrame`,  or
# - `.dry_run()` to print the number of pages and records to request
# - `.explain()` to print the planned request urls
#
# *before* `.get()`ting all the result pages.

# %% tags=["hide-output"]
# checking out the request urls to be executed
biomes.explain()


# %% [markdown]
# ## Execute queries
# If happy with the plan, proceed with the async or sync get requests.
#
# There are multiple options:
#
# - `.get()` or `.aget()` like next() iteratively carries out one page/request at a time per call. Returning the page dict or `None` when iteration is complete
# - `page()` or `.apage()` pass specific `page_num`
# - `.get_all()` or `aget_all()` fetch the pages in bulk sync or asynchronously

# %%
# and async
async with MG: 
    await biomes.aget_all(limit=2) # limit to running only 2 of the requests for demo purposes


# %% [markdown]
# ## Checking progress
#
# For a concise update on progress you can use `.progress`

# %%
biomes.progress

# %% [markdown]
# Can also take a look at results as we go along via `.search_results()`. OR Specific to the biomes, results can also be visualized as a tree "print" "hshow" or "vshow"

# %% tags=["hide-output"]
biomes.show_tree()

# %% [markdown]
# ## Tidy up

# %%
# no cache for this isntance but we can clear anywahys
biomes.clear_cache()

# %%
# also can check clients closed
MG.status()
