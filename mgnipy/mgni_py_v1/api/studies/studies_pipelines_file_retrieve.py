from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.studies_pipelines_file_retrieve_format import (
    StudiesPipelinesFileRetrieveFormat,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    accession: str,
    release_version: str,
    alias: str,
    *,
    format_: StudiesPipelinesFileRetrieveFormat | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_format_: str | Unset = UNSET
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/studies/{accession}/pipelines/{release_version}/file/{alias}".format(
            accession=quote(str(accession), safe=""),
            release_version=quote(str(release_version), safe=""),
            alias=quote(str(alias), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | None:
    if response.status_code == 200:
        return None

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    accession: str,
    release_version: str,
    alias: str,
    *,
    client: AuthenticatedClient,
    format_: StudiesPipelinesFileRetrieveFormat | Unset = UNSET,
) -> Response[Any]:
    """Retrieves static summary file
    Example:
    ---
    `
    /studies/MGYS00000410/pipelines/2.0/file/
    ERP001736_taxonomy_abundances_v2.0.tsv`

    Args:
        accession (str):
        release_version (str):
        alias (str):
        format_ (StudiesPipelinesFileRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        accession=accession,
        release_version=release_version,
        alias=alias,
        format_=format_,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    accession: str,
    release_version: str,
    alias: str,
    *,
    client: AuthenticatedClient,
    format_: StudiesPipelinesFileRetrieveFormat | Unset = UNSET,
) -> Response[Any]:
    """Retrieves static summary file
    Example:
    ---
    `
    /studies/MGYS00000410/pipelines/2.0/file/
    ERP001736_taxonomy_abundances_v2.0.tsv`

    Args:
        accession (str):
        release_version (str):
        alias (str):
        format_ (StudiesPipelinesFileRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        accession=accession,
        release_version=release_version,
        alias=alias,
        format_=format_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
