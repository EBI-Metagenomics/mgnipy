"""Contains all the data models used in inputs/outputs"""

from .additional_contained_genome_schema import AdditionalContainedGenomeSchema
from .analysed_run import AnalysedRun
from .analysis_get_mgnify_analysis_with_annotations_of_type_m_gnify_functional_analysis_annotation_type import (
    AnalysisGetMgnifyAnalysisWithAnnotationsOfTypeMGnifyFunctionalAnalysisAnnotationType,
)
from .assembly import Assembly
from .assembly_detail import AssemblyDetail
from .assembly_detail_metadata_type_0 import AssemblyDetailMetadataType0
from .assembly_detail_status_type_0 import AssemblyDetailStatusType0
from .biome import Biome
from .biome_list_filters import BiomeListFilters
from .download_file_index_file import DownloadFileIndexFile
from .download_file_index_file_index_type import DownloadFileIndexFileIndexType
from .download_file_type import DownloadFileType
from .download_type import DownloadType
from .ena_sample_fields import ENASampleFields
from .ena_study_fields import ENAStudyFields
from .europe_pmc_annotation import EuropePmcAnnotation
from .europe_pmc_annotation_group import EuropePmcAnnotationGroup
from .europe_pmc_annotation_mention import EuropePmcAnnotationMention
from .europe_pmc_annotation_tag import EuropePmcAnnotationTag
from .genome_assembly_link_schema import GenomeAssemblyLinkSchema
from .genome_catalogue_base import GenomeCatalogueBase
from .genome_catalogue_base_catalogue_type import GenomeCatalogueBaseCatalogueType
from .genome_catalogue_base_other_stats_type_0 import GenomeCatalogueBaseOtherStatsType0
from .genome_catalogue_detail import GenomeCatalogueDetail
from .genome_catalogue_detail_catalogue_type import GenomeCatalogueDetailCatalogueType
from .genome_catalogue_detail_other_stats_type_0 import (
    GenomeCatalogueDetailOtherStatsType0,
)
from .genome_catalogue_list import GenomeCatalogueList
from .genome_catalogue_list_catalogue_type import GenomeCatalogueListCatalogueType
from .genome_catalogue_list_other_stats_type_0 import GenomeCatalogueListOtherStatsType0
from .genome_detail import GenomeDetail
from .genome_list import GenomeList
from .genome_schema import GenomeSchema
from .genome_type import GenomeType
from .genome_with_annotations import GenomeWithAnnotations
from .genome_with_annotations_annotations import GenomeWithAnnotationsAnnotations
from .input_ import Input
from .list_mgnify_publications_order_type_0 import ListMgnifyPublicationsOrderType0
from .list_mgnify_samples_order_type_0 import ListMgnifySamplesOrderType0
from .list_mgnify_studies_order_type_0 import ListMgnifyStudiesOrderType0
from .m_gnify_analysis import MGnifyAnalysis
from .m_gnify_analysis_detail import MGnifyAnalysisDetail
from .m_gnify_analysis_detail_metadata_type_0 import MGnifyAnalysisDetailMetadataType0
from .m_gnify_analysis_detail_quality_control_summary_type_0 import (
    MGnifyAnalysisDetailQualityControlSummaryType0,
)
from .m_gnify_analysis_download_file import MGnifyAnalysisDownloadFile
from .m_gnify_analysis_typed_annotation import MGnifyAnalysisTypedAnnotation
from .m_gnify_analysis_with_annotations import MGnifyAnalysisWithAnnotations
from .m_gnify_analysis_with_annotations_annotations import (
    MGnifyAnalysisWithAnnotationsAnnotations,
)
from .m_gnify_analysis_with_annotations_annotations_additional_property_type_1 import (
    MGnifyAnalysisWithAnnotationsAnnotationsAdditionalPropertyType1,
)
from .m_gnify_analysis_with_annotations_metadata_type_0 import (
    MGnifyAnalysisWithAnnotationsMetadataType0,
)
from .m_gnify_analysis_with_annotations_quality_control_summary_type_0 import (
    MGnifyAnalysisWithAnnotationsQualityControlSummaryType0,
)
from .m_gnify_download_file_index_file import MGnifyDownloadFileIndexFile
from .m_gnify_download_file_index_file_index_type import (
    MGnifyDownloadFileIndexFileIndexType,
)
from .m_gnify_functional_analysis_annotation_type import (
    MGnifyFunctionalAnalysisAnnotationType,
)
from .m_gnify_genome_download_file import MGnifyGenomeDownloadFile
from .m_gnify_publication import MGnifyPublication
from .m_gnify_publication_detail import MGnifyPublicationDetail
from .m_gnify_publication_detail_metadata import MGnifyPublicationDetailMetadata
from .m_gnify_publication_metadata import MGnifyPublicationMetadata
from .m_gnify_sample import MGnifySample
from .m_gnify_sample_detail import MGnifySampleDetail
from .m_gnify_sample_detail_metadata import MGnifySampleDetailMetadata
from .m_gnify_sample_with_metadata import MGnifySampleWithMetadata
from .m_gnify_sample_with_metadata_metadata import MGnifySampleWithMetadataMetadata
from .m_gnify_study import MGnifyStudy
from .m_gnify_study_detail import MGnifyStudyDetail
from .m_gnify_study_detail_metadata import MGnifyStudyDetailMetadata
from .m_gnify_study_download_file import MGnifyStudyDownloadFile
from .ninja_pagination_response_schema_additional_contained_genome_schema import (
    NinjaPaginationResponseSchemaAdditionalContainedGenomeSchema,
)
from .ninja_pagination_response_schema_assembly import (
    NinjaPaginationResponseSchemaAssembly,
)
from .ninja_pagination_response_schema_biome import NinjaPaginationResponseSchemaBiome
from .ninja_pagination_response_schema_genome_assembly_link_schema import (
    NinjaPaginationResponseSchemaGenomeAssemblyLinkSchema,
)
from .ninja_pagination_response_schema_genome_catalogue_list import (
    NinjaPaginationResponseSchemaGenomeCatalogueList,
)
from .ninja_pagination_response_schema_genome_list import (
    NinjaPaginationResponseSchemaGenomeList,
)
from .ninja_pagination_response_schema_m_gnify_analysis import (
    NinjaPaginationResponseSchemaMGnifyAnalysis,
)
from .ninja_pagination_response_schema_m_gnify_analysis_detail import (
    NinjaPaginationResponseSchemaMGnifyAnalysisDetail,
)
from .ninja_pagination_response_schema_m_gnify_analysis_typed_annotation import (
    NinjaPaginationResponseSchemaMGnifyAnalysisTypedAnnotation,
)
from .ninja_pagination_response_schema_m_gnify_publication import (
    NinjaPaginationResponseSchemaMGnifyPublication,
)
from .ninja_pagination_response_schema_m_gnify_sample import (
    NinjaPaginationResponseSchemaMGnifySample,
)
from .ninja_pagination_response_schema_m_gnify_sample_with_metadata import (
    NinjaPaginationResponseSchemaMGnifySampleWithMetadata,
)
from .ninja_pagination_response_schema_m_gnify_study import (
    NinjaPaginationResponseSchemaMGnifyStudy,
)
from .ninja_pagination_response_schema_super_study import (
    NinjaPaginationResponseSchemaSuperStudy,
)
from .order_by_filter_literalaccession_accession_updated_at_updated_at import (
    OrderByFilterLiteralaccessionAccessionUpdatedAtUpdatedAt,
)
from .order_by_filter_literalaccession_accession_updated_at_updated_at_order_type_0 import (
    OrderByFilterLiteralaccessionAccessionUpdatedAtUpdatedAtOrderType0,
)
from .order_by_filter_literalpublished_year_published_year import (
    OrderByFilterLiteralpublishedYearPublishedYear,
)
from .order_by_filter_literalpublished_year_published_year_order_type_0 import (
    OrderByFilterLiteralpublishedYearPublishedYearOrderType0,
)
from .order_by_filter_literalsample_title_sample_title_updated_at_updated_at import (
    OrderByFilterLiteralsampleTitleSampleTitleUpdatedAtUpdatedAt,
)
from .order_by_filter_literalsample_title_sample_title_updated_at_updated_at_order_type_0 import (
    OrderByFilterLiteralsampleTitleSampleTitleUpdatedAtUpdatedAtOrderType0,
)
from .pipeline_versions import PipelineVersions
from .publication_annotations import PublicationAnnotations
from .publication_list_filters import PublicationListFilters
from .sample_list_filters import SampleListFilters
from .schema import Schema
from .study_list_filters import StudyListFilters
from .super_study import SuperStudy
from .super_study_detail import SuperStudyDetail
from .token_verify_input_schema import TokenVerifyInputSchema
from .webin_token_refresh_request import WebinTokenRefreshRequest
from .webin_token_request import WebinTokenRequest
from .webin_token_response import WebinTokenResponse

