from typing import (
    Any,
    Literal,
    Optional,
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
from mgnipy.V2.query_set import QuerySet

# I think this kinda follows the openapi "Links" on the right of the docs?
SUPPORTED_RELATIONSHIPS = {
    SupportedEndpoints.BIOMES: {SupportedEndpoints.STUDIES: list_mgnify_studies},
    SupportedEndpoints.MISCELLANEOUS: {SupportedEndpoints.STUDIES: list_mgnify_studies},
    SupportedEndpoints.STUDIES: {
        SupportedEndpoints.ANALYSES: list_mgnify_study_analyses,
        SupportedEndpoints.SAMPLES: list_mgnify_study_samples,
    },
    SupportedEndpoints.SAMPLES: {SupportedEndpoints.RUNS: list_sample_runs},
    SupportedEndpoints.RUNS: {SupportedEndpoints.ANALYSES: list_runs_analyses},
    SupportedEndpoints.ASSEMBLIES: {
        SupportedEndpoints.ANALYSES: list_analyses_for_assembly,
        SupportedEndpoints.GENOMES: list_genome_links_for_assembly,
    },
    SupportedEndpoints.ANALYSES: {
        "annotations": analysis_get_mgnify_analysis_with_annotations
    },
}


class MGnifier(QuerySet):
    """
    MGnifier is the main class representing a queryable MGnify resource.
    It provides methods for fetching and navigating data from the MGnify API.
    """

    def __init__(
        self,
        resource: Literal[
            "biomes",
            "biome",
            "studies",
            "study",
            "samples",
            "sample",
            "runs",
            "run",
            "genomes",
            "genome",
            "analyses",
            "analysis",
            "assemblies",
            "assembly",
        ],
        *,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        super().__init__(resource=resource, params=params, **kwargs)
