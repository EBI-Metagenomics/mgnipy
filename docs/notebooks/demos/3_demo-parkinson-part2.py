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
# # Part 2: Integrating Parkinson's disease cohorts
#
# This notebook is a continuation of demoing the utility of `mgnipy` in curating cross-study datasets from MGnify for secondary analysis. 
#
# Here we further preprocess the curated dataset we obtained from Part 1. Specifically we preprocess the count data and then use `ABaCo` for batch/technical variance correction, following [their PD demo](https://mona-abaco.readthedocs.io/en/latest/tutorial/demo-parkinson.html)
#
# Using abaco we aim to mitigate the technical variance across the 6 MGnify studies.
#
# ```{margin}
# After clicking the "Activate Notebook" button you can run the cells in this browser. Alternatively, you can also click on the 🚀 to launch in colab or binder.
# ```
# <button title="Make live" style="display:inline-flex;align-items:center;gap:0.4rem;padding:0.5rem 1rem;border:0;border-radius:20px;background:linear-gradient(135deg,#0f766e,#14b8a6);color:white;cursor:pointer;font-size:1rem;" class="thebe-button" onclick="initThebeSBT()">Activate Notebook</button>
#
# ---

# %%
# uncomment below if colab
# # !pip install abaco
# # !pip install anndata
# # !pip install scanpy
# # !pip install skbio

# %% [markdown]
# ## Loading the dataset from Part 1

# %%
import anndata as ad
import httpx
from io import BytesIO

url = "https://github.com/EBI-Metagenomics/mgnipy/raw/refs/heads/main/docs/notebooks/demos/pd.h5ad"
r = httpx.get(url, follow_redirects=True)
r.raise_for_status()

# read in
ad_tax = ad.read_h5ad(
    BytesIO(r.content)#'pd.h5ad'
)
# check it out
ad_tax

# %% [markdown]
# ## Preprocessing the counts
#
# and we will agglomerate to Genus level

# %% tags=["hide-input"]
import numpy as np
import scanpy as sc
from mgnipy._models.constants.tax_ranks import SILVA_TAX_RANKS

# quick cleaning

# add filled na layer, zeros
ad_tax.layers["filled_na"] = ad_tax.to_df().fillna(0)

# drop samples if library count is less than median
ad_filt = ad_tax[
    ad_tax.to_df(layer="filled_na").sum(axis=1)
    >= ad_tax.to_df(layer="filled_na").sum(axis=1).median()
]

print(f"Num samples after filtering for low library counts: {ad_filt.n_obs}")

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

print(f"Num features after agglomerating to genus level (w/ pruning): {ad_genus.n_vars}")

# genus prevalence threshold of 10% samples
ad_genus_filt = ad_genus[
    :, (ad_genus.to_df(layer="sum") > 0).sum(axis=0) >= (ad_genus.n_vars * 0.1)
]

print(f"Num features after filtering for prevalence threshold of 10%: {ad_genus_filt.n_vars}")

# now to relative abundances
ad_genus_filt.obs["total_counts"] = ad_genus_filt.layers["sum"].sum(axis=1)
ad_genus_filt.layers["total_counts"] = np.array([ad_genus_filt.obs["total_counts"]] * ad_genus_filt.n_vars).T
ad_genus_filt.layers["rel_abund"] = ad_genus_filt.layers["sum"] / ad_genus_filt.layers["total_counts"]

#verbose
print(ad_genus_filt)
print(ad_genus_filt.obs['has_parkinsons_disease'].value_counts())

# %% [markdown]
# preparing dataset for ABaCo, which requires the feature cols but also:
# - ids
# - batch labels (pipeline version)
# - bio group labels (disease status)

# %% tags=["hide-output"]
df_ab = (
    ad_genus_filt.obs[["has_parkinsons_disease", "pipeline_version"]]
    .merge(ad_genus_filt.to_df(layer="sum"), left_index=True, right_index=True)
    .reset_index()
)
df_ab.to_csv("pd_gut_genus.csv", index=False)
df_ab.head()

# %% [markdown]
# ## Batch correction with `ABaCo`
#
# the below code is from [their demo notebook](https://mona-abaco.readthedocs.io/en/latest/tutorial/demo-parkinson.html)

# %% tags=["hide-input", "hide-output"]
from abaco.dataloader import DataPreprocess

# Load Parkinson's disease dataset
path_to_dataset = "pd_gut_genus.csv"
batch_col = "pipeline_version"
bio_col = "has_parkinsons_disease"
id_col = "_mgnipy_runs_accs"

# Convert data path into compatible pd.DataFrame
df_parkinson = DataPreprocess(
    path_to_dataset, factors=[id_col, batch_col, bio_col]
).dropna()

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
    n_bios=df_parkinson[bio_col].nunique(),
    bio_label=bio_col,
    n_batches=df_parkinson[batch_col].nunique(),
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
