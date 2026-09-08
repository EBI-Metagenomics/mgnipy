from urllib.parse import parse_qs, urlsplit

import pytest

from mgnipy._models.config import MGnipyConfig
from mgnipy.V2.mgnifier.query_set import QuerySet


@pytest.fixture
def config_without_cache_dir():
    return MGnipyConfig(base_url="https://example.test/", cache_dir=None)


def test_query_set_filter_clones_and_overrides_params(config_without_cache_dir):
    query_set = QuerySet(
        "studies",
        config=config_without_cache_dir,
        params={"search": "old"},
        page_size=10,
    )

    filtered = query_set.filter(search="new")

    assert query_set.params == {"search": "old", "page_size": 10}
    assert filtered is not query_set
    assert filtered.params == {"search": "new", "page_size": 10}
    assert filtered.resource == query_set.resource


def test_query_set_builds_list_queries_and_urls(config_without_cache_dir):
    query_set = QuerySet(
        "studies",
        config=config_without_cache_dir,
        params={"search": "marine samples", "page_size": 10},
    )
    query_set.count = 25
    query_set.num_requests = 3

    queries = query_set.build_queries(timeout=5)
    urls = query_set.list_urls()

    assert list(queries) == [1, 2, 3]
    assert queries[2]["params"]["page"] == 2
    assert queries[2]["timeout"] == 5
    assert len(urls) == 3
    assert parse_qs(urlsplit(urls[0]).query) == {
        "search": ["marine samples"],
        "page_size": ["10"],
        "page": ["1"],
    }


def test_query_set_builds_one_detail_query(config_without_cache_dir):
    query_set = QuerySet("study", config=config_without_cache_dir, accession="ERP123")

    queries = query_set.build_queries()

    assert list(queries) == [1]
    assert queries[1]["params"] == {"accession": "ERP123"}
    assert query_set.request_url == (
        "https://example.test/metagenomics/api/v2/studies/ERP123"
    )


def test_query_set_rejects_invalid_resource(config_without_cache_dir):
    with pytest.raises(ValueError):
        QuerySet("not-a-resource", config=config_without_cache_dir)


def test_query_set_rejects_invalid_page_numbers(config_without_cache_dir):
    query_set = QuerySet("studies", config=config_without_cache_dir)

    with pytest.raises(ValueError):
        query_set._is_in_results(0)
