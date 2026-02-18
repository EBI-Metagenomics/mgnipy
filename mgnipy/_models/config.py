from pydantic import (
    BaseModel, 
    DirectoryPath,
    Field, 
    HttpUrl,
    AliasChoices,
)

from typing import (
    Optional,
)

from .CONSTANTS import SupportedApiVersions

from platformdirs import user_cache_dir

    
class MgnipyConfig(BaseModel):
    class Config:
        extra = "forbid"
        use_enum_values = True

    api_version: SupportedApiVersions = Field(
        default=SupportedApiVersions.V2,
        description="API version to use. Supported values are 'v1', 'v2', and 'latest'.",
    )
    base_url: HttpUrl = Field(
        default="https://www.ebi.ac.uk/",
        description="Base URL for the MGnify API",
    )
    auth_token: Optional[str] = Field(
        default=None,
        description="Authentication token for private data access",
        repr=False,
    )
    cache_dir: Optional[DirectoryPath] = Field(
        default_factory=lambda: user_cache_dir("mgnipy", "MGnify"),
        description="Directory for caching API responses. Defaults to the user cache directory.",
        alias=AliasChoices("cache_dir", "cache_directory"),
    )