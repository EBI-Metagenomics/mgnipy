# so can do mgnipy.proxies.x import y
from __future__ import annotations

from ..V2.proxies.analyses import Analyses, AnalysisDetail
from ..V2.proxies.assemblies import Assemblies, AssemblyDetail
from ..V2.proxies.biomes import BiomeDetail, Biomes
from ..V2.proxies.catalogues import CatalogueDetail, Catalogues
from ..V2.proxies.genomes import GenomeDetail, Genomes
from ..V2.proxies.publications import PublicationDetail, Publications
from ..V2.proxies.runs import RunDetail, Runs
from ..V2.proxies.samples import SampleDetail, Samples
from ..V2.proxies.studies import Studies, StudyDetail

__all__ = [
    "Analyses",
    "AnalysisDetail",
    "Assemblies",
    "AssemblyDetail",
    "BiomeDetail",
    "Biomes",
    "CatalogueDetail",
    "Catalogues",
    "GenomeDetail",
    "Genomes",
    "PublicationDetail",
    "Publications",
    "RunDetail",
    "Runs",
    "SampleDetail",
    "Samples",
    "Studies",
    "StudyDetail",
]
