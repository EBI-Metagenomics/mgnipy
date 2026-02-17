from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from mgnipy._shared_helpers import errors
from mgnipy.V2 import (
    AuthenticatedClient,
    Client,
)
from mgnipy.V2._mgnipy_models.types import Response
from mgnipy.V2.mgni_py_v2.models.super_study_detail import SuperStudyDetail


def _get_kwargs(
    slug: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/metagenomics/api/v2/super-studies/{slug}".format(
            slug=quote(str(slug), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> SuperStudyDetail | None:
    if response.status_code == 200:
        response_200 = SuperStudyDetail.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[SuperStudyDetail]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    slug: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[SuperStudyDetail]:
    """Get the detail of a single Super Study

     A Super Study is a collection of MGnify Studies all related to a single large initiative. They may
    also reference Genome Catalogues that were assembled from the Studies or as part of the Super Study
    initiative.

    Args:
        slug (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SuperStudyDetail]
    """

    kwargs = _get_kwargs(
        slug=slug,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    slug: str,
    *,
    client: AuthenticatedClient | Client,
) -> SuperStudyDetail | None:
    """Get the detail of a single Super Study

     A Super Study is a collection of MGnify Studies all related to a single large initiative. They may
    also reference Genome Catalogues that were assembled from the Studies or as part of the Super Study
    initiative.

    Args:
        slug (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SuperStudyDetail
    """

    return sync_detailed(
        slug=slug,
        client=client,
    ).parsed


async def asyncio_detailed(
    slug: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[SuperStudyDetail]:
    """Get the detail of a single Super Study

     A Super Study is a collection of MGnify Studies all related to a single large initiative. They may
    also reference Genome Catalogues that were assembled from the Studies or as part of the Super Study
    initiative.

    Args:
        slug (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SuperStudyDetail]
    """

    kwargs = _get_kwargs(
        slug=slug,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    slug: str,
    *,
    client: AuthenticatedClient | Client,
) -> SuperStudyDetail | None:
    """Get the detail of a single Super Study

     A Super Study is a collection of MGnify Studies all related to a single large initiative. They may
    also reference Genome Catalogues that were assembled from the Studies or as part of the Super Study
    initiative.

    Args:
        slug (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SuperStudyDetail
    """

    return (
        await asyncio_detailed(
            slug=slug,
            client=client,
        )
    ).parsed
