# mainly Enum constants for pydantic models
from pydantic import (
    TypeAdapter,
    ValidationError,
)

from mgnipy.V1._models_v1.CONSTANTS1 import (
    ExperimentTypes,
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


def validate_experiment_type(input):
    try:
        return TypeAdapter(ExperimentTypes).validate_python(input)
    except ValidationError as e:
        raise ValueError(f"Invalid experiment type: {input}") from e
