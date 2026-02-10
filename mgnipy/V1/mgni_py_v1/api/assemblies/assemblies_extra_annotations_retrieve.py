from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.assemblies_extra_annotations_retrieve_format import (
    AssembliesExtraAnnotationsRetrieveFormat,
)
from ...models.assembly_extra_annotation import AssemblyExtraAnnotation
from ...types import UNSET, Response, Unset


def _get_kwargs(
    accession: str,
    alias: str,
    *,
    format_: AssembliesExtraAnnotationsRetrieveFormat | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_format_: str | Unset = UNSET
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/assemblies/{accession}/extra-annotations/{alias}".format(
            accession=quote(str(accession), safe=""),
            alias=quote(str(alias), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> AssemblyExtraAnnotation | None:
    if response.status_code == 200:
        response_200 = AssemblyExtraAnnotation.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[AssemblyExtraAnnotation]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    accession: str,
    alias: str,
    *,
    client: AuthenticatedClient,
    format_: AssembliesExtraAnnotationsRetrieveFormat | Unset = UNSET,
) -> Response[AssemblyExtraAnnotation]:
    """List a queryset.

    Args:
        accession (str):
        alias (str):
        format_ (AssembliesExtraAnnotationsRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AssemblyExtraAnnotation]
    """

    kwargs = _get_kwargs(
        accession=accession,
        alias=alias,
        format_=format_,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    accession: str,
    alias: str,
    *,
    client: AuthenticatedClient,
    format_: AssembliesExtraAnnotationsRetrieveFormat | Unset = UNSET,
) -> AssemblyExtraAnnotation | None:
    """List a queryset.

    Args:
        accession (str):
        alias (str):
        format_ (AssembliesExtraAnnotationsRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AssemblyExtraAnnotation
    """

    return sync_detailed(
        accession=accession,
        alias=alias,
        client=client,
        format_=format_,
    ).parsed


async def asyncio_detailed(
    accession: str,
    alias: str,
    *,
    client: AuthenticatedClient,
    format_: AssembliesExtraAnnotationsRetrieveFormat | Unset = UNSET,
) -> Response[AssemblyExtraAnnotation]:
    """List a queryset.

    Args:
        accession (str):
        alias (str):
        format_ (AssembliesExtraAnnotationsRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AssemblyExtraAnnotation]
    """

    kwargs = _get_kwargs(
        accession=accession,
        alias=alias,
        format_=format_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    accession: str,
    alias: str,
    *,
    client: AuthenticatedClient,
    format_: AssembliesExtraAnnotationsRetrieveFormat | Unset = UNSET,
) -> AssemblyExtraAnnotation | None:
    """List a queryset.

    Args:
        accession (str):
        alias (str):
        format_ (AssembliesExtraAnnotationsRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AssemblyExtraAnnotation
    """

    return (
        await asyncio_detailed(
            accession=accession,
            alias=alias,
            client=client,
            format_=format_,
        )
    ).parsed
