import json

from mgnipy.V2.mixins import ResultsHandler


def test_results_handler_to_list_and_to_json():
    # The handler should expose the stored records both as a list and as JSON.
    handler = ResultsHandler(data=[{"x": 10}, {"x": 20}])

    assert handler.to_list() == [
        {"x": 10},
        {"x": 20},
    ], "List conversion should preserve the record order and content."
    assert json.loads(handler.to_json(lines=False)) == [
        {"x": 10},
        {"x": 20},
    ], "JSON conversion should serialize the same records."


def test_results_handler_to_df_renames_and_expands_nested_columns():
    # Nested dictionaries should be flattened when requested, while lineage is renamed.
    handler = ResultsHandler(
        data=[
            {
                "lineage": "root",
                "sample": {"accession": "S1", "study": "ST1"},
                "value": 1,
            }
        ]
    )

    df = handler.to_df(expand_nested_dicts=["sample"])

    assert list(df.columns) == [
        "biome_lineage",
        "value",
        "sample__accession",
        "sample__study",
    ], "The DataFrame should rename lineage and expand the nested sample field."
    assert (
        df.iloc[0]["biome_lineage"] == "root"
    ), "The lineage column should be renamed to biome_lineage."
    assert (
        df.iloc[0]["sample__accession"] == "S1"
    ), "The nested sample accession should be expanded into a flat column."
