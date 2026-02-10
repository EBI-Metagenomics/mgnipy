from enum import Enum


class CataloguesFilterEnum(str, Enum):
    BARLEY_RHIZOSPHERE_V2_0 = "barley-rhizosphere-v2-0"
    CHICKEN_GUT_V1_0_1 = "chicken-gut-v1-0-1"
    COW_RUMEN_V1_0_1 = "cow-rumen-v1-0-1"
    HONEYBEE_GUT_V1_0_1 = "honeybee-gut-v1-0-1"
    HUMAN_GUT_V2_0_2 = "human-gut-v2-0-2"
    HUMAN_ORAL_V1_0_1 = "human-oral-v1-0-1"
    HUMAN_SKIN_V1_0 = "human-skin-v1-0"
    HUMAN_VAGINAL_V1_0 = "human-vaginal-v1-0"
    MAIZE_RHIZOSPHERE_V1_0 = "maize-rhizosphere-v1-0"
    MARINE_EUKARYOTES_VBETA = "marine-eukaryotes-vbeta"
    MARINE_SEDIMENT_V1_0 = "marine-sediment-v1-0"
    MARINE_V2_0 = "marine-v2-0"
    MOUSE_GUT_V1_0 = "mouse-gut-v1-0"
    NON_MODEL_FISH_GUT_V2_0 = "non-model-fish-gut-v2-0"
    PIG_GUT_V1_0 = "pig-gut-v1-0"
    SHEEP_RUMEN_V1_0 = "sheep-rumen-v1-0"
    SOIL_V1_0 = "soil-v1-0"
    TOMATO_RHIZOSPHERE_V1_0 = "tomato-rhizosphere-v1-0"
    ZEBRAFISH_FECAL_V1_0 = "zebrafish-fecal-v1-0"

    def __str__(self) -> str:
        return str(self.value)
