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
# # Combining Parkinson's disease taxonomic analyses
#
# In this notebook we aim to imitate the analyses in ["`ABaCo` demo: Parkinson’s disease gut microbiome"](https://mona-abaco.readthedocs.io/en/latest/tutorial/demo-parkinson.html) where the aim was to "integrate the 9 studies while preserving key distinctions from the two patient states (Parkinson’s v.s. Healthy)."
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
# ## Curating the taxonomic datasets with metadata
#
# ### Searching for studies using `MGnifier`
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
# ### Using `MGazine` to access the study datasets
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
# #### Filtering the dataset list
#
# We can filter by the pipeline version and short descriptions of the datasets. 
#
# For the ABaCo demo we will use the taxonomic analyses and we will use v4 onwards due to differences in pipeline versions and specifically SILVA databases that were used for the taxonomic analysis
#

# %% tags=["hide-output"]
# we can filter by passing as index
V5 = MZ["v5"]["Taxonomic assignments SSU"]
V6 = MZ["Summary of SILVA-SSU taxonomies"]

print(V5, V6)

# %% [markdown]
# #### Combining dataset lists

# %% tags=["hide-output"]
# can add magazines
MZ_SSU = V5 + V6

# print still works
print(MZ_SSU)

# %% [markdown]
# Now that we have filtered our list of datasets a bit, let's actually get and merge the taxonomic datasets. 
#
# ---
#
# #### (Lazy)loading into one taxonomic dataset
#
# Currently availble in mgnipy are special MGazines for handling taxonomic assignment datasets in the classic taxa x sample/run format `TaxaMGazine` or in Darwin core-ready format `DWCTaxaMGazine`
#
# we can also access these from an existing MGazine instance via `.taxonomic` or `.taxonomic_dwc_ready`

# %%
taxo = MZ_SSU.taxonomic

# %% [markdown]
# now we can load the datasets as `polars.LazyFrame`

# %% tags=["hide-output"]
# lazyload the mgnify taxanomic assignments datasets
taxo.load()

# calling to_pandas or to_polars will collect the data and return a dataframe
taxo.to_pandas().head()

# %% [markdown]
# additionally there is a method `.taxonomic_metadata()` that parses "taxonomy" into the taxonomic ranks, returning as pandas or polars dataframe which is configured via arg `df_engine=`. The default is pandas.

# %% [markdown]
# also any run and sample metadata relevant to the observations (i.e., by run accessions) can be merged and viewed using `.obs_metadata()` again as polars or pandas dataframes. As we know metadata() for the observations in the taxonomic mgazine is not available:

# %%
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
# ### Using `MGnetizer` to collect more metadata
#
# MGnetizer is designed to retrieve the rich metadata from MGnify for a given list of MGnify accessions/ids.
#
# First we get the ids to pass on 

# %%
# separate run and assembly ids
runs_ids = [
    x for x in taxo.runs_accessions if x.startswith("ERR") or x.startswith("SRR")
]
assembly_ids = [x for x in taxo.runs_accessions if x.startswith("ERZ")]
print(f"Runs: {len(runs_ids)}")
print(f"Assembly: {len(assembly_ids)}")

# %% [markdown]
# Now we will instantiate the MGnetizers and pass the accessions/ids. 

# %%
# initialize mgnetizer for runs and assemblies
mnet_run = MG.mgnetizer(resource="run", all_ids=runs_ids)
mnet_acc = MG.mgnetizer(resource="assembly", all_ids=assembly_ids)
print(mnet_run, mnet_acc)


# %%
# now making the API calls with context manager
async with MG:
    await mnet_run.aenrich(limit=None)
    await mnet_acc.aenrich(limit=None)


# %% tags=["hide-output"]
# we can combine the metadata from both runs and assemblies into one MGnifyMetadata
run_metadata = mnet_run.metadata + mnet_acc.metadata

# like any other MGnifyMetdata obj we can view as list, pd, pl
run_metadata.to_pandas().head()

# %% [markdown]
# if wanting to do some cleaning, do so and then save back to `.data`
#
# below I clean as a pandas dataframe and then convert back to list of dicts for the MGazine

