# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
# ---

# %% [markdown]
# # `MGazine` of MGnify data
#
# Recall:
#
# 1. Start up a mgnipy.MGnipy client with your desired configuration
#
# 2. Search in MGnify resources using a MGnifier glass
#
# 3. Receive a MGazine of MGnify datasets
#
# ---

# %% [markdown]
# Supported formats include:
# - TSV/CSV — stream_pandas (pandas) or stream_polars (polars) (handles gzipped TSV/CSV).
# - TXT — stream_txt (full text or line-chunks).
# - HTML — stream_html (opens in browser).
# - FASTA / GFF / BIOM — stream_fasta, stream_gff, stream_biom (scikit-bio generators).
# - Gzipped HTTP streams — stream_gzipped (file-like reader).
# - JSONL / NDJSON — stream_jsonl (pandas or polars).
# - JSON — stream_json (full JSON or streamed via ijson; gzipped JSON supported).
# - Tree / Newick — stream_tree (scikit-bio).
# - Other — JSON files under other are streamed via stream_json; binary/unsupported types should be downloaded.
