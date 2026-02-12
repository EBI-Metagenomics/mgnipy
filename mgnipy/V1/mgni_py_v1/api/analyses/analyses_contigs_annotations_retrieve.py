from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import (
    AuthenticatedClient,
    Client,
)
from ...models.analyses_contigs_annotations_retrieve_format import (
    AnalysesContigsAnnotationsRetrieveFormat,
)
from ...models.analysis_job_contig import AnalysisJobContig
from ...types import (
    UNSET,
    Response,
    Unset,
)


def _get_kwargs(
    accession: str,
    contig_id: str,
    *,
    format_: AnalysesContigsAnnotationsRetrieveFormat | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_format_: str | Unset = UNSET
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/analyses/{accession}/contigs/{contig_id}/annotations".format(
            accession=quote(str(accession), safe=""),
            contig_id=quote(str(contig_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> AnalysisJobContig | None:
    if response.status_code == 200:
        response_200 = AnalysisJobContig.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[AnalysisJobContig]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    accession: str,
    contig_id: str,
    *,
    client: AuthenticatedClient,
    format_: AnalysesContigsAnnotationsRetrieveFormat | Unset = UNSET,
) -> Response[AnalysisJobContig]:
    """Retrieve a contig GFF file.
    The are 2 flavors for the GFF files:
    - COG,KEGG, Pfam, InterPro and EggNOG annotations
    - antiSMASH
    By default the action will return the 'main one', unless specified using the querystring param
    'antismash=True'
    The GFF file will be parsed with pysam and sliced.
    Example:
    ---
    /analyses/<accession>/<contig_id>/annotation
    ---

    Args:
        accession (str):
        contig_id (str):
        format_ (AnalysesContigsAnnotationsRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AnalysisJobContig]
    """

    kwargs = _get_kwargs(
        accession=accession,
        contig_id=contig_id,
        format_=format_,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    accession: str,
    contig_id: str,
    *,
    client: AuthenticatedClient,
    format_: AnalysesContigsAnnotationsRetrieveFormat | Unset = UNSET,
) -> AnalysisJobContig | None:
    """Retrieve a contig GFF file.
    The are 2 flavors for the GFF files:
    - COG,KEGG, Pfam, InterPro and EggNOG annotations
    - antiSMASH
    By default the action will return the 'main one', unless specified using the querystring param
    'antismash=True'
    The GFF file will be parsed with pysam and sliced.
    Example:
    ---
    /analyses/<accession>/<contig_id>/annotation
    ---

    Args:
        accession (str):
        contig_id (str):
        format_ (AnalysesContigsAnnotationsRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AnalysisJobContig
    """

    return sync_detailed(
        accession=accession,
        contig_id=contig_id,
        client=client,
        format_=format_,
    ).parsed


async def asyncio_detailed(
    accession: str,
    contig_id: str,
    *,
    client: AuthenticatedClient,
    format_: AnalysesContigsAnnotationsRetrieveFormat | Unset = UNSET,
) -> Response[AnalysisJobContig]:
    """Retrieve a contig GFF file.
    The are 2 flavors for the GFF files:
    - COG,KEGG, Pfam, InterPro and EggNOG annotations
    - antiSMASH
    By default the action will return the 'main one', unless specified using the querystring param
    'antismash=True'
    The GFF file will be parsed with pysam and sliced.
    Example:
    ---
    /analyses/<accession>/<contig_id>/annotation
    ---

    Args:
        accession (str):
        contig_id (str):
        format_ (AnalysesContigsAnnotationsRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AnalysisJobContig]
    """

    kwargs = _get_kwargs(
        accession=accession,
        contig_id=contig_id,
        format_=format_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    accession: str,
    contig_id: str,
    *,
    client: AuthenticatedClient,
    format_: AnalysesContigsAnnotationsRetrieveFormat | Unset = UNSET,
) -> AnalysisJobContig | None:
    """Retrieve a contig GFF file.
    The are 2 flavors for the GFF files:
    - COG,KEGG, Pfam, InterPro and EggNOG annotations
    - antiSMASH
    By default the action will return the 'main one', unless specified using the querystring param
    'antismash=True'
    The GFF file will be parsed with pysam and sliced.
    Example:
    ---
    /analyses/<accession>/<contig_id>/annotation
    ---

    Args:
        accession (str):
        contig_id (str):
        format_ (AnalysesContigsAnnotationsRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AnalysisJobContig
    """

    return (
        await asyncio_detailed(
            accession=accession,
            contig_id=contig_id,
            client=client,
            format_=format_,
        )
    ).parsed
