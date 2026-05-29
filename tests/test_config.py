from mgnipy._models.config import MGnipyConfig, to_mgnipy_config
from mgnipy._models.constants.CONSTANTS import SupportedApiVersions


def test_to_mgnipy_config_accepts_dict_and_existing_instance(tmp_path):
    """
    The to_mgnipy_config function should convert a plain dictionary into an MGnipyConfig instance, normalizing fields as needed. If an MGnipyConfig instance is passed in, it should return the same instance without modification.
    """
    config_dict = {
        "api_version": "v2",
        "base_url": "https://www.ebi.ac.uk/",
        "mg_user": "myuser",
        "mg_password": "mypassword",
        "cache_dir": tmp_path,
    }

    config = to_mgnipy_config(config_dict)

    assert isinstance(
        config, MGnipyConfig
    ), "Dictionary input should be converted into an MGnipyConfig instance."
    assert (
        config.api_version is SupportedApiVersions.V2
    ), "The api_version field should be normalized to the enum value."
    assert (
        str(config.base_url) == "https://www.ebi.ac.uk/"
    ), "The base URL should stay intact during config normalization."
    assert (
        config.cache_dir == tmp_path
    ), "The configured cache directory should be preserved."

    same_config = to_mgnipy_config(config)
    assert (
        same_config is config
    ), "Passing an MGnipyConfig instance should return the same object unchanged."


def test_token_cache_round_trip(tmp_path):
    """
    Token helpers should use a deterministic cache file derived from user and base URL.
    Saving a token should create the cache file, and loading it immediately after should return the same token. Clearing the cache should remove the file.
    """
    config = MGnipyConfig(cache_dir=tmp_path, mg_user="myuser")

    token_path = config._token_cache_path()

    assert (
        token_path is not None
    ), "A cache path should be created when cache_dir is configured."
    assert (
        token_path.parent == tmp_path
    ), "The token cache should live inside the configured cache directory."
    assert token_path.name.startswith(
        "auth_"
    ), "The token cache file name should use the auth_ prefix."
    assert token_path.suffix == ".json", "The token cache should be written as JSON."

    config._save_cached_token("secret-token")

    assert token_path.exists(), "Saving a token should create the token cache file."
    assert (
        config._load_cached_token() == "secret-token"
    ), "Loading immediately after save should recover the same token."

    config._clear_cached_token()

    assert (
        not token_path.exists()
    ), "Clearing the token cache should remove the cache file."
