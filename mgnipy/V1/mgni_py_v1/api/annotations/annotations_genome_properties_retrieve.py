from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import (
    AuthenticatedClient,
    Client,
)
from ...models.annotations_genome_properties_retrieve_format import (
    AnnotationsGenomePropertiesRetrieveFormat,
)
from ...models.genome_property import GenomeProperty
from ...types import (
    UNSET,
    Response,
    Unset,
)


def _get_kwargs(
    accession: str,
    *,
    format_: AnnotationsGenomePropertiesRetrieveFormat | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_format_: str | Unset = UNSET
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/annotations/genome-properties/{accession}".format(
            accession=quote(str(accession), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GenomeProperty | None:
    if response.status_code == 200:
        response_200 = GenomeProperty.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GenomeProperty]:
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
    format_: AnnotationsGenomePropertiesRetrieveFormat | Unset = UNSET,
) -> Response[GenomeProperty]:
    """Retrieves a Genome property
    Example:
    ---
    `/annotations/genome-properties/GenProp0063`

    Args:
        accession (str):
        format_ (AnnotationsGenomePropertiesRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GenomeProperty]
    """

    kwargs = _get_kwargs(
        accession=accession,
        format_=format_,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    accession: str,
    *,
    client: AuthenticatedClient,
    format_: AnnotationsGenomePropertiesRetrieveFormat | Unset = UNSET,
) -> GenomeProperty | None:
    """Retrieves a Genome property
    Example:
    ---
    `/annotations/genome-properties/GenProp0063`

    Args:
        accession (str):
        format_ (AnnotationsGenomePropertiesRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GenomeProperty
    """

    return sync_detailed(
        accession=accession,
        client=client,
        format_=format_,
    ).parsed


async def asyncio_detailed(
    accession: str,
    *,
    client: AuthenticatedClient,
    format_: AnnotationsGenomePropertiesRetrieveFormat | Unset = UNSET,
) -> Response[GenomeProperty]:
    """Retrieves a Genome property
    Example:
    ---
    `/annotations/genome-properties/GenProp0063`

    Args:
        accession (str):
        format_ (AnnotationsGenomePropertiesRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GenomeProperty]
    """

    kwargs = _get_kwargs(
        accession=accession,
        format_=format_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    accession: str,
    *,
    client: AuthenticatedClient,
    format_: AnnotationsGenomePropertiesRetrieveFormat | Unset = UNSET,
) -> GenomeProperty | None:
    """Retrieves a Genome property
    Example:
    ---
    `/annotations/genome-properties/GenProp0063`

    Args:
        accession (str):
        format_ (AnnotationsGenomePropertiesRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GenomeProperty
    """

    return (
        await asyncio_detailed(
            accession=accession,
            client=client,
            format_=format_,
        )
    ).parsed
