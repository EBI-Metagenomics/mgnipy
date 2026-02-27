from typing import (
    Any,
    List,
    Literal,
    Optional,
)
from bigtree import (
    Tree,
)

from mgnipy.V2.core import Mgnifier
from mgnipy.V2.datasets import DatasetBuilder


class ResourceProxy(Mgnifier):
    """generic"""

    def __init__(
        self,
        resource: str,
        *,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        super().__init__(resource=resource, params=params, **kwargs)


class BiomesProxy(Mgnifier):

    def __init__(self, **kwargs):
        self._tree = None
        super().__init__(resource="biomes", **kwargs)

    # biome-specific methods
    def to_bigtree(self) -> Tree:
        """
        Convert the biomes metadata to a tree structure for visualization or analysis.

        Returns
        -------
        Tree
            A tree representation of the biomes and their relationships.
        """
        if self._results is None:
            raise RuntimeError(
                "No data available to convert to tree. "
                "Please run preview() or get() first."
            )
        # convert to pandas and then to tree
        df = self.to_pandas()
        # TODO generate nodes first
        self._tree = Tree.from_list(df["lineage"], sep=":")
        return self._tree

    def show_tree(
        self,
        method: Literal[
            "compact",
            "show",
            "print",
            "horizontal",
            "hshow",
            "h",
            "hprint",
            "vertical",
            "vshow",
            "v",
            "vprint",
        ] = "compact",
    ):
        if self._tree is None:
            # create tree if not already
            self.to_bigtree()

        if method in ["compact", "show", "print"]:
            # TODO print_tree(self._tree)
            self._tree.show()
        elif method in ["horizontal", "hshow", "h", "hprint"]:
            self._tree.hshow()
        elif method in ["vertical", "vshow", "v", "vprint"]:
            self._tree.vshow()
        else:
            raise ValueError(
                f"Invalid method: {method}. "
                "Supported methods: 'compact', 'show', 'print', "
                "'horizontal', 'hshow', 'h', 'hprint', "
                "'vertical', 'vshow', 'v', 'vprint'."
            )


class StudiesProxy(Mgnifier):

    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        super().__init__(resource="studies", params=params, **kwargs)


class AnalysesProxy(Mgnifier):
    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        super().__init__(resource="analyses", params=params, **kwargs)

    def __getitem__(self, key) -> List[dict] | dict:
        """TODO: docstring"""

        df = self.to_pandas()
        df_as_list = df.to_dict(orient="records")

        # get dataset builder(s)
        if isinstance(key, str) and self._accessions and key in self._accessions:
            return DatasetBuilder(accession=key)
        elif isinstance(key, int) and self._accessions:
            return DatasetBuilder(accession=df_as_list[key]["accession"])
        elif isinstance(key, slice) and self._accessions:
            return [
                DatasetBuilder(accession=record["accession"])
                for record in df_as_list[key]
            ]
        elif self._accessions is None:
            raise RuntimeError(
                "No accessions available for indexing. "
                "E.g., run preview() or get() first to retrieve metadata and accessions."
            )
        else:
            raise KeyError(
                f"Invalid key: {key}. "
                "Key must be an integer index, a slice, or a valid accession string."
            )


class SamplesProxy(Mgnifier):
    def __init__(
        self,
        study_accession: str,
        *,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        super().__init__(
            resource="samples", accession=study_accession, params=params, **kwargs
        )


class GenomesProxy(Mgnifier):
    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        # TODO
        super().__init__(resource="genomes", params=params, **kwargs)
