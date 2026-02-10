from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.analysis_get_mgnify_analysis_with_annotations_of_type_3506390em_gnify_functional_analysis_annotation_type import (
    AnalysisGetMgnifyAnalysisWithAnnotationsOfType3506390EMGnifyFunctionalAnalysisAnnotationType,
)
from ...models.ninja_pagination_response_schema_m_gnify_analysis_typed_annotation import (
    NinjaPaginationResponseSchemaMGnifyAnalysisTypedAnnotation,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    accession: str,
    annotation_type: AnalysisGetMgnifyAnalysisWithAnnotationsOfType3506390EMGnifyFunctionalAnalysisAnnotationType,
    *,
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

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
        "url": "/metagenomics/api/v2/analyses/{accession}/annotations/{annotation_type}".format(
            accession=quote(str(accession), safe=""),
            annotation_type=quote(str(annotation_type), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> NinjaPaginationResponseSchemaMGnifyAnalysisTypedAnnotation | None:
    if response.status_code == 200:
        response_200 = NinjaPaginationResponseSchemaMGnifyAnalysisTypedAnnotation.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[NinjaPaginationResponseSchemaMGnifyAnalysisTypedAnnotation]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    accession: str,
    annotation_type: AnalysisGetMgnifyAnalysisWithAnnotationsOfType3506390EMGnifyFunctionalAnalysisAnnotationType,
    *,
    client: AuthenticatedClient,
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,
) -> Response[NinjaPaginationResponseSchemaMGnifyAnalysisTypedAnnotation]:
    """Get a named set of annotations for a MGnify analysis by accession.

     List the annotations of a given type for a MGnify analysis referred to by its accession.

    Args:
        accession (str):
        annotation_type (AnalysisGetMgnifyAnalysisWithAnnotationsOfType3506390EMGnifyFunctionalAna
            lysisAnnotationType):
        page (int | Unset):  Default: 1.
        page_size (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[NinjaPaginationResponseSchemaMGnifyAnalysisTypedAnnotation]
    """

    kwargs = _get_kwargs(
        accession=accession,
        annotation_type=annotation_type,
        page=page,
        page_size=page_size,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    accession: str,
    annotation_type: AnalysisGetMgnifyAnalysisWithAnnotationsOfType3506390EMGnifyFunctionalAnalysisAnnotationType,
    *,
    client: AuthenticatedClient,
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,
) -> NinjaPaginationResponseSchemaMGnifyAnalysisTypedAnnotation | None:
    """Get a named set of annotations for a MGnify analysis by accession.

     List the annotations of a given type for a MGnify analysis referred to by its accession.

    Args:
        accession (str):
        annotation_type (AnalysisGetMgnifyAnalysisWithAnnotationsOfType3506390EMGnifyFunctionalAna
            lysisAnnotationType):
        page (int | Unset):  Default: 1.
        page_size (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        NinjaPaginationResponseSchemaMGnifyAnalysisTypedAnnotation
    """

    return sync_detailed(
        accession=accession,
        annotation_type=annotation_type,
        client=client,
        page=page,
        page_size=page_size,
    ).parsed


async def asyncio_detailed(
    accession: str,
    annotation_type: AnalysisGetMgnifyAnalysisWithAnnotationsOfType3506390EMGnifyFunctionalAnalysisAnnotationType,
    *,
    client: AuthenticatedClient,
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,
) -> Response[NinjaPaginationResponseSchemaMGnifyAnalysisTypedAnnotation]:
    """Get a named set of annotations for a MGnify analysis by accession.

     List the annotations of a given type for a MGnify analysis referred to by its accession.

    Args:
        accession (str):
        annotation_type (AnalysisGetMgnifyAnalysisWithAnnotationsOfType3506390EMGnifyFunctionalAna
            lysisAnnotationType):
        page (int | Unset):  Default: 1.
        page_size (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[NinjaPaginationResponseSchemaMGnifyAnalysisTypedAnnotation]
    """

    kwargs = _get_kwargs(
        accession=accession,
        annotation_type=annotation_type,
        page=page,
        page_size=page_size,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    accession: str,
    annotation_type: AnalysisGetMgnifyAnalysisWithAnnotationsOfType3506390EMGnifyFunctionalAnalysisAnnotationType,
    *,
    client: AuthenticatedClient,
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,
) -> NinjaPaginationResponseSchemaMGnifyAnalysisTypedAnnotation | None:
    """Get a named set of annotations for a MGnify analysis by accession.

     List the annotations of a given type for a MGnify analysis referred to by its accession.

    Args:
        accession (str):
        annotation_type (AnalysisGetMgnifyAnalysisWithAnnotationsOfType3506390EMGnifyFunctionalAna
            lysisAnnotationType):
        page (int | Unset):  Default: 1.
        page_size (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        NinjaPaginationResponseSchemaMGnifyAnalysisTypedAnnotation
    """

    return (
        await asyncio_detailed(
            accession=accession,
            annotation_type=annotation_type,
            client=client,
            page=page,
            page_size=page_size,
        )
    ).parsed
