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
# # The `emgapi_v2_client` 
#
# For developing or in case you want to work with the `mgnipy.emgapi_v2_client` sub-package directly.
#
# ---
# ## What is it?  
# `mgnipy.emgapi_v2_client` is a python sub-package in MGni.py that was created from the [openapi.json spec](ttps://www.ebi.ac.uk/metagenomics/api/v2/openapi.json) using [openapi-python-client](https://github.com/openapi-generators/openapi-python-client).
#
# It serves as the initial HTTP client to remove the complexity of direct HTTP requests to version 2 of the MGnify API while maintaining type safety through `attrs`-based models.
#
# ## How was it created?
# This client library was automatically generated from the [MGnify API v2 OpenAPI specification](https://www.ebi.ac.uk/metagenomics/api/v2/openapi.json) using [openapi-python-client](https://github.com/openapi-generators/openapi-python-client). This choice was made in the hopes that it would be easier for MGni.py to be updated with changes to the MGnify API endpoints and models.
#
# See [readme-openapi-python-client.md](readme-openapi-python-client.md) for more information on [openapi-python-client](https://github.com/openapi-generators/openapi-python-client)
#
# ## How does it work? 
#
# ### Each MGnify API endpoint has its own module in emgapi_v2_client
# - Every MGnify API v2 endpoint (e.g., [list_all_biomes](https://www.ebi.ac.uk/metagenomics/api/v2/#/Miscellaneous/list_mgnify_biomes), [get_mgnify_analysis](https://www.ebi.ac.uk/metagenomics/api/v2/#/Analyses/get_mgnify_analysis)) has their own module in emgapi_v2_client (e.g., `mgnipy.emgapi_v2_client.api.miscellaneous.list_mgnify_biomes`, `mgnipy.emgapi_v2_client.api.analyses.get_mgnify_analysis`)
#
# - Within the emgapi_v2_client, the endpoint modules are in the `api` directory: 
#
# ```bash
#             emgapi_v2_client/
#             ├── api/
#             │   ├── analyses/
#             │   │   ├── get_mgnify_analysis.py
#             │   │   └── ...
#             │   ├── assemblies/
#             │   │   ├── get_assembly.py
#             │   │   └── ...
#             │   ├── 'other-api-tag'/
#             │   │   └── ...
#             │   ├── 'another-api-tag'/
#             │   │   └── ...
#             │   └── ...
#             ├── models/
#             │   ├── analysed_run.py
#             │   ├── biome.py
#             │   ├── 'some-other-attrs-data-model'.py
#             │   └── ...
#             └── ...
#
#    - each subdir in api/ corresponds to a tag in the MGnify API e.g., analyses, assemblies
#    - the endpoints for that tag are in that tag's subdir (if multi tags, is in the first)
#    - the `attrs` data models are in models/
# ```
#
# ### Each API endpoint module exposes 4 functions:
#
# 1. `sync`: Blocking request that returns parsed data (if successful) or `None`
# 2. `sync_detailed`: Blocking request that always returns a `Request`, optionally with `parsed` set if the request was successful.
# 3. `asyncio`: async version of `sync`.
# 4. `asyncio_detailed`: async version of `sync_detailed`.
#
# ### Putting it altogether in a demo:
# Below we will have an example where we will find studies of the biome root:Host-associated:Plants
#
# ---
#

# %% [markdown]
# ### What to import
#
# At a minimum:
#
# 1. We need to find and import the appropriate module for our endpoint: [`/Miscellaneous/list_mgnify_biomes`](https://www.ebi.ac.uk/metagenomics/api/v2/#/Miscellaneous/list_mgnify_biomes)
# 2. Get and initiate the `mgnipy.Client` instance
# 3. (Optional) add type annotations

# %%
# uncomment below if colab
# #!pip install mgnipy
# #!pip install asyncio

# %%
# at minimum need
# 1. the path
from mgnipy.emgapi_v2_client.api.miscellaneous import list_mgnify_biomes
# 2. the client
from mgnipy.emgapi_v2_client import Client

# extra nice to have annotations but not required for usage
# 3. the models
from mgnipy.emgapi_v2_client.models import NinjaPaginationResponseSchemaBiome
from mgnipy.emgapi_v2_client.types import UNSET, Response

# %% [markdown]
# ### Initiate the client
#
# To instantiate the python client we really only need the base_url. However there are options for loggiing and other httpx args.
#
# `mgnipy.emgapi_v2_client.Client`/`AuheticatedClient` will take care of constructing and closing the httpx clients

# %%
example_client = Client(base_url="https://www.ebi.ac.uk")
# check it out
print(example_client)

# %% [markdown]
# ### Making the request to the API Endpoint
#
# The get request is made when running the `.sync...()` or `.async...()` functions. For example executing
# ```python
#             with example_client as client:
#                 response = list_mgnify_biomes.sync_detailed(
#                     client=client, page_size=10
#                 )
# ```
# the API will respond with the first page of 10 items from the list_mgnify_biomes endpoint. 
#
#
# #### 🎪 *A peak behind the curtain* 🎪 
# The order of the methods within `list_mgnify_biomes.py` when the above is executed would be:
# 1. `_get_kwargs` to prepare the query params, ensuring that the kwarg exists e.g. that `page_size` is an acceptable kwarg
# 2. the httpx request is made with the kwargs
# 3. `_build_response` to prepare as `Response` type
# 4. In the `Response` is attribute `Response.parsed` which uses `_parse_response` to get response as json / dict
#
# > Note: The difference between with and sans `..._detailed()` is that with returns the whole response and sans only returns the parsed response.

# %%
# prep our search
params = {
    "biome_lineage": "root:Host-associated:Plants",
    "page_size": 25,#the default
    "max_depth": 6,
}

# make the sync call and store respone
with example_client as client:
    # adding type annotation for the response is optional 
    response: Response[NinjaPaginationResponseSchemaBiome] = list_mgnify_biomes.sync_detailed(client=client, **params)

# check
response.status_code

# %% [markdown]
# ### Parsing the response
#
# and if we take a look at the parsed content:

# %%
response.parsed.to_dict().keys()

# %% [markdown]
# - In `items` are records such as the biome_lineages
#     - for the first page of results only
# - In `count` is the total number of records that matched our query.
# **Note: you need to instantiate a new client object every call**
#
# Let's take a closer look at the response

# %%
response.parsed.to_dict()

# %% [markdown]
# ## Async requests support 

# %%
import asyncio 

example_client = Client(base_url="https://www.ebi.ac.uk")

async with example_client as client: 
    parsed_response = await list_mgnify_biomes.asyncio(
        client=client, 
        biome_lineage="root:Host-associated",
        max_depth=6,
        page_size=5,
    )

parsed_response.to_dict()
