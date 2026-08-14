from enum import Enum

class MGnifyFunctionalAnalysisAnnotationType(str, Enum):
    PFAMS = "pfams"
    TAXONOMIES_DADA2_PR2 = "taxonomies__dada2_pr2"
    TAXONOMIES_DADA2_SILVA = "taxonomies__dada2_silva"
    TAXONOMIES_ITS_ONE_DB = "taxonomies__its_one_db"
    TAXONOMIES_LSU = "taxonomies__lsu"
    TAXONOMIES_PR2 = "taxonomies__pr2"
    TAXONOMIES_SSU = "taxonomies__ssu"
    TAXONOMIES_UNITE = "taxonomies__unite"

    def __str__(self) -> str:
        return str(self.value)
