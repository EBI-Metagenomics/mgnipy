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
# # Accessing your private data
#
# This page explains how to access private MGnify data.
#
# ---
#
# - Recommended: keep an `.env` file with `MG_USER` and `MG_PASSWORD` (see [.env.example](https://github.com/EBI-Metagenomics/mgnipy/blob/92a70c5f489d1fa16943585fcd50cef253bb61db/.env.example) in the repo). These are auto-loaded into `mgnipy.MGnipyConfig` via pydantic settings.
# - Alternatively, pass credentials directly when creating a config: `config = MGnipyConfig(mg_user="...", mg_password="...")` and use that with `mgnipy.MGnipy` or resource proxies.
#
#     <br>
#     <details style="font-size:16px">
#     <summary style="color:green; font-size:18px; font-weight:600">
#         How the authentication works (sliding token):
#     </summary>
#     </summary>
#     <h1></h1>
#
#     - `mgnipy.MGnipyConfig` takes care of obtaining an authentication token from the [token_obtain_sliding](https://www.ebi.ac.uk/metagenomics/api/v2/#/Authentication/token_obtain_sliding) endpoint of the MGnify API using your username/password
#     - The auth token is verified using the [token_verify](https://www.ebi.ac.uk/metagenomics/api/v2/#/Authentication/token_verify) endpoint and, if valid, refreshed using [token_refresh_sliding](https://www.ebi.ac.uk/metagenomics/api/v2/#/Authentication/token_refresh_sliding) when needed.
#         - The high-level methods within `mgnipy.MGnipyConfig` involved are `obtain_auth_token`, `verify_auth_token`, `refresh_auth_token`, and `resolve_auth_token`.
#     - The resolved token is stored in `MGnipyConfig.auth_token` for the session and used for authenticated API requests.
#     - By default the token is cached on disk under a platform-appropriate cache dir (via `platformdirs`) in a file named auth_<hash>.json.
#         - You can disable disk caching by setting `cache_dir=None` on MGnipyConfig.
#     - On success `resolve_auth_token()` will confirm authentication, it prints `"Authenticated successfully."`
#
#     <h1></h1>
#     </details>
#     <br>
#
# ---
#
# ## Quick configuration examples:

# %% [markdown]
# ### **Option 1.** (Recommended) Auto-loading from an `.env` file
# - Use an `.env` file (recommended). See [`.env.example`](https://github.com/EBI-Metagenomics/mgnipy/blob/92a70c5f489d1fa16943585fcd50cef253bb61db/.env.example) — variables `MG_USER` and `MG_PASSWORD`.
#     - example `.env` contents:
#         ```.env
#                     MG_USER=<your MGnify or ENA username>
#                     MG_PASSWORD=<your MGnify or ENA password>
#         ```
# - The .env file and `MG_USER` and `MG_PASSWORD` variables will auto be detected via pydantic settings and stored safely in `mgnipy.MGnipyConfig`

# %%
# if .env files then can just proceed as normal, for example in a notebook:
from mgnipy import MGnipy

MG = MGnipy()  # will automatically look for .env file and load credentials if found

# %% [markdown]
# ### **Option 1.5** If using a different filename than .env
#
# Or if you prefer an env file name with a different filename then .env
# 1. you can manually load your given file by passing its path to `dotenv.load_dotenv`
# 2. and then use `os.getenv` to get out your MGnify user and pass variables
# 3. initiate `mgnipy.MGnipy` or resource-specific `MGnifier` instances (e.g., `mgnipy.V2.proxies`) with those login credentials like above

# %%
from dotenv import load_dotenv
import os
from mgnipy import MGnipyConfig

# load env variables from specific filename
load_dotenv("path/to/your-env-file")

# pass to config
config = MGnipyConfig(
    mg_user=os.getenv("MG_USER"), mg_password=os.getenv("MG_PASSWORD")
)

# pass config to MGnipy
MG = MGnipy(config=config)
# or directly to proxy
from mgnipy.V2.proxies import Biomes
biomes = Biomes(config=config)

# %% [markdown]
#
# ### **Option 2.** Explicity Configure
# Manually pass the login credentials to `mgnipy.MGnipy` or resource-specific `MGnifier` instances (e.g., `mgnipy.V2.proxies`) at init.

# %%
# pass login credentials to config
config = MGnipyConfig(
    mg_user="this-is-a-fake-user-name", mg_password="this-is-a-fake-password"
)

# pass config to MGnipy
MG = MGnipy(config=config)

# %% [markdown]
# ### **Option 3.** Pass credentials interactively
# if no .env or not passed to MGnipy or proxies then when private endpoints called you will be prompted with an input window for user and then password. Such as for endpoints with only private data e.g. private_studies

# %%
# requires sliding authentication token using user and pass
my_studies = MG.private_studies

# %% [markdown]
# ## Then...
#
# You can continue the same process as you would with non-private resources

# %%
# previewing query
# my_studies.explain()

# %%
# getting a page
# my_studies.get()
