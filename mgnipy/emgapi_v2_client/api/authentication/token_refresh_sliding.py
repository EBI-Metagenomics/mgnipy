from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import (
    AuthenticatedClient,
    Client,
)
from ...models.webin_token_refresh_request import WebinTokenRefreshRequest
from ...models.webin_token_response import WebinTokenResponse
from ...types import Response


def _get_kwargs(
    *,
    body: WebinTokenRefreshRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/metagenomics/api/v2/auth/sliding/refresh",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> WebinTokenResponse | None:
    if response.status_code == 200:
        response_200 = WebinTokenResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[WebinTokenResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: WebinTokenRefreshRequest,
) -> Response[WebinTokenResponse]:
    """Refresh an authentication token to increase its validity duration.

     If a token's expiry has passed, but its (longer) refresh expiry remains valid, this endpoint can be
    used to fetch a replacement token without logging in again.

    Args:
        body (WebinTokenRefreshRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[WebinTokenResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: WebinTokenRefreshRequest,
) -> WebinTokenResponse | None:
    """Refresh an authentication token to increase its validity duration.

     If a token's expiry has passed, but its (longer) refresh expiry remains valid, this endpoint can be
    used to fetch a replacement token without logging in again.

    Args:
        body (WebinTokenRefreshRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        WebinTokenResponse
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: WebinTokenRefreshRequest,
) -> Response[WebinTokenResponse]:
    """Refresh an authentication token to increase its validity duration.

     If a token's expiry has passed, but its (longer) refresh expiry remains valid, this endpoint can be
    used to fetch a replacement token without logging in again.

    Args:
        body (WebinTokenRefreshRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[WebinTokenResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: WebinTokenRefreshRequest,
) -> WebinTokenResponse | None:
    """Refresh an authentication token to increase its validity duration.

     If a token's expiry has passed, but its (longer) refresh expiry remains valid, this endpoint can be
    used to fetch a replacement token without logging in again.

    Args:
        body (WebinTokenRefreshRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        WebinTokenResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
