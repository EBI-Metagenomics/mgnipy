from types import SimpleNamespace

import polars as pl

from mgnipy._models.config import MGnipyConfig
from mgnipy.V2 import datasets as datasets_mod
from mgnipy.V2.datasets import MGazine, TaxaMGazine


class FakeMGnifier:
    def __init__(self, resource, config, url):
        self.resource = resource
        self.config = config
        self.url = url
        self.exec = SimpleNamespace(
            httpx_client="sync-client", httpx_aclient="async-client"
        )


class FakeTaxaMGazine:
    def __init__(self, mgazine, config=None, **kwargs):
        self.mgazine = mgazine
        self.config = config
        self.kwargs = kwargs


class FakeDwCTaxaMGazine(FakeTaxaMGazine):
    pass


def test_mgazine_basic_properties_and_grouping():
    # Keep the fixture minimal but include the columns needed by the grouping helpers.
    downloads = [
        {
            "alias": "reads.tsv",
            "url": "https://example.org/reads.tsv",
            "file_type": "tsv",
            "download_type": "tabular",
            "download_group": "group.v4.1",
            "pipeline_version": "v4_1",
            "short_description": "reads",
        },
        {
            "alias": "summary.tsv",
            "url": "https://example.org/summary.tsv",
            "file_type": "tsv",
            "download_type": "tabular",
            "download_group": "group.v5",
            "pipeline_version": "v5",
            "short_description": "summary",
        },
    ]

    mgazine = MGazine(downloads, config=MGnipyConfig())

    assert mgazine.aliases == [
        "reads.tsv",
        "summary.tsv",
    ], "Aliases should preserve the order from the downloads list."
    assert (
        mgazine.url_dict["reads.tsv"] == "https://example.org/reads.tsv"
    ), "url_dict should map each alias to its URL."
    assert mgazine.url_list == [
        "https://example.org/reads.tsv",
        "https://example.org/summary.tsv",
    ], "url_list should preserve the original download ordering."
    assert mgazine.list_pipeline_version() == [
        "v4_1",
        "v5",
    ], "Pipeline versions should be collected and sorted."
    assert mgazine.list_short_descriptions() == [
        "reads",
        "summary",
    ], "Short descriptions should be collected and sorted."


def test_mgazine_selector_helpers_return_filtered_instances():
    # Attribute and item access should return narrowed MGazine instances for the matching subset.
    downloads = [
        {
            "alias": "reads.tsv",
            "url": "https://example.org/reads.tsv",
            "file_type": "tsv",
            "download_type": "tabular",
            "download_group": "group.v4.1",
            "pipeline_version": "v4_1",
            "short_description": "reads",
        },
        {
            "alias": "summary.tsv",
            "url": "https://example.org/summary.tsv",
            "file_type": "tsv",
            "download_type": "tabular",
            "download_group": "group.v5",
            "pipeline_version": "v5",
            "short_description": "summary",
        },
    ]

    mgazine = MGazine(downloads)

    v4 = mgazine.v4_1
    assert isinstance(
        v4, MGazine
    ), "Pipeline-version attribute access should return a new MGazine instance."
    assert v4.aliases == [
        "reads.tsv"
    ], "The pipeline-version selector should filter to the matching download only."

    summary = mgazine["summary"]
    assert isinstance(
        summary, MGazine
    ), "Non-taxonomic item access should return a narrowed MGazine."
    assert summary.aliases == [
        "summary.tsv"
    ], "The short-description selector should filter to the matching download only."


def test_mgazine_item_access_selects_curators(monkeypatch):
    # Patch the curator classes so we can verify the dispatch logic without building the full curator stack.
    monkeypatch.setattr(datasets_mod, "TaxaMGazine", FakeTaxaMGazine)
    monkeypatch.setattr(datasets_mod, "DWCTaxaMGazine", FakeDwCTaxaMGazine)

    taxonomic_downloads = [
        {
            "alias": "taxonomy.tsv",
            "url": "https://example.org/taxonomy.tsv",
            "file_type": "tsv",
            "download_type": "taxonomic",
            "download_group": "group.v4.1",
            "pipeline_version": "v4_1",
            "short_description": "silva-taxonomy",
        }
    ]
    dwc_downloads = [
        {
            "alias": "dwc.tsv",
            "url": "https://example.org/dwc.tsv",
            "file_type": "tsv",
            "download_type": "taxonomic",
            "download_group": "group.v4.1",
            "pipeline_version": "v4_1",
            "short_description": "dwc-ready-taxonomy",
        }
    ]

    taxonomic = MGazine(taxonomic_downloads)
    dwc = MGazine(dwc_downloads)

    taxa_curator = taxonomic["silva-taxonomy"]
    assert isinstance(
        taxa_curator, FakeTaxaMGazine
    ), "Taxonomic downloads should dispatch to TaxaMGazine."
    assert taxa_curator.mgazine.aliases == [
        "taxonomy.tsv"
    ], "The curator should receive the filtered MGazine subset."

    dwc_curator = dwc["dwc-ready-taxonomy"]
    assert isinstance(
        dwc_curator, FakeDwCTaxaMGazine
    ), "DwC-ready taxonomic downloads should dispatch to DWCTaxaMGazine."
    assert dwc_curator.mgazine.aliases == [
        "dwc.tsv"
    ], "The DwC curator should receive the filtered MGazine subset."


