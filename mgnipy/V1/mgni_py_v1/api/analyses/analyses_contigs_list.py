from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.analyses_contigs_list_format import AnalysesContigsListFormat
from ...models.paginated_analysis_job_contig_list import PaginatedAnalysisJobContigList
from ...types import UNSET, Response, Unset


def _get_kwargs(
    accession: str,
    *,
    cursor: int | Unset = UNSET,
    format_: AnalysesContigsListFormat | Unset = UNSET,
    page_size: int | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["cursor"] = cursor

    json_format_: str | Unset = UNSET
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params["page_size"] = page_size

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/analyses/{accession}/contigs".format(
            accession=quote(str(accession), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PaginatedAnalysisJobContigList | None:
    if response.status_code == 200:
        response_200 = PaginatedAnalysisJobContigList.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[PaginatedAnalysisJobContigList]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    accession: str,
    *,
    client: AuthenticatedClient,
    cursor: int | Unset = UNSET,
    format_: AnalysesContigsListFormat | Unset = UNSET,
    page_size: int | Unset = UNSET,
) -> Response[PaginatedAnalysisJobContigList]:
    """Adaptation of DRF ReadOnlyModelViewSet

    Args:
        accession (str):
        cursor (int | Unset):
        format_ (AnalysesContigsListFormat | Unset):
        page_size (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedAnalysisJobContigList]
    """

    kwargs = _get_kwargs(
        accession=accession,
        cursor=cursor,
        format_=format_,
        page_size=page_size,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    accession: str,
    *,
    client: AuthenticatedClient,
    cursor: int | Unset = UNSET,
    format_: AnalysesContigsListFormat | Unset = UNSET,
    page_size: int | Unset = UNSET,
) -> PaginatedAnalysisJobContigList | None:
    """Adaptation of DRF ReadOnlyModelViewSet

    Args:
        accession (str):
        cursor (int | Unset):
        format_ (AnalysesContigsListFormat | Unset):
        page_size (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedAnalysisJobContigList
    """

    return sync_detailed(
        accession=accession,
        client=client,
        cursor=cursor,
        format_=format_,
        page_size=page_size,
    ).parsed


async def asyncio_detailed(
    accession: str,
    *,
    client: AuthenticatedClient,
    cursor: int | Unset = UNSET,
    format_: AnalysesContigsListFormat | Unset = UNSET,
    page_size: int | Unset = UNSET,
) -> Response[PaginatedAnalysisJobContigList]:
    """Adaptation of DRF ReadOnlyModelViewSet

    Args:
        accession (str):
        cursor (int | Unset):
        format_ (AnalysesContigsListFormat | Unset):
        page_size (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedAnalysisJobContigList]
    """

    kwargs = _get_kwargs(
        accession=accession,
        cursor=cursor,
        format_=format_,
        page_size=page_size,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    accession: str,
    *,
    client: AuthenticatedClient,
    cursor: int | Unset = UNSET,
    format_: AnalysesContigsListFormat | Unset = UNSET,
    page_size: int | Unset = UNSET,
) -> PaginatedAnalysisJobContigList | None:
    """Adaptation of DRF ReadOnlyModelViewSet

    Args:
        accession (str):
        cursor (int | Unset):
        format_ (AnalysesContigsListFormat | Unset):
        page_size (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedAnalysisJobContigList
    """

    return (
        await asyncio_detailed(
            accession=accession,
            client=client,
            cursor=cursor,
            format_=format_,
            page_size=page_size,
        )
    ).parsed
