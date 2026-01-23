# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.0
#   kernelspec:
#     display_name: .venv
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Understanding the client library generated using `openapi-python-client`
#
# - with a demo? 
# - mgnipy will be a wrapper or sdk for the api
# - as the generated read me states:
#
# > 1. Every path/method combo becomes a Python module with four functions:
# >    1. `sync`: Blocking request that returns parsed data (if successful) or `None`
# >    1. `sync_detailed`: Blocking request that always returns a `Request`, optionally with `parsed` set if the request was successful.
# >    1. `asyncio`: Like `sync` but async instead of blocking
# >    1. `asyncio_detailed`: Like `sync_detailed` but async instead of blocking
# >
# > 1. All path/query params, and bodies become method arguments.
# > 1. If your endpoint had any tags on it, the first tag will be used as a module name for the function (my_tag above)
# > 1. Any endpoint which did not have a tag will be in `mgnipy_one.api.default`
#
# - so basically we will get the path/method and matching datamodel
# - pass along the user given params
# - make the get request and then transform the result/response
#     - df
#     - anndata
# - caching??
#

# %% [markdown]
# yes so to get started we will use an example of getting all study ids and their sample counts 
#
# e.g. `https://www.ebi.ac.uk/metagenomics/api/v1/studies?biome_name=root%3AHost-associated%3APlants%3ARhizosphere`

# %%
# the path 
from mgni_py_v1.api.studies import studies_list
# the client
from mgni_py_v1 import Client as ClientOne
# the models
from mgni_py_v1.models import PaginatedStudyList
from mgni_py_v1.types import Response, UNSET

base_url = "https://www.ebi.ac.uk/metagenomics/api"
params = dict(
    biome_name="root:Host-associated:Plants:Rhizosphere",
    page_size=25,#default
    search=UNSET

)

# %%
biome_name = "root:Host-associated:Plants:Rhizosphere"
search = UNSET
page_size = 25 #default

# takes care of constructing and closing the httpx clients
client = ClientOne(
    base_url=base_url,
)

with client as client:
    response: Response[PaginatedStudyList] = studies_list.sync_detailed(
        client=client, biome_name=biome_name, search=search, page_size=page_size
    )



# %%
response.parsed.to_dict()['data'][0]

# %%
response.status_code

# %% [markdown]
#

# %%
# import tqdm.asyncio

# %%
# for f in tqdm.asyncio.tqdm.as_completed(result):
#     await result

# %%