def test_mgazine_mgnifier_helper_passes_download_url_and_disables_cache(
    monkeypatch,
):
    # The helper should preserve the URL and force an uncached configuration for download operations.
    monkeypatch.setattr(datasets_mod, "MGnifier", FakeMGnifier)

    mgazine = MGazine(
        [
            {
                "alias": "reads.tsv",
                "url": "https://example.org/reads.tsv",
                "file_type": "tsv",
                "download_type": "tabular",
                "download_group": "group.v4.1",
                "pipeline_version": "v4_1",
                "short_description": "reads",
            }
        ],
        config=MGnipyConfig(cache_dir="/tmp/mgnipy-cache"),
    )

    helper = mgazine._mgnifier_helper(
        url="https://example.org/reads.tsv", cache_dir=None
    )

    assert (
        helper.resource == "_downloads"
    ), "The helper should target the internal downloads endpoint."
    assert (
        helper.url == "https://example.org/reads.tsv"
    ), "The helper should forward the requested download URL."
    assert (
        helper.config.cache_dir is None
    ), "Download helpers should disable the cache directory."


def test_taxa_curator_builds_metadata_from_taxonomy_column(monkeypatch):
    # Avoid the cache bootstrap path so we can focus on the metadata transformation logic.
    monkeypatch.setattr(TaxaMGazine, "_init_cache_handler_state", lambda self: None)

    mgazine = MGazine(
        [
            {
                "alias": "taxonomy.tsv",
                "url": "https://example.org/taxonomy.tsv",
                "file_type": "tsv",
                "download_type": "taxonomic",
                "download_group": "group.v4.1",
                "pipeline_version": "v4_1",
                "short_description": "silva-taxonomy",
            }
        ]
    )

    curator = TaxaMGazine(
        mgazine=mgazine,
        long_short_mapping={"kingdom": "k", "phylum": "p"},
    )

    curator._lazy_merged = pl.DataFrame(
        {
            "taxonomy": ["k__Bacteria;p__Firmicutes"],
            "run_1": [1],
        }
    ).lazy()

    assert curator.runs_accessions == [
        "run_1"
    ], "run columns should exclude the taxonomic metadata columns."
    assert curator._iter_runs() == [
        "run_1"
    ], "Without run results, every run accession should be considered pending."

    metadata = curator.taxonomic_metadata(df_engine="polars")

    assert list(metadata.columns) == [
        "kingdom",
        "phylum",
    ], "Taxonomy strings should be expanded into the configured rank columns."
    assert (
        metadata[0, "kingdom"] == "Bacteria"
    ), "The kingdom prefix should be stripped from the taxonomy string."
    assert (
        metadata[0, "phylum"] == "Firmicutes"
    ), "The phylum prefix should be stripped from the taxonomy string."


def test_taxa_curator_inherits_mgazine_download_helpers(monkeypatch):
    # Keep the constructor lightweight and verify the curator still behaves like a MGazine.
    monkeypatch.setattr(TaxaMGazine, "_init_cache_handler_state", lambda self: None)

    mgazine = MGazine(
        [
            {
                "alias": "taxonomy.tsv",
                "url": "https://example.org/taxonomy.tsv",
                "file_type": "tsv",
                "download_type": "taxonomic",
                "download_group": "group.v4.1",
                "pipeline_version": "v4_1",
                "short_description": "silva-taxonomy",
            }
        ]
    )

    curator = TaxaMGazine(mgazine=mgazine)

    assert isinstance(
        curator, MGazine
    ), "TaxaMGazine should expose the same public MGazine interface."
    assert curator.url_list == mgazine.url_list
    assert curator.aliases == mgazine.aliases
    assert hasattr(curator, "download")
    assert hasattr(curator, "adownload")
