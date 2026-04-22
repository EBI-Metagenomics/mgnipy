from typing import (
    Any,
    List,
    Literal,
    Optional,
)

from bigtree import (
    Tree,
)

from mgnipy._models.CONSTANTS import SupportedEndpoints
from mgnipy.V2.core import MGnifier
from mgnipy.V2.mixins import (
    DetailNavigationMixin,
    RelatedNavigationMixin,
)


class MGnifyList(MGnifier, DetailNavigationMixin):
    """generic"""

    def __init__(
        self,
        resource: str,
        *,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        # init mgnifier
        super().__init__(
            resource=resource,
            params=params,
            **kwargs,
        )

        self.resource = SupportedEndpoints.validate(resource)


# FIX THIS
class MGnifyDetail(MGnifier, RelatedNavigationMixin):
    def __init__(
        self,
        *,
        resource: Optional[str] = None,
        accession: Optional[str] = None,
        biome_lineage: Optional[str] = None,
    ):

        self._relationships = self.list_relationships()

        if accession and biome_lineage:
            raise ValueError("Cannot specify both accession and biome_lineage.")
        elif accession:
            self.accession = accession
            super().__init__(resource=resource, accession=accession)
        elif biome_lineage:
            self.lineage = biome_lineage
            super().__init__(
                resource=resource,
                biome_lineage=biome_lineage,
            )
        else:
            raise ValueError("Must specify either accession or biome_lineage.")

        self.explain()  # TODO remove after testing
        self.get()

    def describe_relationships(self):
        pass


class Analyses(MGnifyList):
    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):

        super().__init__(resource="analyses", params=params, **kwargs)


class Runs(MGnifyList):
    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):

        super().__init__(resource="runs", params=params, **kwargs)


class Samples(MGnifyList):
    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):

        super().__init__(resource="samples", params=params, **kwargs)


class Studies(MGnifyList):

    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        super().__init__(resource="studies", params=params, **kwargs)


class Biomes(MGnifyList):

    def __init__(self, **kwargs):
        super().__init__(resource="biomes", **kwargs)

    @property
    def lineages(self) -> List[str]:
        if self._results is None:
            raise RuntimeError(
                "No data available to get lineages. Please run get() first."
            )
        return self.results_ids

    @property
    def tree(self) -> Tree:
        """
        Convert the biomes metadata to a tree structure for visualization or analysis.

        Returns
        -------
        Tree
            A tree representation of the biomes and their relationships.
        """
        # TODO generate nodes first
        return Tree.from_list(self.lineages, sep=":")

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
        if method in ["compact", "show", "print"]:
            # TODO print_tree(self._tree)
            self.tree.show()
        elif method in ["horizontal", "hshow", "h", "hprint"]:
            self.tree.hshow()
        elif method in ["vertical", "vshow", "v", "vprint"]:
            self.tree.vshow()
        else:
            raise ValueError(
                f"Invalid method: {method}. "
                "Supported methods: 'compact', 'show', 'print', "
                "'horizontal', 'hshow', 'h', 'hprint', "
                "'vertical', 'vshow', 'v', 'vprint'."
            )


class Assemblies(MGnifyList):
    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        super().__init__(resource="assemblies", params=params, **kwargs)


class Genomes(MGnifyList):
    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        # TODO
        super().__init__(resource="genomes", params=params, **kwargs)


class Publications(MGnifyList):
    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        super().__init__(resource="publications", params=params, **kwargs)


class Catalogues(MGnifyList):
    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        super().__init__(resource="catalogues", params=params, **kwargs)


class StudyDetail(MGnifyDetail):
    def __init__(
        self,
        accession: str,
    ):
        super().__init__(resource="study", accession=accession)


class SampleDetail(MGnifyDetail):
    def __init__(
        self,
        accession: str,
    ):
        super().__init__(resource="sample", accession=accession)


class RunDetail(MGnifyDetail):
    def __init__(
        self,
        accession: str,
    ):
        super().__init__(resource="run", accession=accession)


class AnalysisDetail(MGnifyDetail):
    def __init__(
        self,
        accession: str,
    ):
        super().__init__(resource="analysis", accession=accession)


class GenomeDetail(MGnifyDetail):
    def __init__(
        self,
        accession: str,
    ):
        super().__init__(resource="genome", accession=accession)


class AssemblyDetail(MGnifyDetail):
    def __init__(
        self,
        accession: str,
    ):
        super().__init__(resource="assembly", accession=accession)


class BiomeDetail(MGnifyDetail):
    def __init__(
        self,
        biome_lineage: str,
    ):
        super().__init__(resource="biome", biome_lineage=biome_lineage)


class PublicationDetail(MGnifyDetail):
    def __init__(
        self,
        accession: str,
    ):
        super().__init__(resource="publication", accession=accession)


class CatalogueDetail(MGnifyDetail):
    def __init__(
        self,
        catalogue_id: str,
    ):
        super().__init__(resource="catalogue", catalogue_id=catalogue_id)
