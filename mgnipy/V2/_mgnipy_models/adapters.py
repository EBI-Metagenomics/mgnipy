# mainly Enum constants for pydantic models
from pydantic import (
    TypeAdapter,
    ValidationError,
)

from mgnipy.V2._mgnipy_models.CONSTANTS import (
    SupportedApiVersions,
    SupportedEndpoints,
)


# define pydantic typeadapters
def validate_api(input):
    try:
        return TypeAdapter(SupportedApiVersions).validate_python(input)
    except ValidationError as e:
        raise ValueError(f"Invalid API version: {input}") from e


def validate_endpoint(input):
    try:
        return TypeAdapter(SupportedEndpoints).validate_python(input)
    except ValidationError as e:
        raise ValueError(f"Invalid endpoint: {input}") from e
