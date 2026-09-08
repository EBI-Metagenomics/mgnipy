from types import SimpleNamespace

import pytest

from mgnipy._models.config import MGnipyConfig
from mgnipy.V2.mgnifier.query_executor import QueryExecutor
from mgnipy.V2.mgnifier.query_set import QuerySet


@pytest.fixture
def config_without_cache_dir():
    return MGnipyConfig(base_url="https://example.test/", cache_dir=None)


@pytest.fixture
def query_set(config_without_cache_dir):
    result = QuerySet(
        "studies", config=config_without_cache_dir, params={"page_size": 2}
    )
    result.count = 4
    result.num_requests = 2
    return result


def response(status_code=200, payload=None):
    payload = payload or {"items": [{"accession": "S1"}]}
    return SimpleNamespace(
        status_code=status_code,
        parsed=SimpleNamespace(to_dict=lambda: payload),
    )


def test_parse_response_returns_payload_for_success(query_set):
    executor = QueryExecutor(query_set, client=object())

    assert executor._parse_response(response()) == {"items": [{"accession": "S1"}]}


@pytest.mark.parametrize("status_code", [400, 403, 404, 500])
def test_parse_response_returns_none_for_failed_status(query_set, status_code):
    executor = QueryExecutor(query_set, client=object())

    assert executor._parse_response(response(status_code)) is None


def test_parse_response_preserves_binary_payload(query_set):
    executor = QueryExecutor(query_set, client=object())
    binary_response = SimpleNamespace(status_code=200, parsed=bytearray(b"page"))

    assert executor._parse_response(binary_response) == b"page"


def test_request_page_passes_page_params_and_reuses_results(query_set, monkeypatch):
    calls = []

    def fake_sync_detailed(*, client, **params):
        calls.append((client, params))
        return response(payload={"items": [{"accession": "S1"}]})

    monkeypatch.setattr(query_set.endpoint_module, "sync_detailed", fake_sync_detailed)
    client = object()
    executor = QueryExecutor(query_set, client=client)

    assert executor.request_page(2) == [{"accession": "S1"}]
    assert query_set._results == {2: [{"accession": "S1"}]}
    assert calls == [(client, {"page_size": 2, "page": 2})]
    assert executor.request_page(2) == [{"accession": "S1"}]
    assert len(calls) == 1


def test_request_page_returns_empty_for_page_outside_plan(query_set):
    executor = QueryExecutor(query_set, client=object())

    assert executor.request_page(3) == []


def test_request_page_returns_none_when_response_fails(query_set, monkeypatch):
    monkeypatch.setattr(
        query_set.endpoint_module,
        "sync_detailed",
        lambda **params: response(status_code=500),
    )
    executor = QueryExecutor(query_set, client=object())

    assert executor.request_page(1) is None
    assert query_set._results == {1: None}
