# mainly Enum constants for pydantic models
from enum import Enum
from pydantic import TypeAdapter, ValidationError

class SupportedApiVersions(Enum):
    V1 = "v1"
    V2 = "v2"
    LATEST = "latest"

class SupportedEndpoints(Enum):
    ANALYSES = "analyses"
    ANNOTATIONS = "annotations"
    ANTISMASH_GENECLUSTERS = "antismash-geneclusters"
    ASSEMBLIES = "assemblies"
    BIOMES = "biomes"
    COGS = "cogs"
    EXPERIMENT_TYPES = "experiment-types"
    GENOME_CATALOGUES = "genome-catalogues"
    GENOME_SEARCH = "genome-search"
    GENOMES = "genomes"
    GENOMES_SEARCH = "genomes-search"
    GENOMESET = "genomeset"
    KEGG_CLASSES = "kegg-classes"
    KEGG_MODULES = "kegg-modules"
    MYDATA = "mydata"
    PIPELINE_TOOLS = "pipeline-tools"
    PIPELINES = "pipelines"
    PUBLICATIONS = "publications"
    RUNS = "runs"
    SAMPLES = "samples"
    STUDIES = "studies"
    SUPER_STUDIES = "super-studies"

# define pydantic typeadapters
def validate_api(input):
    try:
        return TypeAdapter(
            SupportedApiVersions
        ).validate_python(input)
    except ValidationError as e:
        raise ValueError(f"Invalid API version: {input}") from e
    
def validate_endpoint(input):
    try:
        return TypeAdapter(
            SupportedEndpoints
        ).validate_python(input)
    except ValidationError as e:
        raise ValueError(f"Invalid endpoint: {input}") from e