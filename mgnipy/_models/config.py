import hashlib
import httpx
import json
import logging

from mgnipy.emgapi_v2_client.models.webin_token_response import (
    WebinTokenResponse,
)

logger = logging.getLogger(__name__)
from getpass import getpass
from pathlib import Path
from time import time
from typing import Any, Optional

from platformdirs import user_cache_dir
from pydantic import Field, HttpUrl, field_serializer
from pydantic_settings import BaseSettings, SettingsConfigDict

from mgnipy._models.constants.CONSTANTS import SupportedApiVersions
from mgnipy.emgapi_v2_client.api.authentication import (
    token_obtain_sliding,
    token_refresh_sliding,
    token_verify,
)
from mgnipy.emgapi_v2_client.models.token_verify_input_schema import (
    TokenVerifyInputSchema,
)
from mgnipy.emgapi_v2_client.models.webin_token_refresh_request import (
    WebinTokenRefreshRequest,
)
from mgnipy.emgapi_v2_client.models.webin_token_request import WebinTokenRequest

APPNAME = "mgnipy"
APPAUTHOR = "MGnify"
CACHE_DIR = user_cache_dir(APPNAME, APPAUTHOR)


class BaseMGnipyConfig(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    api_version: SupportedApiVersions = Field(
        default=SupportedApiVersions.V2,
        description="API version to use. Supported values are 'v2', and 'latest'.",
    )
    base_url: HttpUrl = Field(
        default="https://www.ebi.ac.uk/",
        description="Base URL for the MGnify API",
        validate_default=True,
    )

    mg_user: Optional[str] = Field(
        default=None,
        description="Username for basic authentication (if required)",
        repr=False,
    )

    mg_password: Optional[str] = Field(
        default=None,
        description="Password for basic authentication (if required)",
        repr=False,
    )

    auth_token: Optional[str] = Field(
        default=None,
        description="Authentication token for API access. If provided, it will be used for authenticated requests.",
        repr=False,
    )

    cache_dir: Optional[Path] = Field(
        default_factory=lambda: Path(CACHE_DIR),
        description=(
            "Cache directory for storing API responses or other temp things. "
            "Defaults to a platform-appropriate cache dir via `platformdirs`. "
            "Set to None to disable disk caching.",
        ),
    )

    @field_serializer("base_url")
    def serialize_base_url(self, v: HttpUrl) -> str:
        """Custom serializer for the base_url field to ensure it is always represented as a string."""
        return str(v)


class MGnipyConfig(BaseMGnipyConfig):
    """
    Manage authentication credentials and tokens.

    Extension of BaseMGnipyConfig with methods for handling authentication,
    including obtaining, verifying, and refreshing tokens.

    If cache_dir is not set, the auth_token will be cached to working_dir

    Roughly the order of events:
    1. Check for cached sliding token (comprises access (shorter-lived) and refresh (longer) tokens).
    2. If cached token exists, verify the access token's validity.
    3. If valid, move on.
    4. If not valid token, try to refresh: get new access token if refresh token is still valid.
    5. If that fails, obtain a new one using username/password.
    6. Cache the new token for future use.
    """

    def _unauth_client(self) -> httpx.Client:
        """Client without auth for getting tokens"""
        return httpx.Client(base_url=str(self.base_url))

    @property
    def _token_cache_dir(self) -> Path:
        """
        Get folder path for storing the authentication token str.
        """

        # prep token dir
        _token_dir: Path = self.cache_dir or Path.cwd()
        logger.debug(f"Cached auth token will be stored in: {_token_dir}")
        # create dir if not exist
        _token_dir.mkdir(parents=True, exist_ok=True)
        return _token_dir

    @property
    def _token_file(self) -> Path:
        """
        Hash of url and username for token filename.
        Username in the hash so diff users on the same machine do not overwrite each other's tokens.
        """
        key: str = hashlib.sha256(
            f"{self.base_url}|{self.mg_user or ''}".encode()
        ).hexdigest()
        return self._token_cache_dir / f"auth_{key}.json"

    def _load_cached_token(self) -> Optional[str]:
        """
        Load a cached authentication token from the cache directory if it exists
        Also if cant read then return None to get new token

        Example
        -------
        config = MGnipyConfig()
        auth_token = config._load_cached_token()
        """

        if not self._token_file.exists():
            return None
        try:
            data: dict[str, str] = json.loads(self._token_file.read_text())
            return data.get("auth_token")
        except Exception:
            logger.error(
                f"Failed to read cached auth token from {self._token_file}. Removing file."
            )
            self._clear_cached_token()
            return None

    def _save_cached_token(self, auth_token: str) -> None:
        """
        Save the authentication token to a cache file in the cache directory.
        The token is stored along with a timestamp to allow for future expiration handling if needed.

        Parameters
        ----------
        auth_token : str
            The authentication token to be cached.

        Example
        -------
        config = MGnipyConfig()
        config._save_cached_token("your_auth_token")
        """
        to_cache: dict[str, Any] = {"auth_token": auth_token, "ts": int(time())}
        self._token_file.write_text(json.dumps(to_cache))

    def _clear_cached_token(self) -> None:
        """
        Delete cached auth token if it exists.

        Example
        -------
        config = MGnipyConfig()
        config._clear_cached_token()
        """
        if self._token_file.exists():
            self._token_file.unlink(missing_ok=True)

    def _get_login(
        self,
        *,
        interactive: bool = False,
    ) -> tuple[str, str]:
        """
        Returns MGnify username and password,
        either from config or by prompting the user.

        Parameters
        ----------
        interactive : bool, optional
            If True, prompts the user to input credentials if they are not found in the config. Default is True.

        Returns
        -------
        tuple[str, str]
            A tuple containing the username and password.

        Raises
        ------
        RuntimeError
            If credentials are not provided and prompting is disabled.

        Example
        -------
        config = MGnipyConfig(mg_user="myuser", mg_password="mypassword")
        username, password = config._get_login()
        """
        # if already configured return them
        if self.mg_user and self.mg_password:
            logger.debug("Using MGnipyConfig configured MGnify credentials")
            return self.mg_user, self.mg_password

        # otherwise ask them to login interactively
        # note: they may be prompted each time if user and pass not in .env
        if interactive:
            self.mg_user = input("MGnify username (Webin): ").strip()
            self.mg_password = getpass("MGnify password: ")
        else:
            self.mg_user = None
            self.mg_password = None

        if not self.mg_user or not self.mg_password:
            print(
                "Username/password not provided. " "Proceeding without authentication."
            )
        return self.mg_user, self.mg_password

    def obtain_auth_token(
        self,
        *,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> Optional[str]:
        """
        Obtains an authentication token using the MGnify username and password.
        If credentials are not available, can prompt the user to enter them.

        Parameters
        ----------
        username : str, optional
            MGnify username. If not provided, will attempt to use the configured username or prompt the user.
        password : str, optional
            MGnify password. If not provided, will attempt to use the configured password or prompt the user.

        Returns
        -------
        str or None
            The obtained authentication token, or None if the token could not be obtained.

        Example
        -------
        config = MGnipyConfig(mg_user="myuser", mg_password="mypassword")
        token = config.obtain_auth_token() # doctest: +SKIP
        """

        # prep body
        logger.debug("Preping `body` for sliding token request")
        body = WebinTokenRequest(
            username=username,
            password=password,
        )

        with self._unauth_client() as client:
            # requesting token from API
            logger.debug(f"Requesting auth token via {token_obtain_sliding.__name__}.")
            # getting parsed response
            result: WebinTokenRequest | None = token_obtain_sliding.sync(
                client=client, body=body
            )

        token = result.get("token", None)
        logger.debug(f"Token successfully obtained: {token is not None}")

        # cache if success
        if token:
            self._save_cached_token(token)

        return token

    def verify_auth_token(self, token: Optional[str] = None) -> bool:
        """
        Verify the validity of the provided authentication token
        Makes request to the token verification endpoint
        If no token is provided, it will attempt to verify the token stored in the config.

        Parameters
        ----------
        token : str, optional
            The authentication token to verify.
            If not provided, the method will use the token stored in the config.

        Returns
        -------
        bool
            True if the token is valid, False otherwise.

        Example
        -------
        config = MGnipyConfig()
        is_valid = config.verify_auth_token("your_auth_token") # doctest: +SKIP
        """
        _token = token or self.auth_token

        # if token is None then obvi not valid
        if not _token:
            return False

        # prep body
        body = TokenVerifyInputSchema(token=_token)

        # request
        with self._unauth_client() as client:
            logger.debug(f"Verifying auth token via {token_verify.__name__}")
            result = token_verify.sync(client=client, body=body)

        return result is not None

    def refresh_auth_token(self, token: Optional[str] = None) -> str | None:
        """
        Refresh the provided authentication token using the sliding token refresh endpoint.
        If no token is provided, it will attempt to refresh the token stored in the config.
        """

        _token: str = token or self.auth_token
        if not _token:
            return None

        # prep body
        body = WebinTokenRefreshRequest(token=_token)

        # request
        with self._unauth_client() as client:
            logger.debug(f"Refreshing auth token via {token_refresh_sliding.__name__}")
            # new token or not
            new_token: WebinTokenResponse | None = token_refresh_sliding.sync(
                client=client, body=body
            )

        if new_token:
            # save to cache
            self._save_cached_token(new_token)
        return new_token

    def resolve_auth_token(
        self,
        *,
        interactive: bool = False,
    ) -> None:
        """
        Resolve a valid authentication token by checking the current token,
        verifying it, and refreshing or obtaining a new one as needed.

        Parameters
        ----------
        interactive : bool, optional
            If True, prompts the user to input credentials if they are not found in the config. Default is True.


        Example
        -------
        config = MGnipyConfig(mg_user="myuser", mg_password="mypassword")
        config.resolve_auth_token()
        """

        # 1. get user, pass, auth token
        # a) auth_token from config or cache
        _token: str | None = self.auth_token or self._load_cached_token()

        # getting usr and pass
        username, password = self._get_login(interactive=interactive)

        # if all are None then stop process
        if not any([_token, username, password]):
            logger.warning(
                "No username, password provided. Proceeding without authentication."
            )
            return

        # b) if no token, try to obtain one using username/password
        if _token is None:
            # try to get token
            _token = self.obtain_auth_token(username=username, password=password)

        # 2. verify token (also if None means not valid so returns False)
        # if valid save and return
        if self.verify_auth_token(_token):
            logger.debug("Current access token is valid")
            self.auth_token = _token
            self._save_cached_token(self.auth_token)
            print("Authenticated successfully.")
            return

        # 3. else try to refresh token aka get new access token if longer refresh token still valid
        else:
            _token = self.refresh_auth_token(_token)

        # if refreshed tokenis valid save and return
        if _token:
            logger.debug("Token refreshed successfully")
            self.auth_token = _token
            self._save_cached_token(self.auth_token)
            print("Authenticated successfully.")

        # 4. else try to obtain new token using username/password
        elif username is not None and password is not None:
            logger.debug(
                "Current access token is invalid, trying to obtain new token using username/password"
            )
            self._clear_cached_token()
            self.auth_token = self.obtain_auth_token(
                username=username, password=password
            )
            if self.auth_token:
                logger.debug("New token obtained successfully")
                self._save_cached_token(self.auth_token)
                print("Authenticated successfully.")

        # 5. if still no valid token, then warn user and proceed without auth
        else:
            logger.warning(
                "No username, password provided. Proceeding without authentication."
            )
        return


def to_mgnipy_config(input: MGnipyConfig | dict | None) -> MGnipyConfig:
    """
    Helper function to convert a dictionary or MGnipyConfig instance into an MGnipyConfig instance.

    Parameters
    ----------
    input : MGnipyConfig or dict or None
        The input configuration, which can be an instance of MGnipyConfig, a dictionary containing the configuration parameters, or None.
        If None then default MGnipyConfig will be returned.

    Returns
    -------
    MGnipyConfig
        An instance of MGnipyConfig created from the input.

    Examples
    --------
    >>> config_dict = {
    ...     "api_version": "v2",
    ...     "base_url": "https://www.ebi.ac.uk/",
    ...     "mg_user": "myuser",
    ...     "mg_password": "mypassword",
    ...     "cache_dir": "/path/to/cache",
    ... }
    >>> config = to_mgnipy_config(config_dict)
    >>> config.api_version
    <SupportedApiVersions.V2: 'v2'>
    >>> config.base_url
    HttpUrl('https://www.ebi.ac.uk/')
    >>> config.cache_dir
    PosixPath('/path/to/cache')
    """

    if isinstance(input, MGnipyConfig):
        return input
    elif isinstance(input, dict):
        return MGnipyConfig(**input)
    elif input is None:
        return MGnipyConfig()
    else:
        return MGnipyConfig()
