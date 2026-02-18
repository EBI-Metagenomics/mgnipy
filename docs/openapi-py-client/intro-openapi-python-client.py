# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: mgnipy
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Intro to `openapi-python-client`
#
# Understanding the python client libraries generated using `openapi-python-client`. For if you want to work with the `mgnipy.V1.mgni_py_v1` or `mgnipy.V2.mgni_py_v2` submodules directly.
#
# <details>
# <summary style=color:green> 
# As stated in the README:
# </summary>
# <h1></h1>
#
# Every path/method combo becomes a Python module with four functions:
# 1. `sync`: Blocking request that returns parsed data (if successful) or `None`
# 2. `sync_detailed`: Blocking request that always returns a `Request`, optionally with `parsed` set if the request was successful.
# 3.  `asyncio`: Like `sync` but async instead of blocking
# 4. `asyncio_detailed`: Like `sync_detailed` but async instead of blocking
#
# - All path/query params, and bodies become method arguments.
# - If your endpoint had any tags on it, the first tag will be used as a module name for the function (my_tag above)
#
# <h1></h1>
# </details>
# <br>
#
# Below we will have an example where we will get all studies of the biome and their sample counts: Root:Host-associated:Plants:Rhizosphere
#
# -----

# %% [markdown]
# At a minimum:
#
# 1. We need to find the appropriate module for our query: `studies/studies_list.py`
# 2. Provide the `mgni_py.Client` instance
# 3. (Optional) add type annotations
#
# 2. the client
# from mgnipy.V1.mgni_py_v1 import Client as ClientOne

# %%
# at minimum need
# 1. the path 
from mgnipy.V1.mgni_py_v1.api.studies import studies_list
from mgnipy.V1.mgni_py_v1 import Client

# extra nice to have annotations
# 3. the models
from mgnipy.V1.mgni_py_v1.models import PaginatedStudyList
from mgnipy.V1.mgni_py_v1.types import UNSET, Response

# %% [markdown]
# To instantiate the python client we really only need the base_url. However there are options for loggiing and other httpx args. 
#
# `mgnipy.V1.mgni_py_v1.Client` will take care of constructing and closing the httpx clients

# %%
example_client = Client(
    base_url = "https://www.ebi.ac.uk/metagenomics/api/"
)
# check it out
print(example_client)

# %% [markdown]
# The get request is made when running the `.sync...()` or `.async...()` functions. For example if executing
# ```python
# with example_client as client:
#     response = studies_list.sync_detailed(
#         client=client, page_size=10
#     )
# ```
# the order of the methods within `studies_list.py` is:
#
# 1. `_get_kwargs` to prepare the query params, ensuring that the kwarg exists e.g. that `page_size` is an acceptable kwarg
# 2. the httpx request is made with the kwargs
# 3. `_build_response` to prepare as `Response` type
# 4. In the `Response` is attribute `Response.parsed` which uses `_parse_response` to get response as json / dict
#
# The difference between with and sans `..._detailed()` is that with returns the whole response and sans only returns the parsed response. 
#
# -----
#
# We will now make carry out the example request to get all studies of biome "root:Host-associated:Plants:Rhizosphere".

# %%
# prep our search
params = {
    "biome_name": "root:Host-associated:Plants:Rhizosphere",
    #this is default num of results per page in mgnify
    "page_size": 25,
    #"search": UNSET 
}

# make the sync call and store respone
with example_client as client:
    response = studies_list.sync_detailed(
        client=client, **params
    )

# check 
response.status_code

# %% [markdown]
# and if we take a look at the parsed content:

# %%
response.parsed.to_dict().keys()

# %% [markdown]
# - In `data` is the study metadata
#     - for the first page of results only
# - In `meta` is information on how many results and how many pages thaose results are spread out on based on the given `page_size`
#
#
# **Note: you need to instantiate a new client object every call**
