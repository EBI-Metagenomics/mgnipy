import hashlib
import json
import pytest
from mgnipy._models.config import MGnipyConfig, to_mgnipy_config
from mgnipy._models.constants.CONSTANTS import SupportedApiVersions
from pathlib import Path

## Constants


USER = "myuser"
PASSWORD = "mypassword"
BASE_URL = "https://www.ebi.ac.uk/"
API_VER = "v2"
TOKEN_CONTENT = {"auth_token": "this-is-a-fake-token", "ts": 1234567890}


## Fixtures


@pytest.fixture
def config_with_cache_dir(tmp_path):
    return MGnipyConfig(
        api_version=API_VER,
        base_url=BASE_URL,
        mg_user=USER,
        mg_password=PASSWORD,
        cache_dir=tmp_path,
    )


@pytest.fixture
def config_without_cache_dir():
    return MGnipyConfig(
        api_version=API_VER,
        base_url=BASE_URL,
        mg_user=USER,
        mg_password=PASSWORD,
        cache_dir=None,
    )


@pytest.fixture
def token_basename():
    hash: str = hashlib.sha256(f"{BASE_URL}|{USER}".encode()).hexdigest()
    return f"auth_{hash}.json"


@pytest.fixture
def tmp_file_cached_token(tmp_path, token_basename):

    # prep
    token_file = tmp_path / token_basename

    # making folder
    tmp_path.mkdir(parents=True, exist_ok=True)
    # and now the token file
    token_file.write_text(json.dumps(TOKEN_CONTENT))

    # for clean up
    return token_file


## MGnipyConfig Tests


def test_MGnifyConfig_token_cache_dir(
    config_with_cache_dir, config_without_cache_dir, tmp_path
):
    """
    Even if cache_dir is None, the token should be cached somewhere. If cache_dir==None then in cwd
    """

    assert (
        config_with_cache_dir._token_cache_dir == tmp_path
    ), "The token cache directory should be set to the provided path."

    # If no cache_dir is provided, the token cache directory should default to a non-None value.
    assert (
        config_without_cache_dir._token_cache_dir is not None
    ), "If no cache_dir is provided, the token cache directory should not be None"
    assert (
        config_without_cache_dir._token_cache_dir == Path.cwd()
    ), "If no cache_dir is provided, the token cache directory should default to the current working directory."


def test_MGnifyConfig_token_file(
    config_without_cache_dir, config_with_cache_dir, token_basename
):
    """"""

    # first when no cache_dir
    config = config_without_cache_dir
    expected_token_file_without_cache = Path.cwd() / token_basename
    # now when cache_dir is provided
    config2 = config_with_cache_dir
    expected_token_file_with_cache = config2.cache_dir / token_basename

    assert (
        config._token_file == expected_token_file_without_cache
    ), "The token file path and hash should be correctly computed based on the base URL and user"

    assert (
        config2._token_file == expected_token_file_with_cache
    ), "The token file path and hash should be correctly computed based on the base URL and user, even when a cache_dir is provided."

    assert (
        config._token_file.name == config2._token_file.name
    ), "The token file name should be the same regardless of cache_dir."


def test_MGnipyConfig_load_cached_token(
    tmp_file_cached_token, config_with_cache_dir, tmp_path
):
    """
    The MGnipyConfig should be able to load a cached token from the expected location.
    """
    # prep
    # make temp dir and token file
    token_filepath = tmp_file_cached_token
    config = config_with_cache_dir

    # load the cached token
    loaded_token = config._load_cached_token()

    assert (
        loaded_token == TOKEN_CONTENT["auth_token"]
    ), "The loaded token should match the content of the cached token file."

    # tidy up
    token_filepath.unlink()
    tmp_path.rmdir()


def test_to_mgnipy_config_accepts_dict_or_MGnipyConfig(tmp_path, config_with_cache_dir):
    """
    The to_mgnipy_config function should convert a plain dictionary into an MGnipyConfig instance, normalizing fields as needed.
    If an MGnipyConfig instance is passed in, it should return the same instance without modification.
    """
    config_dict = {
        "api_version": API_VER,
        "base_url": BASE_URL,
        "mg_user": USER,
        "mg_password": PASSWORD,
        "cache_dir": tmp_path,
    }

    config = to_mgnipy_config(config_dict)

    assert isinstance(
        config, MGnipyConfig
    ), "Dictionary input should be converted into an MGnipyConfig instance."
    assert config.api_version is SupportedApiVersions(
        API_VER
    ), "The api_version field should be normalized to the enum value."
    assert (
        str(config.base_url) == BASE_URL
    ), "The base URL should stay intact during config normalization."
    assert (
        config.cache_dir == tmp_path
    ), "The configured cache directory should be preserved."

    same_config = to_mgnipy_config(config)
    assert (
        same_config is config
    ), "Passing an MGnipyConfig instance should return the same object unchanged."
