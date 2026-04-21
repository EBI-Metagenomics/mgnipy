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
from mgnipy.emgapi_v2_client.api.analyses import (
    analysis_get_mgnify_analysis_with_annotations,
)
from mgnipy.emgapi_v2_client.api.assemblies import (
    list_analyses_for_assembly,
    list_genome_links_for_assembly,
)
from mgnipy.emgapi_v2_client.api.runs import (
    list_runs_analyses,
)
from mgnipy.emgapi_v2_client.api.samples import (
    list_sample_runs,
)
from mgnipy.emgapi_v2_client.api.studies import (
    list_mgnify_studies,
    list_mgnify_study_analyses,
    list_mgnify_study_samples,
)
from mgnipy.V2.core import MGnifier

# I think this kinda follows the openapi "Links" on the right of the docs?
SUPPORTED_RELATIONSHIPS = {
    SupportedEndpoints.BIOME: {SupportedEndpoints.STUDIES: list_mgnify_studies},
    SupportedEndpoints.STUDY: {
        SupportedEndpoints.ANALYSES: list_mgnify_study_analyses,
        SupportedEndpoints.SAMPLES: list_mgnify_study_samples,
    },
    SupportedEndpoints.SAMPLE: {SupportedEndpoints.RUNS: list_sample_runs},
    SupportedEndpoints.RUN: {SupportedEndpoints.ANALYSES: list_runs_analyses},
    SupportedEndpoints.ASSEMBLY: {
        SupportedEndpoints.ANALYSES: list_analyses_for_assembly,
        SupportedEndpoints.GENOMES: list_genome_links_for_assembly,
    },
    SupportedEndpoints.ANALYSIS: {
        "annotations": analysis_get_mgnify_analysis_with_annotations
    },
}


class MGnifyList(MGnifier):
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


class MGnifyDetail(MGnifier):
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

    def list_relationships(self) -> list[str]:
        return [endpoint.value for endpoint in SUPPORTED_RELATIONSHIPS[self.resource]]

    def describe_relationships(self):
        pass

    def __getattr__(self, name: str):
        if name in self._relationships:

            _name = SupportedEndpoints.validate(name)

            # init via clone
            list_proxy = self._clone()

            # init resource proxy
            list_proxy.endpoint_module = SUPPORTED_RELATIONSHIPS[self.resource][_name]

            return list_proxy


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
        return self.results_biome_lineages

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
