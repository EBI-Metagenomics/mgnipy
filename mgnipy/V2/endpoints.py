from mgnipy._models.CONSTANTS import SupportedEndpoints
from mgnipy.emgapi_v2_client.api.analyses import (
    analysis_get_mgnify_analysis_with_annotations,
    get_mgnify_analysis,
    list_mgnify_analyses,
)
from mgnipy.emgapi_v2_client.api.assemblies import (
    get_assembly,
    list_analyses_for_assembly,
    list_assemblies,
    list_genome_links_for_assembly,
)
from mgnipy.emgapi_v2_client.api.genomes import (
    get_genome_catalogue,
    get_mgnify_genome,
    list_genome_catalogues,
    list_mgnify_genomes,
)
from mgnipy.emgapi_v2_client.api.miscellaneous import list_mgnify_biomes
from mgnipy.emgapi_v2_client.api.private_data import list_private_mgnify_studies
from mgnipy.emgapi_v2_client.api.publications import (
    get_mgnify_publication,
    list_mgnify_publications,
)
from mgnipy.emgapi_v2_client.api.runs import (
    get_analysed_run,
    list_analysed_runs,
    list_runs_analyses,
)
from mgnipy.emgapi_v2_client.api.samples import (
    get_mgnify_sample,
    list_mgnify_samples,
    list_sample_runs,
)
from mgnipy.emgapi_v2_client.api.studies import (
    get_mgnify_study,
    list_mgnify_studies,
    list_mgnify_study_analyses,
    list_mgnify_study_publications,
    list_mgnify_study_samples,
)

LIST_ENDPOINTS: dict[SupportedEndpoints, callable] = {
    SupportedEndpoints.BIOMES: list_mgnify_biomes,  # get all biomes, filtering option
    SupportedEndpoints.STUDIES: list_mgnify_studies,  # get all studies, filtering option
    SupportedEndpoints.SAMPLES: list_mgnify_samples,  # get all samples, filtering option or with study acc
    SupportedEndpoints.RUNS: list_analysed_runs,  # get all runs, filtering option or with sample acc
    SupportedEndpoints.ANALYSES: list_mgnify_analyses,  # get all analyses, NO FILTERING OPTION, but with study or assem acc
    SupportedEndpoints.GENOMES: list_mgnify_genomes,  # listing all genomes, NO FILTERING OPTION but with assem acc
    SupportedEndpoints.ASSEMBLIES: list_assemblies,  # listing all assemblies, no filtering TODO more info?
    SupportedEndpoints.PUBLICATIONS: list_mgnify_publications,
    SupportedEndpoints.CATALOGUES: list_genome_catalogues,  # not really a list endpoint but fits better here than acc detail
    SupportedEndpoints.PRIVATE_STUDIES: list_private_mgnify_studies,
}

DETAIL_ENDPOINTS_BY_ID: dict[SupportedEndpoints, callable] = {
    SupportedEndpoints.BIOME: list_mgnify_biomes,
    SupportedEndpoints.STUDY: get_mgnify_study,
    SupportedEndpoints.SAMPLE: get_mgnify_sample,
    SupportedEndpoints.RUN: get_analysed_run,
    SupportedEndpoints.ANALYSIS: get_mgnify_analysis,  # or with_annot?
    SupportedEndpoints.GENOME: get_mgnify_genome,
    SupportedEndpoints.ASSEMBLY: get_assembly,
    SupportedEndpoints.PUBLICATION: get_mgnify_publication,
    SupportedEndpoints.CATALOGUE: get_genome_catalogue,
}

ALL_ENDPOINTS: dict[SupportedEndpoints, callable] = (
    LIST_ENDPOINTS | DETAIL_ENDPOINTS_BY_ID
)

PARENT_CHILD_RESOURCES: dict[SupportedEndpoints, SupportedEndpoints] = {
    SupportedEndpoints.BIOMES: SupportedEndpoints.BIOME,
    SupportedEndpoints.STUDIES: SupportedEndpoints.STUDY,
    SupportedEndpoints.SAMPLES: SupportedEndpoints.SAMPLE,
    SupportedEndpoints.RUNS: SupportedEndpoints.RUN,
    SupportedEndpoints.ANALYSES: SupportedEndpoints.ANALYSIS,
    SupportedEndpoints.GENOMES: SupportedEndpoints.GENOME,
    SupportedEndpoints.ASSEMBLIES: SupportedEndpoints.ASSEMBLY,
    SupportedEndpoints.PUBLICATIONS: SupportedEndpoints.PUBLICATION,
    SupportedEndpoints.CATALOGUES: SupportedEndpoints.CATALOGUE,
}

WITHIN_RESOURCE_RELATIONSHIPS: dict[
    SupportedEndpoints, dict[SupportedEndpoints, callable]
] = {
    parent: {child: DETAIL_ENDPOINTS_BY_ID[child]}
    for parent, child in PARENT_CHILD_RESOURCES.items()
}

# I think this kinda follows the openapi "Links" on the right of the docs?
BETWEEN_RESOURCE_RELATIONSHIPS: dict[
    SupportedEndpoints, dict[SupportedEndpoints, callable]
] = {
    # for a biome detail, can list all studies associated with that biome
    SupportedEndpoints.BIOME: {SupportedEndpoints.STUDIES: list_mgnify_studies},
    # for a study detail,
    SupportedEndpoints.STUDY: {
        # also an endpoint to list all samples associated with the study
        SupportedEndpoints.SAMPLES: list_mgnify_study_samples,
        # there is an endpoint to list all analyses associated with the study
        SupportedEndpoints.ANALYSES: list_mgnify_study_analyses,
        # also one for publications
        SupportedEndpoints.PUBLICATIONS: list_mgnify_study_publications,
    },
    # for a sample detail, can list all runs associated with that sample
    SupportedEndpoints.SAMPLE: {SupportedEndpoints.RUNS: list_sample_runs},
    # for a run detail, can list all analyses associated with that run
    SupportedEndpoints.RUN: {SupportedEndpoints.ANALYSES: list_runs_analyses},
    # for an assembly detail,
    SupportedEndpoints.ASSEMBLY: {
        # there is an endpoint to list all analyses associated with that assembly
        SupportedEndpoints.ANALYSES: list_analyses_for_assembly,
        # also an endpoint to list all genomes linked to that assembly
        SupportedEndpoints.GENOMES: list_genome_links_for_assembly,
    },
    # for an analysis detail, there is an endpoint to get the analysis with annotations
    # or should the analysis detail already have annotations?
    SupportedEndpoints.ANALYSIS: {
        SupportedEndpoints.ANNOTATIONS: analysis_get_mgnify_analysis_with_annotations
    },
}

ALL_SUPPORTED_RELATIONSHIPS: dict[
    SupportedEndpoints, dict[SupportedEndpoints, callable]
] = (WITHIN_RESOURCE_RELATIONSHIPS | BETWEEN_RESOURCE_RELATIONSHIPS)

PRIVATE_ENDPOINTS: set[SupportedEndpoints] = {
    SupportedEndpoints.PRIVATE_STUDIES,
}

# so basically an agent could update this based on openapi.json spec changes,
# and then the rest of the code should work without needing to change?
# maybe some edge cases but ideally this is how we can future proof against API changes
