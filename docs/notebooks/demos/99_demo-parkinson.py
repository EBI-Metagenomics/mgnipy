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
# # Part 1: Integrating Parkinson's disease cohorts
#
# In this notebook we demo the utility of `mgnipy` in curating cross-study datasets from MGnify for secondary analysis. 
#
# Specifically, we integrate the gut microbiome profiles of multiple Parkinson's disease vs. healthy control cohorts from various MGnify studies, relying on the sample metadata available on [MGnify](https://www.ebi.ac.uk/metagenomics/), [ENA](https://www.ebi.ac.uk/ena/browser/home) or [BioSamples](https://www.ebi.ac.uk/biosamples/) for the disease status label.  
#
# The mgnipy curated abundance dataset with metadata is then further preprocessed in Part 2.
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

# %% [markdown]
# ## Searching for studies using `MGnifier`
#
# To start we configure our MGnipy client and access the MGnify API Studies resource.
#
# We will filter our query to studies of the gut microbiome that mention "parkinson"s disease.
#
# We can preview the resulting query urls via `.explain()`

# %%
from mgnipy import MGnipy

# Initialize MGnipy with a cache directory
MG = MGnipy(cache_dir="downloads")

# Search for studies related to Parkinson's disease in the human gut microbiome
pd_studies = MG.studies(
    search="parkinson",
    biome_lineage="root:Host-associated:Human:Digestive system:Large intestine:Fecal",
)

# Show all of the request urls for the search i.e., the query set
pd_studies.explain()


# %% [markdown]
# looks good. we can proceed with actually executing the list query/queries via .get(). To enrich our list of studies with metadata details we can do this in bulk using `.enrich_details()` or asynchronously via `.aenrich_details()`

# %% tags=["hide-output"]
# as http client manager
async with MG:
    # populate study list
    await pd_studies.aget()
    # enrich study list with metadta
    await pd_studies.aenrich_details()

# can view as pandas or even save to file if you prefer
study_meta = pd_studies.metadata
# taking a look
study_meta.to_pandas(expand_nested_dicts=True)

# %% [markdown]
# Now that we found some studies that match our sesarch criteria, we can take a look at their datasets. 
#
# ---

# %% [markdown]
# ## Using `MGazine` to access the study datasets
#
# we can access the mgazine of datasets (kinda like a list of available datasets) via `.datasets` attribute. The study details we retrieved above will also be passed on to the mgazine

# %% tags=["hide-output"]
# access mgazine
MZ = pd_studies.datasets

# take a look
print(MZ)

# %% [markdown]
# Notice in "Nonempty metadata sets" we can see that the study details we collected [above](#searching-for-studies-using-mgnifier) are preserved in the mgazine. 
# ```{toggle}
# The `mgnify_studies` attribute is a `MGnifyMetadata` object so contains all the same methods for viewing e.g.: 
# - `MZ_SSU.mgnify_studies.to_pandas(expand_nested_dicts=True)`
# - `... .to_list()`
# - `... .to_polars()`
# - `... .records()`
# - etc.
#
# Later on in [Using MGnetizer to colllect more metadata](#using-mgnetizer-to-collect-more-metadata) we will assign additional sets of metadata to `.mgnify_runs` and `.biosamples_metadata` which will also convert the lists of records into a MGnifyMetadata object
# ```
#
# ### Filtering the dataset list
#
# We can filter by the pipeline version and short descriptions of the datasets. 
#
# For the ABaCo demo we will use the taxonomic analyses and we will use v4 onwards due to differences in pipeline versions and specifically SILVA databases that were used for the taxonomic analysis
#

# %% tags=["hide-output"]
# we can filter by passing as index
V3 = MZ["Taxonomic assignments"]
V4_5 = MZ["Taxonomic assignments SSU"]
V6 = MZ["Summary of SILVA-SSU taxonomies"]

print(V3, V4_5, V6)

# %% [markdown]
# ### Combining dataset lists

# %% tags=["hide-output"]
# can add magazines
MZ_SSU = V3 + V4_5 + V6

# keeping latest pipeline version if multiple output files 
dedupe_downloads: list[dict] = (
    MZ_SSU.downloads_df()
    .sort_values(by='pipeline_version', ascending=False)
    .drop_duplicates(subset='accession', keep='first')
).to_dict(orient='records')

MZ_SSU.downloads = dedupe_downloads
# print still works
print(MZ_SSU)

