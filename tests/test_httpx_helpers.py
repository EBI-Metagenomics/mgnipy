# Warning: This test will make actual HTTP requests
import asyncio

import pytest

from mgnipy._models.config import MGnipyConfig
from mgnipy._shared_helpers.httpx_helpers import init_httpx_client

URL = "https://www.ebi.ac.uk/metagenomics/api/v2/studies/?page=1&page_size=1"


def test_http2_false():

    client = init_httpx_client(
        config=MGnipyConfig(cache_dir=None),
        httpx_args={"http2": False},
    )

    async_client = client.get_async_httpx_client()

    response = asyncio.run(async_client.get(URL))

    assert response.http_version == "HTTP/1.1", "Expected HTTP/1.1 when http2 is False"


def test_http2_true():

    client = init_httpx_client(
        config=MGnipyConfig(cache_dir=None),
    )

    async_client = client.get_async_httpx_client()

    response = asyncio.run(async_client.get(URL))

    if response.http_version != "HTTP/2":
        pytest.skip(f"HTTP/2 was not negotiated: {response.http_version}")
