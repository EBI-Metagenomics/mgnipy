import pytest

import mgnipy.mgnipy as mgnipy_module
from mgnipy import MGnipy
from mgnipy._models.config import MGnipyConfig
from mgnipy._models.constants.CONSTANTS import SupportedEndpoints


class FakeListProxy:
    def __init__(self, config):
        self.config = config


class FakeDetailProxy:
    def __init__(self, id=None, config=None, **kwargs):
        self.id = id
        self.config = config
        self.kwargs = kwargs


class FakeDescribeHandler:
    def __init__(self, response):
        self.response = response

    def describe_endpoint(self, as_dict=False):
        return {"as_dict": as_dict, "response": self.response}


class FakeDescribeProxy:
    def __init__(self, config):
        self.config = config
        self.emgapi_handler = FakeDescribeHandler(response=config.cache_dir)


def test_mgnipy_exposes_cache_dir_and_endpoint_dispatch(tmp_path, monkeypatch):
    # Swap the real endpoint proxies for tiny fakes so the dispatch logic stays offline.
    monkeypatch.setattr(
        mgnipy_module,
        "V2_ENDPOINT_LIST_PROXIES",
        {SupportedEndpoints.STUDIES: FakeListProxy},
    )
    monkeypatch.setattr(
        mgnipy_module,
        "V2_ENDPOINT_DETAIL_PROXIES",
        {SupportedEndpoints.STUDY: FakeDetailProxy},
    )

    client = MGnipy(cache_dir=tmp_path)

    assert (
        client.cache_dir == tmp_path
    ), "The cache_dir shortcut should expose the configured cache path."

    studies = client.studies
    assert isinstance(
        studies, FakeListProxy
    ), "List endpoint access should return the configured list proxy."
    assert isinstance(
        studies.config, MGnipyConfig
    ), "List proxy should receive the active MGnipyConfig instance."

    study = client.study("ABC123")
    assert isinstance(
        study, FakeDetailProxy
    ), "Detail endpoint access should return the configured detail proxy factory."
    assert (
        study.id == "ABC123"
    ), "Detail endpoint access should forward the accession to the proxy."
    assert (
        study.config == studies.config
    ), "Detail proxies should reuse the same config object as list proxies."

    with pytest.raises(ValueError, match="Invalid SupportedEndpoints: not_a_resource"):
        _ = client.not_a_resource


def test_describe_resource_delegates_and_rejects_invalid_resources(
    tmp_path, monkeypatch
):
    # The describe path should route through the proxy's handler and reject invalid names cleanly.
    monkeypatch.setattr(
        mgnipy_module,
        "V2_ALL_PROXIES",
        {SupportedEndpoints.STUDIES: FakeDescribeProxy},
    )

    client = MGnipy(cache_dir=tmp_path)

    assert client.describe_resource("studies", as_dict=True) == {
        "as_dict": True,
        "response": tmp_path,
    }, "Describing a supported resource should delegate to the proxy handler."
    assert (
        client.describe_resource("does-not-exist") is None
    ), "Unsupported resources should return None instead of raising."


def test_clear_subcaches_removes_only_expected_cache_entries(tmp_path):
    # Only cache subdirectories with the expected file layout should be removed.
    keep_file = tmp_path / "auth_token.json"
    keep_file.write_text("keep me")

    cache_dir = tmp_path / "studies"
    cache_dir.mkdir()
    (cache_dir / "mgnipy_manifest.json").write_text("{}")
    (cache_dir / "mgnipy_page_1.json").write_text("[]")

    client = MGnipy(cache_dir=tmp_path)
    client.clear_subcaches()

    assert (
        not cache_dir.exists()
    ), "Valid cache subdirectories should be deleted during cache clearing."
    assert keep_file.exists(), "Non-directory cache entries should be preserved."