# %% [markdown]
# Now that we have filtered our list of datasets a bit, let's actually get and merge the taxonomic datasets. 
#
# ---
#
# ### (Lazy)loading into one taxonomic dataset
#
# Currently availble in mgnipy are special MGazines for handling taxonomic assignment datasets in the classic taxa x sample/run format `TaxaMGazine` or in Darwin core-ready format `DWCTaxaMGazine`
#
# we can also access these from an existing MGazine instance via `.taxonomic` or `.taxonomic_dwc_ready`

# %% tags=["hide-output"]
taxo = MZ_SSU.taxonomic

# %% [markdown]
# now `load` where the datasets will be merged as `polars.LazyFrame`

# %% tags=["hide-output"]
# lazyload the mgnify taxanomic assignments datasets
taxo.load()

# calling to_pandas or to_polars will collect the data and return a dataframe
taxo.to_pandas().head()

# %% [markdown]
# additionally there is a method `.taxonomic_metadata()` that parses "taxonomy" into the taxonomic ranks, returning as pandas or polars dataframe which is configured via arg `df_engine=`. The default is pandas.

# %% [markdown]
# also any run and sample metadata relevant to the observations (i.e., by run accessions) can be merged and viewed using `.obs_metadata()` again as polars or pandas dataframes. As we know metadata() for the observations in the taxonomic mgazine is not available:

# %% tags=["hide-output"]
# see first 5 sample's metadata
display(taxo.obs_metadata().head())

# recall the "Nonempty metadata set:"
print(taxo)

# %% [markdown]
# if we recall [from earlier](#using-mgazine-to-access-the-study-datasets) and again in the print statement, we only had `.mgnify_studies` enriched. 
#
# We still need to enrich with run and/or sample metadata, which we will do next :) 
#
# ---

# %% [markdown]
# ## Using `MGnetizer` to collect more metadata
#
# MGnetizer is designed to retrieve the rich metadata from MGnify for a given list of MGnify accessions/ids.
#
# First we get the ids to pass on 

# %%
# separate run and assembly ids
runs_ids: list[str] = [x for x in taxo.runs_accessions if not x.startswith('ERZ')]
assembly_ids: list[str] = [x for x in taxo.runs_accessions if x.startswith('ERZ')]
print(f"Runs: {len(runs_ids)}")
print(f"Assemblies: {len(assembly_ids)}")

# %% [markdown]
# Now we will instantiate the MGnetizers and pass the accessions/ids. 

# %%
# initialize mgnetizer for runs and assemblies
mnet_run = MG.mgnetizer(resource="run", all_ids=runs_ids)
mnet_acc = MG.mgnetizer(resource="assembly", all_ids=assembly_ids)

# now making the API calls with context manager
async with MG:
    await mnet_run.aenrich(limit=None)
    await mnet_acc.aenrich(limit=None)


# %% [markdown]
# `.metadata` attribute of MGnetizer returns a `MGnifyMetadata` object just like with the MGnifiers. the MGnifyMetadata's can be combined:

# %%
# we can combine the metadata from both runs and assemblies into one MGnifyMetadata
run_metadata = mnet_run.metadata + mnet_acc.metadata

# %% [markdown]
# if wanting to do some cleaning, do so (which below I do as a pandas df) and then convert back to list of dicts for the MGazine `.mgnify_run` property.

# %% tags=["hide-input"]
# cleaning up metadata
df_run = run_metadata.to_pandas()
# fill in missing study_accession
df_run["study_accession"] = df_run["study_accession"].fillna(
    df_run["assembly_study_accession"]
)
# keep pipeline_version
df_run = df_run.merge(
    (
        taxo.downloads_df()[['accession', 'pipeline_version']]
        .rename(columns={"accession": "study_accession_temp"})
    ),
    how='left',
    left_on='study_accession',
    right_on='study_accession_temp'
)
# drop assembly_study_accession column and any columns that are all NaN
df_run = df_run.drop(columns=["assembly_study_accession", "study_accession_temp"])
df_run = df_run.dropna(axis=1, how="all")

# %% [markdown]
# Now can pass tidied metadata back to our MGazine of taxonomic data:

# %% tags=["hide-output"]
# now back to TaxaMGazine instance as list of records
taxo.mgnify_runs = df_run.to_dict(orient="records")

# and now
print(taxo)

# also the metadata is updated
taxo.obs_metadata().info()

# %% [markdown]
# However, the available run/sample metadata is not consistent for all e.g. sample__sample_title which has lots missing. We can try to get additional sample metadata from the BioSamples database. 
#
# ---
#
# ## Collecting even more sample metadata using `BioSampler`
# BioSampler is designed to retrieve the rich sample metadata from BioSamples for a list of Run or Sample ENA accessions.
#
#
# we again start from the mgnipy instance to automatically pass on the configuration 

