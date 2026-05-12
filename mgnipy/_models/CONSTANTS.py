# mainly Enum constants for pydantic models
from enum import Enum

from pydantic import (
    TypeAdapter,
    ValidationError,
)


class SpecialEnum(Enum):
    def __str__(self):
        """Return the value of the enum member as a string."""
        return str(self.value)

    @classmethod
    def as_list(cls):
        """Return a list of the values of all enum members."""
        return [field.value for field in cls]

    @classmethod
    def validate(cls, input):
        """
        Validate the input against the enum values and return the corresponding enum member.

        Parameters
        ----------
        input : str
            The input string to validate against the enum values.

        Returns
        -------
            Enum member corresponding to the input string if valid, otherwise raises ValueError.

        Examples
        --------
        >>> SupportedEndpoints.validate("analyses")
        <SupportedEndpoints.ANALYSES: 'analyses'>
        >>> SupportedEndpoints.validate("invalid")
        Traceback (most recent call last):
        ...
        ValueError: Invalid SupportedEndpoints: invalid
        """
        try:
            return TypeAdapter(cls).validate_python(input)
        except ValidationError as e:
            raise ValueError(f"Invalid {cls.__name__}: {input}") from e

    @classmethod
    def is_valid(cls, input) -> bool:
        """
        Check if the input is a valid value for the enum.

        Parameters
        ----------
        input : str
            The input string to check against the enum values.

        Returns
        -------
            True if the input is a valid enum value, False otherwise.

        Examples
        --------
        >>> SupportedEndpoints.is_valid("analyses")
        True
        >>> SupportedEndpoints.is_valid("invalid")
        False
        """
        try:
            cls.validate(input)
            return True
        except ValueError:
            return False

    @classmethod
    def as_one_str(cls, sep=",") -> str:
        """
        Provides a string of all enum values joined by the specified separator.

        Parameters
        ----------
        sep : str, optional
            The separator to use between enum values in the resulting string (default is ",").

        Returns
        -------
        str
            A string of all enum values joined by the specified separator.

        Examples
        --------
        >>> comma_sep = SupportedEndpoints.as_one_str()
        >>> comma_sep
        'analyses,analysis,...,annotations,private_studies'
        >>> pipe_sep = SupportedEndpoints.as_one_str(sep="|")
        >>> pipe_sep
        'analyses|analysis|...|biomes|biome|...|private_studies'
        """
        return sep.join(field.value for field in cls)


class SupportedApiVersions(SpecialEnum):
    # V1 = 'v1' # TODO: add support for v1 endpoints?
    V2 = "v2"
    LATEST = "latest"


class SupportedEndpoints(SpecialEnum):
    ANALYSES = "analyses"
    ANALYSIS = "analysis"
    ASSEMBLIES = "assemblies"
    ASSEMBLY = "assembly"
    GENOMES = "genomes"
    GENOME = "genome"
    PUBLICATIONS = "publications"
    PUBLICATION = "publication"
    SAMPLES = "samples"
    SAMPLE = "sample"
    STUDIES = "studies"
    STUDY = "study"
    RUNS = "runs"
    RUN = "run"
    BIOMES = "biomes"  # miscellaneous
    BIOME = "biome"
    CATALOGUES = "catalogues"
    CATALOGUE = "catalogue"
    ANNOTATIONS = (
        "annotations"  # not really an endpoint but fits better here than acc detail
    )
    PRIVATE_STUDIES = "private_studies"