# %%
df_run = run_metadata.to_pandas()
df_run["study_accession"] = df_run["study_accession"].fillna(
    df_run["assembly_study_accession"]
)
df_run = df_run.drop(columns=["assembly_study_accession"])

# %% [markdown]
# Optionally we can pass this metadata back to a MGazine to help with dataset curation:

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
# ### Collecting even more sample metadata using `BioSampler`
# BioSampler is designed to retrieve the rich sample metadata from BioSamples for a list of Run or Sample ENA accessions.
#
#
# we again start from the mgnipy instance to automatically pass on the configuration 

# %%
# getting list of sample ids to go to BioSamples
sample_ids = taxo.mgnify_runs.to_pandas()["sample_accession"].to_list()

bios = MG.biosampler(sample_ids=sample_ids)

print(bios)

# %%
with bios:
    await bios.aenrich(limit=None, incl_ena=False)

# %% [markdown]
# and we can also pass this metadata to the TaxaMGazine instance to `.biosamples_metadata` for merging:

# %%
taxo.biosamples_metadata = bios.metadata.to_list(drop_duplicates=True)
print(taxo)

# %% [markdown]
# and now if we look at the observations metadata we have even more possible annotations

# %% tags=["hide-output"]
taxo.obs_metadata().info()

# %% [markdown]
# ### Data cleaning based on sample (obs) metadata 
#
# inspecting the metadata we found disease status distrbuted between the following columns: 

# %% tags=["hide-input"]
disease_status_columns = {
    "host_phenotype": {"Y": ["Parkinson's Disease"], "N": ["Healthy Control"]},
    "host disease status": {
        "Y": ["Parkinson's disease", "Parkinson's Disease [DOID:14330]"],
        "N": ["healthy control", "Healthy [NCIT:C115935]"],
    },
    "parkinson": {"Y": ["yes"], "N": ["no"]},
    "Case_status": {"Y": ["PD"], "N": ["Control"]},
}

# filter out samples with no disease status metadata
df_obs = taxo.obs_metadata().copy()
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
# One way we can go about filtering our taxonomic datasets is repeating the above steps but starting with MGnetizer instead of searching Studies resource with MGnifier:

# %%
# collect the studies metadata and datasets for the filtered studies
new_mnet = MG.mgnetizer(resource="study", all_ids=filt_studies)
with MG:
    new_mnet.enrich()

# accessing datasets of the filtered studies
new_mz = new_mnet.datasets
V5 = new_mz["v5"]["Taxonomic assignments SSU"]
V6 = new_mz["Summary of SILVA-SSU taxonomies"]

# filter datasets to taxonomic 
new_new_mz = V5 + V6
new_taxo = new_new_mz.taxonomic
new_taxo.load()

# also add on the observation metadata that we had prepared just before
new_taxo.obs = df_obs_filt.reset_index().to_dict(orient="records")

# %% [markdown]
# and the TaxaMGazine can handle the rest and we can export to_anndata() if we want

# %%
ad_tax = new_taxo.to_anndata()
ad_tax

# %% [markdown]
# okay thanks for the help mgnipy and thank you MGnify for the analyses and metadata! From here out we further pre-process the data including cleaning and normalising the taxonomic matrix, followed by ABaCo for batch correction between the studies. 

# %% [markdown]
# ## Preprocessing the counts
#
# and we will agglomerate to Genus level

# %%
import numpy as np
import scanpy as sc

from mgnipy._models.constants.tax_ranks import SILVA_TAX_RANKS

