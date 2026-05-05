import inspect
import logging
import os
from copy import deepcopy
from math import ceil
from types import ModuleType
from typing import (
    Any,
    Optional,
)
from urllib.parse import urlencode

import httpx

from mgnipy._shared_helpers.parsers import (
    get_docstring,
    parse_docstring,
)
from mgnipy.V2.endpoints import (
    LIST_ENDPOINTS,
    PRIVATE_ENDPOINTS,
)


class DescribeEmgapiModule:

    def __init__(self, endpoint_module: Optional[ModuleType] = None):
        self.endpoint_module = endpoint_module

        self.default_page_size: int = 25

    def list_supported_params(self) -> list[str]:
        """
        Lists supported keyword arguments for the endpoint module.

        Returns
        -------
        list of str
            List of supported keyword argument names.
        """
        sig = inspect.signature(self.endpoint_module._get_kwargs)
        return list(sig.parameters.keys())

    def validate_endpoint_kwargs(self, **kwargs) -> dict[str, Any]:
        """
        Validates the provided keyword arguments against the supported parameters of the endpoint module.

        Parameters
        ----------
        **kwargs
            Keyword arguments to validate.

        Returns
        -------
        dict of str to Any
            The validated keyword arguments.

        Raises
        ------
        ValueError
            If any provided keyword argument is not supported by the endpoint module.
        """
        return self.endpoint_module._get_kwargs(**kwargs)

    @property
    def emgapi_resource(self) -> Optional[str]:
        """
        Retrieves the name of the endpoint resource based on the endpoint module.

        Returns
        -------
        str or None
            The name of the endpoint resource, or None if the endpoint module is not set.
        """
        return os.path.basename(os.path.dirname(self.endpoint_module.__file__))

    def sub_url(self, **kwargs) -> Optional[str]:
        """
        Constructs the sub-URL for the endpoint based on the current parameters.

        Returns
        -------
        str or None
            The constructed sub-URL, or None if the endpoint module is not set.
        """
        _kwargs = self.validate_endpoint_kwargs(**kwargs)
        _end_url: str = _kwargs.get(
            "url", f"/metagenomics/api/v2/{self.emgapi_resource}/"
        ).strip("/")

        return _end_url

    def resolve_query_string(self, **kwargs) -> str:
        """
        Resolves the query string for the endpoint based on the current parameters.

        Parameters
        ----------
        **kwargs
            Keyword arguments to validate and include in the query string.

        Returns
        -------
        str
            The resolved query string.
        """
        _kwargs = self.validate_endpoint_kwargs(**kwargs)

        # get validated params if any
        params = _kwargs.get("params", {})

        # encode params for url
        return urlencode(params, doseq=True)

    def url_path(self, **kwargs) -> str:
        """
        Constructs the full URL path for the endpoint based on the current parameters.

        Parameters
        ----------
        **kwargs
            Keyword arguments to validate and include in the URL construction.

        Returns
        -------
        str
            The constructed URL path.
        """
        _end_url = self.sub_url(**kwargs)
        query_string = self.resolve_query_string(**kwargs)

        return f"{_end_url}?{query_string}" if query_string else _end_url

    @property
    def emgapi_docs(self) -> str:
        return get_docstring(self.endpoint_module, "sync")

    def describe_endpoint(self, as_dict: bool = False) -> dict[str, str] | None:
        return parse_docstring(self.emgapi_docs, as_dict=as_dict)

    @property
    def is_private(self) -> bool:
        """Checks if the endpoint module corresponds to a private only endpoint."""
        return self.endpoint_module in PRIVATE_ENDPOINTS

    @property
    def is_list_endpoint(self) -> bool:
        """Checks if the endpoint module corresponds to a list endpoint."""
        return self.endpoint_module in LIST_ENDPOINTS.values()

    def get_num_items(
        self, client: httpx.Client, params: Optional[dict] = None
    ) -> Optional[int]:

        _params = deepcopy(params) or {}

        if not self.is_list_endpoint:
            return 1

        _params.update({"page_size": 1})
        with client as c:
            response = self.endpoint_module.sync_detailed(client=c, **_params)

        if response.status_code == 200:
            return response.parsed.to_dict().get("count", 0)
        else:
            logging.warning(
                f"Failed to retrieve count for endpoint {self.emgapi_resource}. Status code: {response.status_code}"
            )

    def get_num_pages(
        self, num_items: Optional[int], page_size: Optional[int] = None
    ) -> Optional[int]:
        """Calculates the total number of pages based on the total count and default page size."""
        if not num_items:
            return None
        ps = page_size or self.default_page_size
        return ceil(num_items / ps)

    def page_param_iter(self, num_pages: int) -> list[dict[str, int]]:
        """Generates a list of parameter dictionaries for each page based on the total number of pages."""
        return [{"page": page} for page in range(1, num_pages + 1)]
