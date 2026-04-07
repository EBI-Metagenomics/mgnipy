from typing import Any

import pytest

from mgnipy.V2.core import MGnifier


@pytest.fixture
def cache_dir():
    return "pytesting_core_mgnifier_cache"


@pytest.fixture
def pagenate_params() -> dict[str, Any]:
    return {
        "page_size": 5,
        "page": 1,
    }


@pytest.fixture
def biomes_params() -> dict[str, Any]:
    return {"biome_lineage": "root:Engineered:Bioremediation"}


def test_pagenated(pagenate_params):
    # test that pagenated retrieval works and that the correct number of pages are retrieved
    # make small requests

    for resource in ["studies", "analyses", "samples", "biomes"]:
        # init mgnifier
        mg = MGnifier(resource=resource, params=pagenate_params)
        # get page 1
        mg.first()
        # now tests
        assert (
            mg.pagination_status
        ), f"Pagination status should be True after retrieval for resource {resource}"
        assert (
            mg.total_pages > 0
        ), f"Total pages should be greater than 0 for resource {resource}"
        assert (
            len(mg.to_df()) == pagenate_params["page_size"]
        ), f"pandas df should only contain page_size results for resource {resource}"
        assert (
            mg.to_polars().height == pagenate_params["page_size"]
        ), f"Polars df should only contain page_size results for resource {resource}"
        assert mg._is_in_results(
            1
        ), f"Page 1 should be in results for resource {resource}"
        assert not mg._is_in_results(
            2
        ), f"Page 2 should not be in results for resource {resource}"

        # now get page 2
        mg.page(2)
        # tests
        assert mg._is_in_results(
            2
        ), f"Page 2 should be in results after retrieval for resource {resource}"
        assert len(mg.to_df()) == (
            pagenate_params["page_size"] * 2
        ), f"pandas df should contain page_size * 2 results for resource {resource}"
        assert mg.to_polars().height == (
            pagenate_params["page_size"] * 2
        ), f"Polars df should contain page_size * 2 results for resource {resource}"

        # now get page 5
        mg.page(5)
        # tests
        assert not mg._is_in_results(
            3
        ), f"Page 3 should not be in results after retrieval for resource {resource}"
        assert mg._is_in_results(
            5
        ), f"Page 5 should be in results after retrieval for resource {resource}"
        assert len(mg.to_df()) == (
            pagenate_params["page_size"] * 3
        ), f"pandas df should contain page_size * 3 results for resource {resource}"
        assert mg.to_polars().height == (
            pagenate_params["page_size"] * 3
        ), f"Polars df should contain page_size * 3 results for resource {resource}"

    # clean up
    del mg
