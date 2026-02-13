import functools
from bigtree import Tree
from typing import Any, Optional, Literal
from mgnipy.V2.mgni_py_v2 import Client
from mgnipy.V2.mgni_py_v2.api.miscellaneous import list_mgnify_biomes
from mgnipy._shared_helpers.pydantic_help import int_gt_adapter
import pandas as pd

@functools.cache
def planner(
    client, 
    mgni_py_module,
    page_size: int = 25,
    *,
    params: Optional[dict[str, Any]] = None,
    **kwargs
) -> int:
    """
    Get total pages for a given endpoint and parameters

    Parameters
    ----------
    client : Client
        An instance of the MGnipy Client.
    mgni_py_module : module
        The MGnipy module corresponding to the endpoint (e.g. studies, samples).
    page_size : int, optional
        The number of results per page (default is 25).
    params : dict, optional
        Additional parameters to include in the request (default is None).
    **kwargs
        Additional keyword arguments to include in the request. 
        These will be added to the params dictionary.
    
    Returns
    -------
    int
        The total number of pages for the given endpoint and parameters.
    
    Raises
    ------
    ValueError
        If the request fails or if the page size is not greater than 0.
    """
    # validate page size > 0 
    _page_size = int_gt_adapter(page_size)
    # add kwargs to params if provided
    _params = params or {}
    if kwargs:
        _params.update(kwargs)
        # min page and pagesize, 1 since only want result count
        _params.update(dict(
            page=1,
            page_size=1,
        ))
    # make the sync req
    response = mgni_py_module.sync_detailed(
        client=client,
        **_params,
    )
    # check response and calculate total pages based on pg size
    if response.status_code == 200:
        num_results = response.parsed.to_dict()['count']
        return {
            "total_results": num_results,
            "total_pages": num_results // _page_size
        }
    raise ValueError(
        f"Error fetching data: {response.status_code} "
    )

@functools.cache
def previewer(
    client, 
    mgni_py_module,
    page_size: int = 25,
    *,
    params: Optional[dict[str, Any]] = None,
    **kwargs
) -> dict[str, int | pd.DataFrame]:
    """
    Get total pages for a given endpoint and parameters
    and preview the first page as a DataFrame

    Parameters
    ----------
    client : Client
        An instance of the MGnipy Client.
    mgni_py_module : module
        The MGnipy module corresponding to the endpoint (e.g. studies, samples).
    page_size : int, optional
        The number of results per page (default is 25).
    params : dict, optional
        Additional parameters to include in the request (default is None).
    **kwargs
        Additional keyword arguments to include in the request. 
        These will be added to the params dictionary.
    
    Returns
    -------
    dict[str, int | pd.DataFrame]
        The total number of pages for the given endpoint and parameters.
        and a preview of the first page as a DataFrame.
    
    Raises
    ------
    ValueError
        If the request fails or if the page size is not greater than 0.
    """
    # validate page size > 0 
    _page_size = int_gt_adapter(page_size)
    # add kwargs to params if provided
    _params = params or {}
    if kwargs:
        _params.update(kwargs)
        # min page and pagesize, 1 since only want result count
        _params.update(dict(
            page=1,
            page_size=_page_size,
        ))
    # make the sync req
    response = mgni_py_module.sync_detailed(
        client=client,
        **_params,
    )
    # check response and calculate total pages based on pg size
    if response.status_code == 200:
        num_results = response.parsed.to_dict()['count']
        items = response.parsed.to_dict().get('items', [])
        return {
            "total_results": num_results,
            "total_pages": num_results // _page_size,
            "first_page": pd.DataFrame(items)
        }
    raise ValueError(
        f"Error fetching data: {response.status_code} "
    )

