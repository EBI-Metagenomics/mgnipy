from __future__ import annotations

from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.m_gnify_study_accession_lookup import MGnifyStudyAccessionLookup
from ...types import Response


def _get_kwargs(
    accession: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/metagenomics/api/v2/studies/insdc/{accession}".format(
            accession=quote(str(accession), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> MGnifyStudyAccessionLookup | None:
    if response.status_code == 200:
        response_200 = MGnifyStudyAccessionLookup.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[MGnifyStudyAccessionLookup]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    accession: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[MGnifyStudyAccessionLookup]:
    """Find a MGnify study by its corresponding INSDC study/project accession

     Returns the MGnify study accession corresponding to an INSDC study/project accession.

    Args:
        accession (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[MGnifyStudyAccessionLookup]
    """

    kwargs = _get_kwargs(
        accession=accession,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    accession: str,
    *,
    client: AuthenticatedClient | Client,
) -> MGnifyStudyAccessionLookup | None:
    """Find a MGnify study by its corresponding INSDC study/project accession

     Returns the MGnify study accession corresponding to an INSDC study/project accession.

    Args:
        accession (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        MGnifyStudyAccessionLookup
    """

    return sync_detailed(
        accession=accession,
        client=client,
    ).parsed


async def asyncio_detailed(
    accession: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[MGnifyStudyAccessionLookup]:
    """Find a MGnify study by its corresponding INSDC study/project accession

     Returns the MGnify study accession corresponding to an INSDC study/project accession.

    Args:
        accession (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[MGnifyStudyAccessionLookup]
    """

    kwargs = _get_kwargs(
        accession=accession,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    accession: str,
    *,
    client: AuthenticatedClient | Client,
) -> MGnifyStudyAccessionLookup | None:
    """Find a MGnify study by its corresponding INSDC study/project accession

     Returns the MGnify study accession corresponding to an INSDC study/project accession.

    Args:
        accession (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        MGnifyStudyAccessionLookup
    """

    return (
        await asyncio_detailed(
            accession=accession,
            client=client,
        )
    ).parsed