__all__ = (
    "AdditionalContainedGenomeSchema",
    "AnalysedRun",
    "AnalysisGetMgnifyAnalysisWithAnnotationsOfTypeMGnifyFunctionalAnalysisAnnotationType",
    "Assembly",
    "AssemblyDetail",
    "AssemblyDetailMetadataType0",
    "AssemblyDetailStatusType0",
    "Biome",
    "BiomeListFilters",
    "DownloadFileIndexFile",
    "DownloadFileIndexFileIndexType",
    "DownloadFileType",
    "DownloadType",
    "ENASampleFields",
    "ENAStudyFields",
    "EuropePmcAnnotation",
    "EuropePmcAnnotationGroup",
    "EuropePmcAnnotationMention",
    "EuropePmcAnnotationTag",
    "GenomeAssemblyLinkSchema",
    "GenomeCatalogueBase",
    "GenomeCatalogueBaseCatalogueType",
    "GenomeCatalogueBaseOtherStatsType0",
    "GenomeCatalogueDetail",
    "GenomeCatalogueDetailCatalogueType",
    "GenomeCatalogueDetailOtherStatsType0",
    "GenomeCatalogueList",
    "GenomeCatalogueListCatalogueType",
    "GenomeCatalogueListOtherStatsType0",
    "GenomeDetail",
    "GenomeList",
    "GenomeSchema",
    "GenomeType",
    "GenomeWithAnnotations",
    "GenomeWithAnnotationsAnnotations",
    "Input",
    "ListMgnifyPublicationsOrderType0",
    "ListMgnifySamplesOrderType0",
    "ListMgnifyStudiesOrderType0",
    "MGnifyAnalysis",
    "MGnifyAnalysisDetail",
    "MGnifyAnalysisDetailMetadataType0",
    "MGnifyAnalysisDetailQualityControlSummaryType0",
    "MGnifyAnalysisDownloadFile",
    "MGnifyAnalysisTypedAnnotation",
    "MGnifyAnalysisWithAnnotations",
    "MGnifyAnalysisWithAnnotationsAnnotations",
    "MGnifyAnalysisWithAnnotationsAnnotationsAdditionalPropertyType1",
    "MGnifyAnalysisWithAnnotationsMetadataType0",
    "MGnifyAnalysisWithAnnotationsQualityControlSummaryType0",
    "MGnifyDownloadFileIndexFile",
    "MGnifyDownloadFileIndexFileIndexType",
    "MGnifyFunctionalAnalysisAnnotationType",
    "MGnifyGenomeDownloadFile",
    "MGnifyPublication",
    "MGnifyPublicationDetail",
    "MGnifyPublicationDetailMetadata",
    "MGnifyPublicationMetadata",
    "MGnifySample",
    "MGnifySampleDetail",
    "MGnifySampleDetailMetadata",
    "MGnifySampleWithMetadata",
    "MGnifySampleWithMetadataMetadata",
    "MGnifyStudy",
    "MGnifyStudyDetail",
    "MGnifyStudyDetailMetadata",
    "MGnifyStudyDownloadFile",
    "NinjaPaginationResponseSchemaAdditionalContainedGenomeSchema",
    "NinjaPaginationResponseSchemaAssembly",
    "NinjaPaginationResponseSchemaBiome",
    "NinjaPaginationResponseSchemaGenomeAssemblyLinkSchema",
    "NinjaPaginationResponseSchemaGenomeCatalogueList",
    "NinjaPaginationResponseSchemaGenomeList",
    "NinjaPaginationResponseSchemaMGnifyAnalysis",
    "NinjaPaginationResponseSchemaMGnifyAnalysisDetail",
    "NinjaPaginationResponseSchemaMGnifyAnalysisTypedAnnotation",
    "NinjaPaginationResponseSchemaMGnifyPublication",
    "NinjaPaginationResponseSchemaMGnifySample",
    "NinjaPaginationResponseSchemaMGnifySampleWithMetadata",
    "NinjaPaginationResponseSchemaMGnifyStudy",
    "NinjaPaginationResponseSchemaSuperStudy",
    "OrderByFilterLiteralaccessionAccessionUpdatedAtUpdatedAt",
    "OrderByFilterLiteralaccessionAccessionUpdatedAtUpdatedAtOrderType0",
    "OrderByFilterLiteralpublishedYearPublishedYear",
    "OrderByFilterLiteralpublishedYearPublishedYearOrderType0",
    "OrderByFilterLiteralsampleTitleSampleTitleUpdatedAtUpdatedAt",
    "OrderByFilterLiteralsampleTitleSampleTitleUpdatedAtUpdatedAtOrderType0",
    "PipelineVersions",
    "PublicationAnnotations",
    "PublicationListFilters",
    "SampleListFilters",
    "Schema",
    "StudyListFilters",
    "SuperStudy",
    "SuperStudyDetail",
    "TokenVerifyInputSchema",
    "WebinTokenRefreshRequest",
    "WebinTokenRequest",
    "WebinTokenResponse",
)
