from itertools import chain
import logging
from typing import Optional

logger = logging.getLogger(__name__)

from mgnipy.V2.mixins import ResultsHandler


class MGnifyMetadata(ResultsHandler):

    def __init__(
        self,
        results: dict[int, list[dict]] | None = None,
        id_label: Optional[str] = None,
    ):
        # init results
        self._results = results
        self._id_label = id_label

    @property
    def results(self) -> dict[int, list[dict]]:
        """
        Get the retrieved metadata results, if available.
        Results are stored in a dictionary with request number (e.g. page number) as keys.
        """
        return self._results

    def _unpageinate_results(self, data: Optional[dict] = None) -> chain:
        """
        Flattening the results into a single iterator of records.
        If paginated results are stored in a dictionary with page numbers as keys,
        this method will extract the records from all pages and combine them into a single iterable sequence.

        Returns
        -------
        chain
            An iterator that yields individual metadata records from all pages.
        """
        logger.debug("Flattening paginated results")
        _data = data or self.results

        def _page_to_records(page):
            if page is None:
                return []
            if isinstance(page, list):
                return page
            if isinstance(page, dict):
                return [page]
            return [page]

        return chain.from_iterable(_page_to_records(v) for v in _data.values())

    @property
    def records(self) -> Optional[chain]:
        """
        Get an iterator of individual metadata records from the retrieved results, if available.
        This property provides a convenient way to access the metadata records without needing to handle pagination.

        Returns
        -------
        chain or None
            An iterator that yields individual metadata records if results are available, otherwise None.
        """
        if self.results is None:
            logger.warning(".results is None. No record iterator available")
            return None
        logger.debug("Returning record iterator")
        return self._unpageinate_results()

    @property
    def ids(self) -> Optional[list[str]]:
        """Get the list of identifiers from the current results.

        Returns
        -------
        list[str] or None
            List of identifiers (accessions, etc.), or ``None`` if no results.

        Examples
        --------
        >>> from mgnipy.V2.core import MGnifier  # doctest: +SKIP
        >>> query = MGnifier("studies")  # doctest: +SKIP
        >>> query.get()  # doctest: +SKIP
        >>> ids = query.metadata.ids  # doctest: +SKIP
        """
        if self.results is None:
            logger.warning(
                "No attempts for results to be retieved yet (e.g., .get(), .page()), so no accessions/ids available."
            )
            return None

        try:
            return [record[self._id_label] for record in self._unpageinate_results()]
        except KeyError as exc:
            raise KeyError(
                f"Identifier key '{self._id_label}' not found in results for resource '{self.resource}'. Cannot extract accessions/ids. Check .results"
            ) from exc

    def _resolve_id_param(
        self, key: int | str, param_name: Optional[str] = None
    ) -> dict:
        """Resolve an identifier parameter by index or value.

        Parameters
        ----------
        key : int or str
            Integer position in the results, or a string identifier value
            (e.g., accession, biome lineage).

        Returns
        -------
        dict
            Dictionary with the identifier parameter key and its value.

        Examples
        --------
        >>> from mgnipy.V2.core import MGnifier  # doctest: +SKIP
        >>> query = MGnifier("studies")  # doctest: +SKIP
        >>> query.get()  # doctest: +SKIP
        >>> param_dict = query._resolve_id_param(0)  # doctest: +SKIP
        """

        if not param_name:
            param_name = self._id_label

        # allow index-based access
        if self.ids is not None and isinstance(key, int):
            return {param_name: self.ids[key]}
        # or by accession/biome_lineage/ids string directly
        if self.ids is not None and key in self.ids:
            return {param_name: key}

        raise KeyError(
            f"Invalid key: {key}. "
            "Key must be an integer index, or a valid id string. "
            f"Accession/id/biome_lineage must exist in`.ids`: {self.ids}"
        )

    @property
    def pages(self) -> Optional[int]:
        """
        The pages available in the results, if any.
        This is determined by the keys of the results dictionary,
        which represent page numbers.

        Returns
        -------
        list[int]
            A list of page numbers available in the results.
        """
        if self.results is None:
            logger.warning(".results is None. No pages available.")
            return []
        return list(self.results.keys())
