# mainly Enum constants for pydantic models
from enum import Enum


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


class ExperimentTypes(str, Enum):
    """https://www.ebi.ac.uk/metagenomics/api/v1/experiment-types"""

    AMPLICON = "amplicon"
    ASSEMBLY = "assembly"
    HYBRID_ASSEMBLY = "hybrid_assembly"
    LONG_READS_ASSEMBLY = "long_reads_assembly"
    METABARCODING = "metabarcoding"
    METAGENOMIC = "metagenomic"
    METATRANSCRIPTOMIC = "metatranscriptomic"
    UNKNOWN = "unknown"
