from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import (
    AuthenticatedClient,
    Client,
)
from ...models.paginated_pipeline_tool_list import PaginatedPipelineToolList
from ...models.pipelines_tools_list_format import PipelinesToolsListFormat
from ...types import (
    UNSET,
    Response,
    Unset,
)


def _get_kwargs(
    release_version: str,
    *,
    format_: PipelinesToolsListFormat | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_format_: str | Unset = UNSET
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params["ordering"] = ordering

    params["page"] = page

    params["page_size"] = page_size

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/pipelines/{release_version}/tools".format(
            release_version=quote(str(release_version), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PaginatedPipelineToolList | None:
    if response.status_code == 200:
        response_200 = PaginatedPipelineToolList.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[PaginatedPipelineToolList]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    release_version: str,
    *,
    client: AuthenticatedClient,
    format_: PipelinesToolsListFormat | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
) -> Response[PaginatedPipelineToolList]:
    """Retrieves list of pipeline tools for the given pipeline version
    Example:
    ---
    `/pipeline/{release_version}/tools`

    Args:
        release_version (str):
        format_ (PipelinesToolsListFormat | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedPipelineToolList]
    """

    kwargs = _get_kwargs(
        release_version=release_version,
        format_=format_,
        ordering=ordering,
        page=page,
        page_size=page_size,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    release_version: str,
    *,
    client: AuthenticatedClient,
    format_: PipelinesToolsListFormat | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
) -> PaginatedPipelineToolList | None:
    """Retrieves list of pipeline tools for the given pipeline version
    Example:
    ---
    `/pipeline/{release_version}/tools`

    Args:
        release_version (str):
        format_ (PipelinesToolsListFormat | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedPipelineToolList
    """

    return sync_detailed(
        release_version=release_version,
        client=client,
        format_=format_,
        ordering=ordering,
        page=page,
        page_size=page_size,
    ).parsed


async def asyncio_detailed(
    release_version: str,
    *,
    client: AuthenticatedClient,
    format_: PipelinesToolsListFormat | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
) -> Response[PaginatedPipelineToolList]:
    """Retrieves list of pipeline tools for the given pipeline version
    Example:
    ---
    `/pipeline/{release_version}/tools`

    Args:
        release_version (str):
        format_ (PipelinesToolsListFormat | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedPipelineToolList]
    """

    kwargs = _get_kwargs(
        release_version=release_version,
        format_=format_,
        ordering=ordering,
        page=page,
        page_size=page_size,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    release_version: str,
    *,
    client: AuthenticatedClient,
    format_: PipelinesToolsListFormat | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
) -> PaginatedPipelineToolList | None:
    """Retrieves list of pipeline tools for the given pipeline version
    Example:
    ---
    `/pipeline/{release_version}/tools`

    Args:
        release_version (str):
        format_ (PipelinesToolsListFormat | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedPipelineToolList
    """

    return (
        await asyncio_detailed(
            release_version=release_version,
            client=client,
            format_=format_,
            ordering=ordering,
            page=page,
            page_size=page_size,
        )
    ).parsed
