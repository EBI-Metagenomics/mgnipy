from typing import (
    Optional,
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    field_serializer,
)

from mgnipy._models.CONSTANTS import SupportedApiVersions


class MgnipyConfig(BaseModel):
    # class ConfigDict:
    #     extra = "forbid"
    #     use_enum_values = True

    model_config = ConfigDict(
        extra="forbid", use_enum_values=True, validate_assignment=True
    )

    api_version: SupportedApiVersions = Field(
        default=SupportedApiVersions.V2,
        description="API version to use. Supported values are 'v1', 'v2', and 'latest'.",
    )
    base_url: HttpUrl = Field(
        default="https://www.ebi.ac.uk/",
        description="Base URL for the MGnify API",
        validate_default=True,
    )
    auth_token: Optional[str] = Field(
        default=None,
        description="Authentication token for private data access",
        repr=False,
    )
    # cache_dir: Optional[DirectoryPath] = Field(
    #     default_factory=lambda: user_cache_dir("mgnipy", "MGnify"),
    #     description="Directory for caching API responses. Defaults to the user cache directory.",
    #     alias=AliasChoices("cache_dir", "cache_directory"),
    # )

    @field_serializer("base_url")
    def serialize_base_url(self, v: HttpUrl) -> str:
        return str(v)
