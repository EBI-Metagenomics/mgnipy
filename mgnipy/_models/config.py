import hashlib
import json
import logging
from getpass import getpass
from pathlib import Path
from time import time
from typing import (
    Optional,
)

from platformdirs import user_cache_dir
from pydantic import (
    Field,
    HttpUrl,
    field_serializer,
)
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

from mgnipy._models.CONSTANTS import SupportedApiVersions
from mgnipy.emgapi_v2_client import Client
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


class MgnipyConfig(BaseSettings):

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

    cache_dir: Path = Field(
        default_factory=lambda: Path(CACHE_DIR),
        description=(
            "Cache directory for storing API responses or other temp things. "
            "Defaults to a platform-appropriate cache dir via `platformdirs`.",
        ),
    )

    @field_serializer("base_url")
    def serialize_base_url(self, v: HttpUrl) -> str:
        """Custom serializer for the base_url field to ensure it is always represented as a string."""
        return str(v)


class AuthMGnipyConfig(MgnipyConfig):
    """
    Manage authentication credentials and tokens.

    Extension of MgnipyConfig with methods for handling authentication,
    including obtaining, verifying, and refreshing tokens.
    """

    def _unauth_client(self) -> Client:
        """Client without auth for getting tokens"""
        return Client(base_url=str(self.base_url))

    def _token_cache_path(self) -> Path:
        """
        Generate a cache file path for storing the authentication token based on the base URL and username.
        """
        # create dir if not exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        # hash of url and username for filename
        key = hashlib.sha256(
            f"{self.base_url}|{self.mg_user or ''}".encode()
        ).hexdigest()
        return Path(self.cache_dir) / f"auth_{key}.json"

    def _load_cached_token(self) -> Optional[str]:
        """
        Load a cached authentication token from the cache directory if it exists
        Also if cant read then return None to get new token
        """
        token_path = self._token_cache_path()
        if not token_path.exists():
            return None
        try:
            data = json.loads(token_path.read_text())
            return data.get("auth_token")
        except Exception:
            return None

    def _save_cached_token(self, auth_token: str) -> None:
        """
        Save the authentication token to a cache file in the cache directory.
        The token is stored along with a timestamp to allow for future expiration handling if needed.

        Parameters
        ----------
        auth_token : str
            The authentication token to be cached.

        """
        token_path = self._token_cache_path()
        to_cache = {"auth_token": auth_token, "ts": int(time())}
        token_path.write_text(json.dumps(to_cache))

    def _clear_cached_token(self) -> None:
        """
        Clear the cached authentication token by deleting the cache file if it exists.
        """
        token_path = self._token_cache_path()
        if token_path.exists():
            token_path.unlink(missing_ok=True)

    def _get_login(
        self,
        *,
        interactive: bool = True,
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
        config = AuthMGnipyConfig(mg_user="myuser", mg_password="mypassword")
        username, password = config._get_login()
        """
        # if already configured return them
        if self.mg_user and self.mg_password:
            logging.debug("Using configured MGnify credentials")
            return self.mg_user, self.mg_password

        if interactive:
            # otherwise ask them to login interactively
            user = input("MGnify username (Webin): ").strip()
            password = getpass("MGnify password: ")

            if not user or not password:
                print(
                    "Username/password not provided. Proceeding without authentication."
                )

        else:
            user = None
            password = None
        # keep in config for this session
        # they will be prompted each time if not in .env
        self.mg_user = user or None
        self.mg_password = password or None
        return user, password

    def obtain_auth_token(
        self,
        *,
        interactive: bool = True,
    ) -> Optional[str]:
        """
        Obtains an authentication token using the MGnify username and password.
        If credentials are not available, can prompt the user to enter them.
        """
        logging.debug("getting username and password...")
        username, password = self._get_login(interactive=interactive)
        logging.debug("retrieved username and password...")
        # prep body
        logging.debug("prepping body for token request...")
        body = WebinTokenRequest(
            username=username,
            password=password,
        )

        try:
            # requesting token from API
            logging.debug("requesting token from API...")
            with self._unauth_client() as client:
                resp = token_obtain_sliding.sync(client=client, body=body)
            token = resp.token if resp else None
            # if successful cache it and return
            if token:
                logging.debug("successfully obtained auth token, caching it...")
                self._save_cached_token(token)
            return token
        except Exception:
            logging.debug("Failed to obtain authentication token.")
            return None

    def verify_auth_token(self, token: Optional[str] = None) -> bool:
        """
        Verify the validity of the provided authentication token
        Makes request to the token verification endpoint
        If no token is provided, it will attempt to verify the token stored in the config.
        """
        _token = token or self.auth_token

        # if token is None then obvi not valid
        if not _token:
            return False

        # prep body
        body = TokenVerifyInputSchema(token=_token)

        try:
            with self._unauth_client() as client:
                reponse = token_verify.sync(client=client, body=body)
            return reponse is not None
        except Exception:
            return False

    def refresh_auth_token(self, token: Optional[str] = None) -> Optional[str]:
        _token = token or self.auth_token
        if not _token:
            return None

        # prep body
        body = WebinTokenRefreshRequest(token=_token)

        try:
            with self._unauth_client() as client:
                response = token_refresh_sliding.sync(client=client, body=body)
            # new token or not?
            new_token = response.token if response else None
            # if yes then cache it and return
            if new_token:
                # save to cache
                self._save_cached_token(new_token)
            return new_token
        except Exception:
            return None

    def resolve_auth_token(
        self,
        *,
        interactive: bool = True,
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
        config = AuthMGnipyConfig(mg_user="myuser", mg_password="mypassword")
        config.resolve_auth_token()
        """

        # 1. check cache first
        cached = self._load_cached_token()
        if cached and not self.auth_token:
            logging.debug("Loaded auth token from cache")
            self.auth_token = cached

        # 1.5. verify if is cached or existing token
        if self.auth_token:
            # if is valid try refresh
            if self.verify_auth_token(self.auth_token):
                logging.debug("Valid auth token found, refreshing it...")
                self.auth_token = self.refresh_auth_token(self.auth_token)
            else:
                # then clear it from cache
                logging.debug(
                    "Invalid auth token found, clearing cache and trying to obtain new one..."
                )
                self._clear_cached_token()
                self.auth_token = None

        # 2. try to obtain new token :) and caches
        if self.auth_token is None:
            logging.debug("No valid auth token available, obtaining new one...")
            self.auth_token = self.obtain_auth_token(interactive=interactive)
            if not self.mg_user and not self.mg_password:
                logging.debug(
                    "No login credentials provided, unable to obtain auth_token."
                )

        # post checks
        if self.auth_token and not self.verify_auth_token(self.auth_token):
            raise RuntimeError("Failed to resolve a valid authentication token.")
        if self.auth_token and self.verify_auth_token(self.auth_token):
            print("Authenticated successfully.")