# quick cleaning
# add filled na layer
ad_tax.layers["filled_na"] = ad_tax.to_df().fillna(0)
# drop samples if library count is less than median
ad_filt = ad_tax[
    ad_tax.to_df(layer="filled_na").sum(axis=1)
    >= ad_tax.to_df(layer="filled_na").sum(axis=1).median()
]
# calc total counts per sample
total_counts = ad_filt.layers["filled_na"].sum(axis=1)
# agglom to genus level (pruning then agg)
pruned = ad_filt[:, ((ad_filt.var["Genus"] != "NA") & (ad_filt.var["Species"] != "NA"))]
# to avoid memory issues..
pruned.var["ranks_to_genus"] = pruned.var[SILVA_TAX_RANKS[:-1]].agg(";".join, axis=1)
# agg with scanpy
ad_genus = sc.get.aggregate(
    pruned,
    by="ranks_to_genus",
    func="sum",
    axis="var",
    layer="filled_na",
)
# getting the relabund
ad_genus.layers["total_counts"] = np.array([total_counts] * ad_genus.n_vars).T
ad_genus.layers["rel_abund"] = ad_genus.layers["sum"] / ad_genus.layers["total_counts"]
# prevalence threshold of 10%
ad_genus_filt = ad_genus[
    :, (ad_genus.to_df(layer="sum") > 0).sum(axis=0) >= (ad_genus.n_vars * 0.1)
]
ad_genus_filt.to_df(layer="sum")

# %%
ad_filt.obs["total_counts"] = ad_filt.layers["filled_na"].sum(axis=1)

this = (
    ad_filt.obs[["has_parkinsons_disease", "study_accession", "total_counts"]]
    .merge(ad_filt.to_df(layer="filled_na"), left_index=True, right_index=True)
    .reset_index()
)
this

# %%
ad_genus.obs[["has_parkinsons_disease", "study_accession"]].merge(
    ad_genus_filt.to_df(layer="sum"), left_index=True, right_index=True
).reset_index().to_csv("pd_gut_genus.csv", index=False)

# %% [markdown]
# ## Batch correction with `ABaCo`
#
# the below code is from [their demo notebook](https://mona-abaco.readthedocs.io/en/latest/tutorial/demo-parkinson.html)

# %% tags=["hide-input", "hide-output"]
from abaco.dataloader import DataPreprocess

# Load Parkinson's disease dataset
path_to_dataset = "pd_gut_genus.csv"
batch_col = "study_accession"
bio_col = "has_parkinsons_disease"
id_col = "_mgnipy_runs_accs"

# Convert data path into compatible pd.DataFrame
df_parkinson = DataPreprocess(
    path_to_dataset, factors=[id_col, batch_col, bio_col]
).dropna()

# see if there are 3 categorical and n numeric columns (should be an extra column for location)
df_parkinson.info()

# %% tags=["hide-input"]
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Ellipse
from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy.spatial.distance import pdist, squareform
from skbio.stats.distance import DistanceMatrix, permanova
from skbio.stats.ordination import pcoa
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


# Auxiliary
def permanova_ait(df, sample_label, group_label):
    samples = df[sample_label].values
    groups = df[group_label].values
    clr_data = df.select_dtypes(include="number").values

    aitch = pdist(clr_data, metric="euclidean")
    dist_mat = squareform(aitch)
    dm = DistanceMatrix(dist_mat, ids=samples)

    res_ait = permanova(distance_matrix=dm, grouping=groups)

    res_ait["R2"] = (
        res_ait["test statistic"]
        * (len(np.unique(groups)) - 1)
        / (
            res_ait["test statistic"] * (len(np.unique(groups)) - 1)
            + (len(samples) - len(np.unique(groups)))
        )
    )
    return res_ait


def pcoa_aitchison(df, sample_label, batch_label, bio_label):
    df_otu = df.select_dtypes(include="number")
    dist = pdist(df_otu, "euclidean")
    dist = squareform(dist)

    pcoa_res = pcoa(dist)
    explained = (pcoa_res.proportion_explained * 100).round(1)
    explained_dict = {"PC1": explained[0], "PC2": explained[1]}
    df_pcoa = pd.DataFrame(pcoa_res.samples[["PC1", "PC2"]], columns=["PC1", "PC2"])
    df_pcoa.index = df.index
    df_pcoa[[sample_label, batch_label, bio_label]] = df[
        [sample_label, batch_label, bio_label]
    ]
    return df_pcoa, explained_dict


