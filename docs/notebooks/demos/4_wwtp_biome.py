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
#
# ```{margin}
# After clicking the "Activate Notebook" button you can run the cells in this browser. Alternatively, you can also click on the 🚀 to launch in colab or binder.
# ```
# <button title="Make live" style="display:inline-flex;align-items:center;gap:0.4rem;padding:0.5rem 1rem;border:0;border-radius:20px;background:linear-gradient(135deg,#0f766e,#14b8a6);color:white;cursor:pointer;font-size:1rem;" class="thebe-button" onclick="initThebeSBT()">Activate Notebook</button>
#
# ---

# %%
# uncomment if colab
# # !pip install mgnipy
# # !pip install plotly-express
# # !pip install anndata

# %% [markdown]
# ## `MGnipy`: Init session
#
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
# ## `MGnifier`: Build and execute queries
#
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


# %% tags=["hide-output"]
# taking a look at metdata so far 
wwtp_studies.metadata.to_pandas(expand_nested_dicts=True).head()

# %% [markdown]
# ## `MGazine`: Filtering and loading study datasets
#
# exploring the MGazine of datasets for the studies

# %%
# getting the magazine of datasets
MZ = wwtp_studies.datasets

# filtering to taxonomic of interest
filtered_MZ = MZ['Taxonomic assignments SSU']

# keeping latest pipeline version if multiple output files 
dedupe_downloads: list[dict] = (
    filtered_MZ.downloads_df()
    .sort_values(by='pipeline_version', ascending=False)
    .drop_duplicates(subset='accession', keep='first')
).to_dict(orient='records')
# assign back to the filtered_MZ object
filtered_MZ.downloads = dedupe_downloads

# with taxonomic helpers
taxo_mz = filtered_MZ.taxonomic

# %%
# lazy loading the datasets
taxo_mz.load()

# %% [markdown]
# ## `MGnetizer`: Collecting metadata from MGnify
#
# optionally we use MGnetizers to collect additional information from MGnify given accessions

# %% tags=["hide-output"]
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
studies_as_dict = {x['accession']: x for x in wwtp_studies.search_results.to_list()}

# passing the additional metadata to the Mgazine of taxonomic datasets
taxo_mz.mgnify_runs = mnet_run.metadata.to_list() + (
    # some cleaning of assembly metadata to match the run metadata format
    mnet_assembly.metadata.to_pandas()
    .dropna(how='all', axis=1)
    .rename(columns={'assembly_study_accession': 'study_accession'})
    .assign(study=lambda df: df['study_accession'].map(studies_as_dict))
).to_dict(orient='records')

# taking a look
taxo_mz.mgnify_runs.to_pandas(expand_nested_dicts=True).head()

# %% [markdown]
# ## `BioSampler`: Collecting metadata from BioSamples
#
# optionally can also use BioSampler helper to collect additional sample metadata from BioSamples

# %% tags=["hide-input"]
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
# ## `MGazine.to_anndata()`: Saving taxa count matrix with metadata
#
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
# In the above we curated a wastewater biome dataset using MGnify API v2.
#
# ---
#
# ## Bonus: Loading in the `AnnData` dataframe 
# as an example here we demo how to use the dataset in a new script:

# %%
import anndata as ad 

# read in data
back: ad.AnnData = ad.read_h5ad('wwtp_biome.h5ad')

print(back)

# %% [markdown]
# ### How to filter annotated df by obs (sample) metadata

# %%
# filtering out even more samples with no metadata
an_df_filt: ad.AnnData = back[back.obs['study_accession'] != 'None']

# now how many studies? 
print("Number of studies with sample metadata: ", an_df_filt.obs['study_accession'].nunique())

# %% [markdown]
# ### How to filter annotated df by var (taxa) metadata

# %%
# pruning var to species level
to_species: ad.AnnData = an_df_filt[:, an_df_filt.var['Species']!='NA']
# filtering out samples with no species level 
has_species_level_info: ad.AnnData = to_species[~to_species.to_df().isna().all(axis=1)]

# now how many studies? 
print("Number of studies with species level information: ", has_species_level_info.obs['study_accession'].nunique())

# %% [markdown]
# ### Adding more obs metadata columns

# %% tags=["hide-input"]
# demo adding an obs col with total counts
has_species_level_info.obs['total_counts'] = has_species_level_info.layers['filled_zeros'].sum(axis=1)

# filter obs to dedupe sample_accession
dedupe: ad.AnnData = has_species_level_info[
    has_species_level_info.obs
    .sort_values(by='total_counts', ascending=False)
    .drop_duplicates(subset='sample_accession', keep='first')
    .index
]

# expanding biome lineage into multi columns in obs 
biome_expanded = dedupe.obs['study__biome.lineage'].str.split(':', expand=True)
biome_expanded = biome_expanded.fillna('Wastewater')
biome_expanded.columns = [
    'biome_root', 'biome_level_1', 'biome_level_2', 'biome_level_3', 'biome_level_4'
]
dedupe.obs = dedupe.obs.merge(
    biome_expanded, left_index=True, right_index=True, how='left'
)

print("Number of samples after deduplication: ", dedupe.shape[0])
print("Number of studies after deduplication: ", dedupe.obs['study_accession'].nunique())

# %% [markdown]
# ### Plotting some obs metadata

# %% tags=["hide-input"]
import plotly.express as px

df = dedupe.obs["biome_level_3"].value_counts().reset_index()
df['pct'] = round(df['count']/sum(df['count'])*100, 1)
df['text'] = df['count'].astype(str) + ' (' + df['pct'].astype(str) + '%)'

fig = px.bar(
    df,
    y='biome_level_3',
    x='count',
    labels={"biome_level_3": "Sub-biome", "count": "Number of Samples"},
    title="Number of Samples by Sub-biome",
    orientation='h',
    template='plotly_white',
    text='text'  
)
fig.update_traces(marker_color='#191919')
fig.update_layout(showlegend=False)
