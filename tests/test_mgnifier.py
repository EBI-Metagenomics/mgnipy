from mgnipy._models.config import MGnipyConfig
from mgnipy._models.constants.CONSTANTS import SupportedEndpoints
from mgnipy.V2.mgnifier import MGnifier
from mgnipy.V2.mgnifier.endpoints import ID_PARAM

RESOURCE = "studies"
SUPPORTED_END = SupportedEndpoints(RESOURCE)
FAKE_PAGE_RESULT = [
    {ID_PARAM[SUPPORTED_END]: "S1"},
    {ID_PARAM[SUPPORTED_END]: "S2"},
]
EXPECTED_IDS = ["S1", "S2"]


def test_mgnifier_page_checkpoints(monkeypatch, tmp_path):
    # Setup a MGnifier instance with a temporary cache directory
    config = MGnipyConfig(
        base_url="https://example.test/",
        cache_dir=tmp_path,
    )

    # Setup a MGnifier instance
    query = MGnifier(
        RESOURCE,
        config=config,
        client=object(),  # client is not used in this test
        resolve_auth=False,
        page_size=2,
    )
    query.count = 2  # num items in total
    query.num_requests = 1  # num queries

    # Mock the request_page method to simulate a real API call
    def fake_request_page(page_num):
        query._results = {page_num: FAKE_PAGE_RESULT}
        return query._results[page_num]

    # Mock the request_page method of the executor
    monkeypatch.setattr(query.exec, "request_page", fake_request_page)

    assert (
        query.page(1) == FAKE_PAGE_RESULT
    ), "Expected the page method to return the fake page result"
    assert (
        query.search_results.ids == EXPECTED_IDS
    ), "Expected the search_results.ids to be updated with the fake page result"

    # empty result again to test cache loading
    query._results = None
    assert query.load_cache_results() == [
        1
    ], "Expected the load_cache_results method to return the cached page number"
    assert (
        query.search_results.ids == EXPECTED_IDS
    ), "Expected the search_results.ids to be preserved after loading from cache"


def test_mgnifier_get_all_fetches_leftover_pages(monkeypatch):
    query = MGnifier(
        RESOURCE,
        config=MGnipyConfig(cache_dir=None),
        client=object(),
        resolve_auth=False,
    )
    query.count = 2
    query.num_requests = 3
    query._results = {}

    def fake_page(page_num):
        query._results[page_num] = FAKE_PAGE_RESULT
        return query._results[page_num]

    # Mock .page to simulate fetching pages without making real API calls
    monkeypatch.setattr(query, "try_load_cache", lambda: None)
    monkeypatch.setattr(query.exec, "_set_counts", lambda: None)
    monkeypatch.setattr(query, "page", fake_page)

    # Call get_all to fetch all pages (num_requests=2)
    query.get_all(limit=None, hide_progress=True)

    assert query._results == {
        1: FAKE_PAGE_RESULT,
        2: FAKE_PAGE_RESULT,
        3: FAKE_PAGE_RESULT,
    }, "Expected the _results to contain all three pages"
    assert (
        query.search_results.ids == EXPECTED_IDS * 3
    ), "Expected search_results.ids to contain IDs from all three pages"