def plot_pcoa_2(
    df_pcoa,
    group_col,
    df,
    sample_label,
    ax,
    explained,
    palette=None,
    xlim=None,
    ylim=None,
    marginal_size="20%",  # size of marginals relative to main
    marginal_pad=0.1,  # padding between main and marginals
    kde_bw_adjust=1.0,  # bandwidth scaling for KDE
    alpha_kde=0.5,  # fill transparency for KDE areas
    title=None,  # optional title above the top density plot
    show_legend=True,  # whether to draw the legend
):
    # compute PERMANOVA R2
    perma_r2 = permanova_ait(df, sample_label, group_col)["R2"]

    # set up axes divider for marginals
    divider = make_axes_locatable(ax)
    ax_top = divider.append_axes("top", size=marginal_size, pad=marginal_pad, sharex=ax)
    ax_right = divider.append_axes(
        "right", size=marginal_size, pad=marginal_pad, sharey=ax
    )

    # hide the marginal axes completely (no ticks, no spines)
    ax_top.axis("off")
    ax_right.axis("off")

    groups = df_pcoa[group_col].unique()
    colors = palette or plt.cm.tab10.colors

    handles = []
    labels = []

    for i, grp in enumerate(groups):
        sub = df_pcoa[df_pcoa[group_col] == grp]
        x = sub["PC1"].values
        y = sub["PC2"].values
        c = colors[i % len(colors)]

        # main scatter
        pts = ax.scatter(x, y, label=str(grp), alpha=0.7, color=c)
        handles.append(pts)
        labels.append(str(grp))

        # marginal KDEs (axes are off so only the filled area shows)
        sns.kdeplot(
            x=x,
            ax=ax_top,
            bw_adjust=kde_bw_adjust,
            fill=True,
            alpha=alpha_kde,
            color=c,
            linewidth=1.5,
        )
        sns.kdeplot(
            y=y,
            ax=ax_right,
            bw_adjust=kde_bw_adjust,
            fill=True,
            alpha=alpha_kde,
            color=c,
            linewidth=1.5,
        )

        # 95% confidence ellipse
        cov = np.cov(x, y)
        vals, vecs = np.linalg.eigh(cov)
        width, height = 2 * np.sqrt(vals * 5.991)
        angle = np.degrees(np.arctan2(*vecs[:, 0][::-1]))
        ell = Ellipse(
            xy=(x.mean(), y.mean()),
            width=width,
            height=height,
            angle=angle,
            edgecolor=c,
            facecolor="none",
            lw=2,
        )
        ax.add_patch(ell)

    # add title above the top density plot
    if title:
        ax_top.set_title(title, pad=10, fontsize=16)

    # optionally draw legend on top density axis
    if show_legend:
        ax_top.legend(
            handles,
            labels,
            title=group_col,
            bbox_to_anchor=(1.02, 1),
            loc="upper left",
            frameon=False,
            fontsize=14,
            title_fontsize=16,
        )

    # main axis formatting
    ax.set_xlabel(f"PC1 ({explained['PC1']:.1f}%)", fontsize=12)
    ax.set_ylabel(f"PC2 ({explained['PC2']:.1f}%)", fontsize=12)
    ax.text(
        0.99,
        0.99,
        f"PERMANOVA R² ({group_col}): {perma_r2:.3f}",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize="small",
    )
    ax.set_aspect("equal")

    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)


# %% tags=["hide-input"]
# Define figure
from abaco.dataloader import DataTransform

sns.set_style("whitegrid")
fig = plt.figure(figsize=(24, 16))
fig.suptitle("", fontsize=16, y=0.97)

gs = GridSpec(2, 1, figure=fig, wspace=0.4, hspace=0.3)

top_palette = sns.color_palette("tab10", n_colors=9)
bottom_palette = sns.color_palette("tab10", n_colors=10)[::-1][:9]

ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[1, 0])

data_clr = DataTransform(df_parkinson, factors=[id_col, batch_col, bio_col], count=True)

data_pcoa, data_exp = pcoa_aitchison(
    data_clr, sample_label=id_col, batch_label=batch_col, bio_label=bio_col
)

plot_pcoa_2(
    data_pcoa,
    group_col=batch_col,
    df=data_clr,
    sample_label=id_col,
    ax=ax1,
    explained=data_exp,
    palette=top_palette,
    title="Aitchison PCoA - Colored by Study",
    show_legend=False,
)

