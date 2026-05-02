import inspect
import os
from types import ModuleType
from typing import (
    Any,
    Optional,
)
from urllib.parse import urlencode

from mgnipy._shared_helpers.docstring_parser import (
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
        return self.endpoint_module in PRIVATE_ENDPOINTS.values()

    @property
    def is_list_endpoint(self) -> bool:
        """Checks if the endpoint module corresponds to a list endpoint."""
        return self.endpoint_module in LIST_ENDPOINTS.values()
