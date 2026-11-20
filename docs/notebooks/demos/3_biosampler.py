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
# # Add BioSamples metadata
#
# Using `mgnipy` we can also retrieve and integrate additional sample metadata from the [BioSamples](https://www.ebi.ac.uk/biosamples/) respository with the MGnify samples.
# <br><br>
#
# `mgnipy.collect.BioSampler()`
#
# BioSampler can take a list of Run or Sample ENA accessions and retrieve rich metadata from BioSamples for a list of Run or Sample ENA/BioSamples accessions.
#
# For this example we will get samples from MGnify using a `MGnifier`, passing the accessions to a `BioSampler` to get the BioSamples metadata.
#
# ```{margin}
# After clicking the "Activate Notebook" button you can run the cells in this browser. Alternatively, you can also click on the 🚀 to launch in colab or binder. 
# ```
# <button title="Make live" style="display:inline-flex;align-items:center;gap:0.4rem;padding:0.5rem 1rem;border:0;border-radius:20px;background:linear-gradient(135deg,#0f766e,#14b8a6);color:white;cursor:pointer;font-size:1rem;" class="thebe-button" onclick="initThebeSBT()">Activate Notebook</button>
#
# ---

# %%
# uncomment below if colab
# #!pip install mgnipy

# %% [markdown]
# ## First getting MGnify samples
#
# As done in the previous demo ["Finding sample details"](2_samples.ipynb), we'll start with initiating our MGnipy client with a cache, then building and executing our queries to the MGnify API.

# %%
from mgnipy import MGnipy

# init with cache
MG = MGnipy(cache_dir="temp_example")

# point to samples endpoint/get samples mgnifier
samples = MG.samples(search='cancer', page_size=5) # with search & pg sz params

# execute asynchronously 
async with MG:
    # get one page list of samples
    await samples.aget()
    # and if we want to get details for each sample in the list 
    await samples.aenrich_details()


# %% [markdown]
# we now have our list of sample accessions to pass to our BioSampler

# %%
# check it out
print(samples.metadata.ids)

# %% [markdown]
# ## Now the BioSampler
#
# we can access from our MGnipy client instance, which will also pass on our configuration such as the cache directory

# %%
# init biosampler from mgnipy client
bios = MG.biosampler(samples.metadata.ids)
# check it out
print(bios)


# %% [markdown]
# Now let's execute the requests to the BioSamples API

# %%
# execute asynchronously and with context manager
async with bios:
    await bios.aenrich(limit=None)


# %% [markdown]
# ## Merging metadata sets 
# we can merge the metadata as we would any pandas or polars dataframe

# %% tags=["hide-output"]
samples.metadata.to_polars(expand_nested_dicts=['metadata']).join(
    bios.metadata.to_polars(), 
    left_on="accession", 
    right_on="SampleID",
    how="left"
)



# %% [markdown]
# if wanting to cleanup the "temp_example" cache

# %%
#MG.clear_subcaches()
