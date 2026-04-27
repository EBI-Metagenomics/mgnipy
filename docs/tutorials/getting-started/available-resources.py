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
# #  &#x1F575; Exploring MGnify Resources &#x1F5C2;
#
# The MGnify API provides access to multiple types of resources (or endpoints) such as studies, samples, analyses, runs, and more. This notebook shows you how to:
#
# 1. **Discover** what resources are available
# 2. **Inspect** what parameters each resource accepts
# 3. **Query** resources using two different approaches
#
# ## &#x270C; Two Ways to Query Resources
#
# MGnipy provides two main interfaces:
# - **`MGnipy` client**: High-level interface with built-in helper functions for exploration
# - **Resource proxies** (`mgnipy.V2.proxies`): Direct access to individual resource types
#
# Let's start by exploring available resources using the `MGnipy` client.
#
# ---
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
print(filtered_studies.explain())
# or
print("\n----------\n")
filtered_studies = MG.studies(search="chicken")
print(filtered_studies.explain())

# %% [markdown]
# again to help there are helper functions for each resource proxy such as `.list_supported_params()` `.describe_endpoint()`

# %%
print(studies.list_supported_params())
# or
print("\n----------\n")
print(studies.describe_endpoint())

# %% [markdown]
# ## 2. Resource `mgnipy.V2.proxies`
#
# Alternatively, many of the same functionalities are available from the resource proxies

# %%
from mgnipy.V2.proxies import Studies

# %%
chicken_studies = Studies(search="chicken")
print(chicken_studies.describe_endpoint())
print("\n----------\n")
print(chicken_studies.explain())

# %%

# %%
