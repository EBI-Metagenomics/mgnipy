from types import SimpleNamespace

import pytest

from mgnipy._shared_helpers.async_helpers import (
    CONCURRENCY_LIMIT,
    get_semaphore,
)
from mgnipy._shared_helpers.parsers import (
    extract_doc_sections,
    get_docstring,
    is_numpy_header,
    parse_args_block,
)
from mgnipy._shared_helpers.validators import validate_gt_int
from mgnipy._shared_helpers.writers import atomic_write_bytes, atomic_write_json


def test_validate_gt_int_enforces_lower_bound():
    # The validator should return the original value when it satisfies the lower bound.
    assert (
        validate_gt_int(10, 5) == 10
    ), "Values above the threshold should pass through unchanged."

    with pytest.raises(ValueError, match="Int must be greater than 5: 3"):
        validate_gt_int(3, 5)


def test_get_semaphore_caps_concurrency():
    # The semaphore should never exceed the module-level concurrency cap.
    assert (
        get_semaphore(2)._value == 2
    ), "Requested concurrency below the cap should be preserved."
    assert (
        get_semaphore(CONCURRENCY_LIMIT + 20)._value == CONCURRENCY_LIMIT
    ), "Requested concurrency above the cap should be clamped."


def test_atomic_write_helpers_create_expected_files(tmp_path):
    # Write both JSON and binary payloads so the file helpers are exercised end to end.
    json_path = tmp_path / "data.json"
    bytes_path = tmp_path / "data.bin"

    atomic_write_json(json_path, {"a": 1, "b": [2, 3]})
    atomic_write_bytes(bytes_path, b"abc123")

    assert (
        json_path.read_text() == '{"a": 1, "b": [2, 3]}'
    ), "JSON writes should preserve the original data structure."
    assert (
        bytes_path.read_bytes() == b"abc123"
    ), "Binary writes should preserve the original byte content."
    assert not json_path.with_suffix(
        ".json.tmp"
    ).exists(), "Temporary JSON files should be cleaned up after the atomic write."
    assert not bytes_path.with_suffix(
        ".bin.tmp"
    ).exists(), "Temporary binary files should be cleaned up after the atomic write."


def test_parse_doc_helpers_handle_numpy_and_google_styles():
    # This sample docstring mixes the Google-style and NumPy-style patterns the parser supports.
    doc = """
    My Function

    This function does something.

    Args:
        x (int): The first parameter.
        y (str): The second parameter.

    Returns:
        bool: True if successful.
    """

    sections = extract_doc_sections(doc)
    assert (
        sections["title"] == "My Function"
    ), "The first non-empty line should be treated as the section title."
    assert (
        sections["description"] == "This function does something."
    ), "The body text before the Args section should become the description."
    assert parse_args_block(sections["args"]) == {
        "x": "int The first parameter.",
        "y": "str The second parameter.",
    }, "Argument blocks should normalize parameter names and descriptions."

    assert (
        is_numpy_header(["Parameters", "----------"], 0) is True
    ), "NumPy-style section headers should be detected."
    assert (
        is_numpy_header(["Notes", "-----"], 0) is True
    ), "Known section names with dash underlines should be detected."
    assert (
        is_numpy_header(["Other", "-----"], 0) is False
    ), "Unknown header names should not be treated as sections."


def test_get_docstring_uses_callable_docstring_first():
    def sample_function():
        """Sample callable docstring."""

    module = SimpleNamespace(sample_function=sample_function)

    assert (
        get_docstring(module, "sample_function") == "Sample callable docstring."
    ), "The callable docstring should be preferred over the module docstring."
