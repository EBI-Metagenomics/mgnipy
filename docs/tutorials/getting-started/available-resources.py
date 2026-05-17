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
# #  📚 Intro to MGnify Resources
#
# <button title="Make live" style="display:inline-flex;align-items:center;gap:0.4rem;padding:0.5rem 1rem;border:0;border-radius:100px;background:linear-gradient(135deg,#0f766e,#14b8a6);color:white;box-shadow:0 6px 18px rgba(15,118,110,.25);cursor:pointer;font-size:1rem;" class="thebe-button" onclick="initThebe()">Activate Notebook</button>
#
# The MGnify API provides access to multiple types of resources (or endpoints) such as studies, samples, analyses, runs, and more. This notebook shows you how to
#
# 1. **Discover** what resources are available
# 2. **Inspect** what query parameters each resource accepts
#
# ## Two starting points for querying resources
#
# MGnipy provides two main interfaces:
# - **`MGnipy` client**: High-level interface with built-in helper functions for exploration
# - **Resource proxies** (`mgnipy.V2.proxies`): Direct access to individual resource types
#
# Let's start by exploring available resources via the `MGnipy` client.
#
# ---
#

# %%
# uncomment below if colab
# #!pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple mgnipy
# #!pip install asyncio

# %% [markdown]
#
# ## 1. `MGnipy` Client

# %%
from mgnipy import MGnipy

# init
MG = MGnipy(
    # add a configuration
)

# we can explore which resources are available
MG.list_resources()

# %% [markdown]
# For more detail we can describe the resource

# %%
print("studies list endpoint:")
MG.describe_resources("studies")

print("\n----------\n")

print("analysis detail endpoint:")
MG.describe_resources("analysis")

# %% [markdown]
# To use a given endpoint you can access it as an attribute

# %%
studies = MG.studies
filtered_studies = studies.filter(search="chicken")
filtered_studies.explain()
# or
print("\n----------\n")
filtered_studies = MG.studies(search="chicken")
filtered_studies.explain()

# %% [markdown]
# again to help there are helper functions for each resource proxy such as `.list_supported_params()` `.describe_endpoint()`

# %%
print(studies.list_supported_params())
# or
print("\n----------\n")
studies.describe_endpoint()

# %% [markdown]
# ## 2. Resource `mgnipy.V2.proxies`
#
# Alternatively, many of the same functionalities are available from the resource proxies

# %%
from mgnipy.V2.proxies import Studies

# %%
chicken_studies = Studies(search="chicken")
chicken_studies.describe_endpoint()

print("\n----------\n")
chicken_studies.explain()
