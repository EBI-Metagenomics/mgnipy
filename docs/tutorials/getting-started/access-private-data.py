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
# # &#x1F510; Accessing your private data &#x1F513;
#
# - Ideal is to have an .env file with MG_USER and MG_PASSWORD. .env.example file can be found in root of repository
#
# - Alternatively, you can pass mg_user and mg_password when initiating MGnipy or proxies.
#
# - Alternative again is that you will be prompted with an input window to enter username and password. (not ideal though because will have to repeat for every private data query)
#
# ---

# %% [markdown]
# ## Using an env file
# .env file will auto be detected via pydantic settings
#
# or if you prefer a diff file name

# %%
from mgnipy import MGnipy
import os
from dotenv import load_dotenv

# load env file
load_dotenv("path/to/your-env-file")

# %%
# init authenticated client
MG = MGnipy(mg_user=os.getenv("MG_USER"), mg_password=os.getenv("MG_PASS"))

# would be auto authenticated
# my_studies = MG.private_studies

# %% [markdown]
# ## Input
#
# if no .env or not passed to MGnipy or proxies then when private endpoints called you will auto be prompted with an input window for user and then password

# %%
from mgnipy import MGnipy

MG = MGnipy(
    # no config
)
# my_studies = MG.private_studies

# %% [markdown]
# ## then
#
# same as with non-private data

# %%
# my_studies.dry_run()

# %%
# my_studies.get()

# %%