handles, labels = ax1.get_legend_handles_labels()

fig.legend(
    handles,
    labels,
    title="Batch",
    loc="upper right",
    frameon=False,
    bbox_to_anchor=(0.8, 0.82),
    fontsize=12,
    title_fontsize=12,
)

plot_pcoa_2(
    data_pcoa,
    group_col=bio_col,
    df=data_clr,
    sample_label=id_col,
    ax=ax2,
    explained=data_exp,
    palette=bottom_palette,
    title="Aitchison PCoA - Colored by Phenotype",
    show_legend=False,
)

handles, labels = ax2.get_legend_handles_labels()

fig.legend(
    handles,
    labels,
    title="Phenotype",
    loc="upper right",
    frameon=False,
    bbox_to_anchor=(0.78, 0.37),
    fontsize=12,
    title_fontsize=12,
)

fig.subplots_adjust(right=0.85)

plt.show()

# %%
from abaco.ABaCo import metaABaCo
import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Create ABaCo model
abaco_model = metaABaCo(
    data=df_parkinson,
    n_bios=2,
    bio_label=bio_col,
    n_batches=4,
    batch_label=batch_col,
    n_features=df_parkinson.select_dtypes(include="number").shape[1],
    # prior="VMM",
    device=device,
    epochs=[1000, 2000, 1000],
)

abaco_model.fit(
    seed=42,
    w_cluster_penalty=0.1,  # 0.1
    phase_1_vae_lr=1e-3,  # 1e-3
    phase_2_vae_lr=1e-3,  # 1e-3
    phase_3_vae_lr=1e-7,  # 1e-7
    adv_lr=1e-4,  # 1e-4
    disc_lr=1e-4,
)  # 1e-4

# %% tags=["hide-input"]
# Reconstruct the dataset using the trained ABaCo model
corrected_dataset = abaco_model.correct(seed=42)

sns.set_style("whitegrid")
fig = plt.figure(figsize=(24, 16))
fig.suptitle("", fontsize=16, y=0.97)

gs = GridSpec(2, 1, figure=fig, wspace=0.4, hspace=0.3)

top_palette = sns.color_palette("tab10", n_colors=9)
bottom_palette = sns.color_palette("tab10", n_colors=10)[::-1][:9]

ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[1, 0])

corrected_data_clr = DataTransform(
    corrected_dataset, factors=[id_col, batch_col, bio_col], count=True
)

data_pcoa, data_exp = pcoa_aitchison(
    corrected_data_clr, sample_label=id_col, batch_label=batch_col, bio_label=bio_col
)

plot_pcoa_2(
    data_pcoa,
    group_col=batch_col,
    df=corrected_data_clr,
    sample_label=id_col,
    ax=ax1,
    explained=data_exp,
    palette=top_palette,
    title="Aitchison PCoA - Colored by Study",
    show_legend=False,
)

handles, labels = ax1.get_legend_handles_labels()

fig.legend(
    handles,
    labels,
    title="Batch",
    loc="upper right",
    frameon=False,
    bbox_to_anchor=(0.77, 0.82),
    fontsize=12,
    title_fontsize=12,
)

plot_pcoa_2(
    data_pcoa,
    group_col=bio_col,
    df=corrected_data_clr,
    sample_label=id_col,
    ax=ax2,
    explained=data_exp,
    palette=bottom_palette,
    title="Aitchison PCoA - Colored by Phenotype",
    show_legend=False,
)

handles, labels = ax2.get_legend_handles_labels()

fig.legend(
    handles,
    labels,
    title="Phenotype",
    loc="upper right",
    frameon=False,
    bbox_to_anchor=(0.745, 0.37),
    fontsize=12,
    title_fontsize=12,
)

fig.subplots_adjust(right=0.85)

plt.show()

# %%
import abaco.metrics as metrics

