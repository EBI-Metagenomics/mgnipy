from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import (
    AuthenticatedClient,
    Client,
)
from ...models.experiment_types import ExperimentTypes
from ...models.ninja_pagination_response_schema_analysed_run import (
    NinjaPaginationResponseSchemaAnalysedRun,
)
from ...types import (
    UNSET,
    Response,
    Unset,
)


def _get_kwargs(
    *,
    has_experiment_type: ExperimentTypes | None | Unset = UNSET,
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_has_experiment_type: None | str | Unset
    if isinstance(has_experiment_type, Unset):
        json_has_experiment_type = UNSET
    elif isinstance(has_experiment_type, ExperimentTypes):
        json_has_experiment_type = has_experiment_type.value
    else:
        json_has_experiment_type = has_experiment_type
    params["has_experiment_type"] = json_has_experiment_type

    params["page"] = page

    json_page_size: int | None | Unset
    if isinstance(page_size, Unset):
        json_page_size = UNSET
    else:
        json_page_size = page_size
    params["page_size"] = json_page_size

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/metagenomics/api/v2/runs/",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> NinjaPaginationResponseSchemaAnalysedRun | None:
    if response.status_code == 200:
        response_200 = NinjaPaginationResponseSchemaAnalysedRun.from_dict(
            response.json()
        )

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[NinjaPaginationResponseSchemaAnalysedRun]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    has_experiment_type: ExperimentTypes | None | Unset = UNSET,
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,
) -> Response[NinjaPaginationResponseSchemaAnalysedRun]:
    """List all analysed runs

     List all analysed runs in the MGnify database.

    Args:
        has_experiment_type (ExperimentTypes | None | Unset): If set, will only show runs with the
            specified experiment type
        page (int | Unset):  Default: 1.
        page_size (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[NinjaPaginationResponseSchemaAnalysedRun]
    """

    kwargs = _get_kwargs(
        has_experiment_type=has_experiment_type,
        page=page,
        page_size=page_size,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    has_experiment_type: ExperimentTypes | None | Unset = UNSET,
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,
) -> NinjaPaginationResponseSchemaAnalysedRun | None:
    """List all analysed runs

     List all analysed runs in the MGnify database.

    Args:
        has_experiment_type (ExperimentTypes | None | Unset): If set, will only show runs with the
            specified experiment type
        page (int | Unset):  Default: 1.
        page_size (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        NinjaPaginationResponseSchemaAnalysedRun
    """

    return sync_detailed(
        client=client,
        has_experiment_type=has_experiment_type,
        page=page,
        page_size=page_size,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    has_experiment_type: ExperimentTypes | None | Unset = UNSET,
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,
) -> Response[NinjaPaginationResponseSchemaAnalysedRun]:
    """List all analysed runs

     List all analysed runs in the MGnify database.

    Args:
        has_experiment_type (ExperimentTypes | None | Unset): If set, will only show runs with the
            specified experiment type
        page (int | Unset):  Default: 1.
        page_size (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[NinjaPaginationResponseSchemaAnalysedRun]
    """

    kwargs = _get_kwargs(
        has_experiment_type=has_experiment_type,
        page=page,
        page_size=page_size,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    has_experiment_type: ExperimentTypes | None | Unset = UNSET,
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,
) -> NinjaPaginationResponseSchemaAnalysedRun | None:
    """List all analysed runs

     List all analysed runs in the MGnify database.

    Args:
        has_experiment_type (ExperimentTypes | None | Unset): If set, will only show runs with the
            specified experiment type
        page (int | Unset):  Default: 1.
        page_size (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        NinjaPaginationResponseSchemaAnalysedRun
    """

    return (
        await asyncio_detailed(
            client=client,
            has_experiment_type=has_experiment_type,
            page=page,
            page_size=page_size,
        )
    ).parsed
