# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: .venv (3.11.7.final.0)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Getting all Wastewater study datasets
#
# Here we demonstrate how `mgnipy` can be used to build a cross-study taxonomic dataset for a given biome with rich sample metadata from MGnify and BioSamples in a few lines of code. 

# %% [markdown]
# First starting the session with a MGnipy client

# %%
from mgnipy import MGnipy

# configure session 
MG = MGnipy(cache_dir='wwtp')

# selecting the studies resource
studies_resource = MG.studies

# helper to see accepted search params for endpoint
studies_resource.describe_endpoint()

# %% [markdown]
# now using mgnifier to build and then execute the query set

# %%
# preparing query set
wwtp_studies = studies_resource(biome_lineage='root:Engineered:Wastewater')
# helper to preview the query set prior to fetch
wwtp_studies.explain()


# %%
# now actually executing queries
async with MG: 
    # get all 8 pages of records from the list endpoint
    await wwtp_studies.aget_all()
    # enrich the records with study metadata from detail endpoint
    await wwtp_studies.aenrich_details()


# %%
# taking a look at metdata so far 
wwtp_studies.metadata.to_pandas(expand_nested_dicts=True).head()

# %% [markdown]
# exploring the MGazine of datasets for the studies

# %%
# getting the magazine of datasets
MZ = wwtp_studies.datasets
# filtering to taxonomic of interest
filtered_MZ = MZ['v4_1']['Taxonomic assignments SSU']
# with helpers 
taxo_mz = filtered_MZ.taxonomic 

# %%
# lazy loading the datasets
taxo_mz.load()

# %% [markdown]
# optionally we use MGnetizers to collect additional information from MGnify given accessions

# %%
# collecting run/assembly metadata for given accessions
run_accs = [x for x in taxo_mz.runs_accessions if not x.startswith('ERZ')]
assembly_accs = [x for x in taxo_mz.runs_accessions if x.startswith('ERZ')]
# init mgnetizer to collect 
mnet_run = MG.mgnetizer(resource='run', all_ids=run_accs)
mnet_assembly = MG.mgnetizer(resource='assembly', all_ids=assembly_accs)
# now executing the requests to the detail endpoints
async with MG: 
    await mnet_run.aenrich(limit=None)
    await mnet_assembly.aenrich(limit=None)


# %%
# passing the additional metadata to the Mgazine of taxonomic datasets
taxo_mz.mgnify_runs = mnet_run.metadata.to_list() + mnet_assembly.metadata.to_list()

# %% [markdown]
# optionally can also use BioSampler helper to collect additional sample metadata from BioSamples

# %%
# # the sample accessions to use
# sample_ids = taxo_mz.mgnify_runs.to_pandas()['sample_accession'].unique()
# # init biosampler to collect
# bios = MG.biosampler(sample_ids)
# # actually executing the requests
# async with MG: 
#     await bios.aenrich(limit=None)
# # passing the matadata back to MGazine
# taxo_mz.biosamples_metadata = bios.metadata.to_list(drop_duplicates=True)
# # taking a look 
# print(taxo_mz)

# %% [markdown]
# from the TaxaMGazine we can get an annotated dataframe with the observation metadata and taxonomic metadata (i.e., taxonomic ranks)

# %%
# convert to annotated dataframe
an_df = taxo_mz.to_anndata()
# demo adding a layer with filled in zeros 
an_df.layers['filled_zeros'] = an_df.to_df().fillna(0)
# exporting to h5ad file 
an_df.obs = an_df.obs.astype(str) #workaround for h5ad export issue with mixed types in obs
an_df.write_h5ad('wwtp_biome.h5ad')

# %% [markdown]
# as an example here we demo how to use the dataset in a new script:

# %%
import anndata as ad 
# read in data
back = ad.read_h5ad('wwtp_biome.h5ad')
# check it out
back