print("kBET results before batch correction:")
print(metrics.kBET(data_clr, batch_col))
print("\niLISI results before batch correction:")
print(metrics.iLISI_norm(data_clr, batch_col))
print("\nbatch ASW results before batch correction:")
print(1 - metrics.ASW(data_clr, batch_col))
print("\nbatch ARI results before batch correction:")
print(1 - metrics.ARI(data_clr, batch_col))

print("\n\nkBET results after batch correction:")
print(metrics.kBET(corrected_data_clr, batch_col))
print("\niLISI results after batch correction:")
print(metrics.iLISI_norm(corrected_data_clr, batch_col))
print("\nbatch ASW results after batch correction:")
print(1 - metrics.ASW(corrected_data_clr, batch_col))
print("\nbatch ARI results after batch correction:")
print(1 - metrics.ARI(corrected_data_clr, batch_col))

# %% [markdown]
# batch corrected. 
#
# ---
#
# # TODO

# %% [markdown]
# working with the corrected dataset
#
# as anndata

# %%
from skbio.stats.composition import clr
import anndata as ad

adata = ad.AnnData(corrected_dataset.iloc[:, 3:], obs=corrected_dataset.iloc[:, :3])
adata.layers["totals"] = np.array([adata.to_df().sum(axis=1)] * adata.n_vars).T
adata.layers["normalized_X"] = adata.to_df() / adata.layers["totals"]
adata.layers["clr_X"] = clr(
    np.where(adata.layers["normalized_X"] > 0, adata.layers["normalized_X"], 1e-10)
)

# %%
# Diversity: Number of unique taxa per sample as new metadata
adata.obs["X_numtaxa"] = (adata.X > 0).sum(axis=1)

# Diversity with correction: Chao1 estimator
# Chao1 = num observed taxa + (num singletons / (2 x num doubletons))
num_singletons = (adata.X == 1).sum(axis=1)
num_doubletons = (adata.X == 2).sum(axis=1)
adata.obs["X_chao1"] = (adata.X > 0).sum(axis=1) + (
    num_singletons / (2 * num_doubletons)
)

# Diversity: Shannon index H = -sum(p_i * log(p_i)), entropy
from scipy.stats import entropy

adata.obs["X_shannon"] = entropy(
    adata.layers["normalized_X"], nan_policy="omit", axis=1
)

# Evenness: Pielou evenness index P = H/H_max, H_max = ln(num species)
adata.obs["X_pielou"] = adata.obs["X_shannon"] / np.log(adata.obs["X_numtaxa"])

# Diversity: simpson index lambda = sum(p_i ^2)
adata.obs["X_simpson"] = (adata.layers["normalized_X"] ** 2).sum(axis=1)

# Diversity: inverse simpson index D = 1/lambda
adata.obs["X_inv_simpson"] = 1 / adata.obs["X_simpson"]

# %%
import seaborn as sns
import matplotlib.pyplot as plt

# preparing the df for vis
df_alphas = adata.obs[
    [
        "X_numtaxa",
        "X_chao1",
        "X_shannon",
        "X_pielou",
        "X_simpson",
        "X_inv_simpson",
        batch_col,
        bio_col,
    ]
].copy()

# plotting by bio groups
g1 = sns.pairplot(df_alphas, hue=bio_col, corner=True, height=1.8)
g1.figure.suptitle("Alpha Diversity by Biological Groups", fontsize=22)
plt.setp(g1._legend.get_texts(), fontsize=18)
plt.setp(g1._legend.get_title(), fontsize=20)

g2 = sns.pairplot(df_alphas, hue=batch_col, corner=True, height=1.8)
g2.figure.suptitle("Alpha Diversity by Batch Groups", fontsize=22)
plt.setp(g2._legend.get_texts(), fontsize=18)
plt.setp(g2._legend.get_title(), fontsize=20)

# %%
adata.obs.groupby("has_parkinsons_disease")[
    ["X_numtaxa", "X_chao1", "X_shannon", "X_pielou", "X_simpson", "X_inv_simpson"]
].mean()

# %%
oj = taxo.obs_metadata()

oj[oj["sample_accession"] == "SAMN28061739"][disease_status_columns.keys()]

# %%
new_taxo.mgnify_studies.ids
