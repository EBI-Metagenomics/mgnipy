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
    get_mgnify_genome,
    list_mgnify_genomes,
)
from mgnipy.emgapi_v2_client.api.miscellaneous import list_mgnify_biomes
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
    list_mgnify_study_samples,
)

LIST_ENDPOINTS = {
    SupportedEndpoints.BIOMES: list_mgnify_biomes,  # get all biomes, filtering option
    #    SupportedEndpoints.MISCELLANEOUS: list_mgnify_biomes,  # get all biomes, filtering option
    SupportedEndpoints.STUDIES: list_mgnify_studies,  # get all studies, filtering option
    SupportedEndpoints.SAMPLES: list_mgnify_samples,  # get all samples, filtering option or with study acc
    SupportedEndpoints.RUNS: list_analysed_runs,  # get all runs, filtering option or with sample acc
    SupportedEndpoints.ANALYSES: list_mgnify_analyses,  # get all analyses, NO FILTERING OPTION, but with study or assem acc
    SupportedEndpoints.GENOMES: list_mgnify_genomes,  # listing all genomes, NO FILTERING OPTION but with assem acc
    SupportedEndpoints.ASSEMBLIES: list_assemblies,  # listing all assemblies, no filtering TODO more info?
}

ACC_DETAIL_ENDPOINTS = {
    SupportedEndpoints.BIOME: list_mgnify_biomes,
    SupportedEndpoints.STUDY: get_mgnify_study,
    SupportedEndpoints.SAMPLE: get_mgnify_sample,
    SupportedEndpoints.RUN: get_analysed_run,
    SupportedEndpoints.ANALYSIS: get_mgnify_analysis,  # or with_annot?
    SupportedEndpoints.GENOME: get_mgnify_genome,
    SupportedEndpoints.ASSEMBLY: get_assembly,
}

ALL_ENDPOINTS = LIST_ENDPOINTS | ACC_DETAIL_ENDPOINTS

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

OLD_SUPPORTED_RELATIONSHIPS = {
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
