import pytest

from mgnipy import MGnipy
from mgnipy.V2.datasets import MTG
from mgnipy.V2.proxies import Studies


@pytest.fixture
def mgnipy_client():
    return MGnipy(cache_dir=None)


def test_mgnipy_lists_supported_resources(mgnipy_client):
    resources = mgnipy_client.list_resources()

    assert "studies" in resources
    assert "study" in resources


def test_mgnipy_resolves_endpoint_proxy(mgnipy_client):
    studies = mgnipy_client.studies

    assert isinstance(studies, Studies)
    assert studies.resource.value == "studies"
    assert studies.client is mgnipy_client.client


def test_mgnipy_resolves_dataset_helper(mgnipy_client):
    assert isinstance(mgnipy_client.mtg, MTG)


def test_mgnipy_rejects_unknown_attribute(mgnipy_client):
    with pytest.raises(AttributeError):
        _ = mgnipy_client.not_a_resource


def test_mgnipy_rejects_unknown_item(mgnipy_client):
    with pytest.raises(KeyError):
        mgnipy_client["not_a_resource"]
