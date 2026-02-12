from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import (
    AuthenticatedClient,
    Client,
)
from ...models.pipeline_tool import PipelineTool
from ...models.pipeline_tools_retrieve_format import PipelineToolsRetrieveFormat
from ...types import (
    UNSET,
    Response,
    Unset,
)


def _get_kwargs(
    tool_name: str,
    version: str,
    *,
    format_: PipelineToolsRetrieveFormat | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_format_: str | Unset = UNSET
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/pipeline-tools/{tool_name}/{version}".format(
            tool_name=quote(str(tool_name), safe=""),
            version=quote(str(version), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PipelineTool | None:
    if response.status_code == 200:
        response_200 = PipelineTool.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[PipelineTool]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    tool_name: str,
    version: str,
    *,
    client: AuthenticatedClient,
    format_: PipelineToolsRetrieveFormat | Unset = UNSET,
) -> Response[PipelineTool]:
    """Retrieves pipeline tool details for the given pipeline version
    Example:
    ---
    `/pipeline-tools/interproscan/5.19-58.0`

    Args:
        tool_name (str):
        version (str):
        format_ (PipelineToolsRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PipelineTool]
    """

    kwargs = _get_kwargs(
        tool_name=tool_name,
        version=version,
        format_=format_,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    tool_name: str,
    version: str,
    *,
    client: AuthenticatedClient,
    format_: PipelineToolsRetrieveFormat | Unset = UNSET,
) -> PipelineTool | None:
    """Retrieves pipeline tool details for the given pipeline version
    Example:
    ---
    `/pipeline-tools/interproscan/5.19-58.0`

    Args:
        tool_name (str):
        version (str):
        format_ (PipelineToolsRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PipelineTool
    """

    return sync_detailed(
        tool_name=tool_name,
        version=version,
        client=client,
        format_=format_,
    ).parsed


async def asyncio_detailed(
    tool_name: str,
    version: str,
    *,
    client: AuthenticatedClient,
    format_: PipelineToolsRetrieveFormat | Unset = UNSET,
) -> Response[PipelineTool]:
    """Retrieves pipeline tool details for the given pipeline version
    Example:
    ---
    `/pipeline-tools/interproscan/5.19-58.0`

    Args:
        tool_name (str):
        version (str):
        format_ (PipelineToolsRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PipelineTool]
    """

    kwargs = _get_kwargs(
        tool_name=tool_name,
        version=version,
        format_=format_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    tool_name: str,
    version: str,
    *,
    client: AuthenticatedClient,
    format_: PipelineToolsRetrieveFormat | Unset = UNSET,
) -> PipelineTool | None:
    """Retrieves pipeline tool details for the given pipeline version
    Example:
    ---
    `/pipeline-tools/interproscan/5.19-58.0`

    Args:
        tool_name (str):
        version (str):
        format_ (PipelineToolsRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PipelineTool
    """

    return (
        await asyncio_detailed(
            tool_name=tool_name,
            version=version,
            client=client,
            format_=format_,
        )
    ).parsed
