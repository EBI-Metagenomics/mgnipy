from mgnipy._models.constants.CONSTANTS import SupportedEndpoints


def test_supported_endpoints_list_excludes_private_members():
    # The public resource list should expose only supported user-facing endpoints.
    resources = SupportedEndpoints.as_list()

    assert (
        "studies" in resources
    ), "Expected studies to be exposed as a public endpoint."
    assert (
        "analysis" in resources
    ), "Expected analysis to be exposed as a public endpoint."
    assert (
        "_downloads" not in resources
    ), "Private helper endpoints should not appear in the public list."


def test_supported_endpoints_validate_and_is_valid():
    # Validation should resolve known resources and reject unknown names.
    assert (
        SupportedEndpoints.validate("studies") is SupportedEndpoints.STUDIES
    ), "Validation should map studies to the enum member."
    assert (
        SupportedEndpoints.is_valid("studies") is True
    ), "Known resources should be reported as valid."
    assert (
        SupportedEndpoints.is_valid("not-a-resource") is False
    ), "Unknown resources should be reported as invalid."


def test_supported_endpoints_dict_helpers_are_consistent():
    # The helper views should agree on the enum mapping in both directions.
    as_dict = SupportedEndpoints.as_dict()
    flipped = SupportedEndpoints.flipped_dict()

    assert (
        as_dict["STUDIES"] == "studies"
    ), "Enum-to-value mapping should preserve the studies entry."
    assert (
        flipped["studies"] == "STUDIES"
    ), "Value-to-enum mapping should preserve the studies entry."
    assert SupportedEndpoints.as_one_str().split(",")[:2] == [
        "analyses",
        "analysis",
    ], "The joined endpoint string should preserve enum ordering."