# %%
# getting list of sample ids to go to BioSamples
sample_ids = taxo.mgnify_runs.to_pandas()["sample_accession"].to_list()

# init biosampler
bios = MG.biosampler(sample_ids=sample_ids)

# now making the API calls with context manager
async with bios:
    await bios.aenrich(limit=None, incl_ena=False)


# %% [markdown]
# again we can pass this metadata as list of records to the MGazine instance to `.biosamples_metadata` for merging:

# %%
# assign the biosamples metadata to the taxo object
taxo.biosamples_metadata = bios.metadata.to_list(drop_duplicates=True)
# now can see the additional metadata set
print(taxo)

# %% [markdown]
# and now if we were to look at the observations metadata `.obs_metadata()` there is even more info. 
#
# ---

# %% [markdown]
# ## Finding disease label in sample (obs) metadata 
#
# inspecting the metadata we found disease status distrbuted between the following columns, which we normalise into a new label column `has_parkinsons_disease` with `Y` and `N`
#
# samples for which disease status could not be identified from the metadata are then excluded.

# %% tags=["hide-input"]
disease_status_columns = {
    "host_phenotype": {
        "Y": ["Parkinson's Disease"], 
        "N": ["Healthy Control"]
    },
    "host disease status": {
        "Y": ["Parkinson's disease", "Parkinson's Disease [DOID:14330]"],
        "N": ["healthy control", "Healthy [NCIT:C115935]"],
    },
    "parkinson": {
        "Y": ["yes"], 
        "N": ["no"]
    },
    "Case_status": {
        "Y": ["PD"], 
        "N": ["Control"]
    },
    "disease status": {
        "Y": ["Parkinson's disease"], 
        "N": ["Not"]
    },#MGYS00001650
}

# # copy the metadata to a new dataframe to work with
df_obs = taxo.obs_metadata().copy()
#for MGYS00001650
df_obs.loc[
    (
        (df_obs['study_accession']== 'MGYS00001650') & 
        (df_obs['disease status'].isna())
    ), 
    'disease status'
] = "Not"

# filter out samples with no disease status metadata
df_obs_filt = df_obs[df_obs[disease_status_columns.keys()].notna().any(axis=1)].copy()
print(f"Filtered down to {len(df_obs_filt)} samples with disease status metadata.")

# create a new column to indicate if the sample has Parkinson's disease or not
df_obs_filt["has_parkinsons_disease"] = None
for col in disease_status_columns:
    df_obs_filt[col] = df_obs_filt[col].map(
        lambda x: (
            "Y"
            if x in disease_status_columns[col]["Y"]
            else ("N" if x in disease_status_columns[col]["N"] else None)
        )
    )

# new col
df_obs_filt["has_parkinsons_disease"] = df_obs_filt.loc[
    :, disease_status_columns.keys()
].apply(
    lambda x: "Y" if "Y" in x.values else ("N" if "N" in x.values else None), axis=1
)
print(
    f"PD samples: {len(df_obs_filt[df_obs_filt['has_parkinsons_disease'] == 'Y'])}, Non-PD samples: {len(df_obs_filt[df_obs_filt['has_parkinsons_disease'] == 'N'])}"
)

# list of studies
filt_studies = df_obs_filt["study_accession"].unique()
print(f"Studies: {filt_studies}")

# %% [markdown]
# We will only include the studies with samples with disease status metadata and will move on with this demonstration. 
#
# Also using `.obs` we can assign our cleaned metadata set which will be given priority over the other sets:

# %%
# filter datasets in mgazine to the filtered studies
taxo.downloads = [x for x in taxo.downloads if x['accession'] in filt_studies]
# also add on the observation metadata that we had prepared just before
taxo.obs = df_obs_filt.reset_index().to_dict(orient="records")
print(taxo)

# %% [markdown]
# then the TaxaMGazine can handle the rest and we can export `to_anndata()` if we want

# %%
ad_tax = taxo.to_anndata()
ad_tax

# %% [markdown]
# Using MGni.py we could find Parkinson's disease cohorts and integrate their abundance tables along with sample metadata from MGnify and BioSamples.
#
# In Part 2 we further pre-process the data including cleaning and normalising the taxonomic matrix, followed by [ABaCo](https://mona-abaco.readthedocs.io/en/latest/tutorial/demo-parkinson.html) for batch correction between the studies. 

# %%
# exporting to h5ad file 
ad_tax.obs = ad_tax.obs.astype(str) #workaround for h5ad export issue with mixed types in obs
ad_tax.write_h5ad('pd.h5ad')
