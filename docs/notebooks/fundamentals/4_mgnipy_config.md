# Configuring `MGnipyConfig`

## What is `mgnipy.MGnipyConfig`?

A [Pydantic-based settings object](https://pydantic.dev/docs/validation/latest/concepts/pydantic_settings/) used across MGni.Py to:

- ✅ store API connection details such as the base url
- ✅ store credentials (`mg_user`, `mg_password`) and handle retrieval and verification of sliding authentication tokens (`auth_token`)
- ✅ and configure the cache such as local disk cache directory (`cache_dir`).

## The fields

- **`cache_dir`**: Directory used for response caching; defaults to a platform-appropriate cache directory via [`platformdirs`](https://platformdirs.readthedocs.io/en/latest/). Set to `None` to disable disk caching.
- **`mg_user` / `mg_password`**: Optional MGnify username/password for sliding-token authentication.
- **`api_version`**: Which API version to target (Should be: v2).
- **`base_url`**: Base MGnify URL. Should be: `https://www.ebi.ac.uk/`.


## Authentication

`mgnipy.MGnipyConfig` takes care of 

1. Checking for cached [sliding JSON Web Tokens (JWT)](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/token_types.html#sliding-tokens) which comprises a shorter-lived Access token and a longer Refresh token.

2. Verifying the validity of Access tokens using the [token_verify](https://www.ebi.ac.uk/metagenomics/api/v2/#/Authentication/token_verify) endpoint 

3. Refreshing access, getting a new Access token if the Refresh token is at least still valid using [token_refresh_sliding](https://www.ebi.ac.uk/metagenomics/api/v2/#/Authentication/token_refresh_sliding)

4. Or obtaining new Access and Refresh tokens using login credentials (e.g., like from a .env file) from the [token_obtain_sliding](https://www.ebi.ac.uk/metagenomics/api/v2/#/Authentication/token_obtain_sliding) endpoint of the MGnify API using your username/password

5. Caching the token and stored in `MGnipyConfig.auth_token` for the session and used for authenticated API requests.

```{note}
- By default the token is cached on disk under a platform-appropriate cache dir (via `platformdirs`) in a file named auth_<hash>.json. -- unless cache is disabled via `cache_dir=None`
- Cached tokens are stored per base URL + username (hashed) to avoid collisions when using multiple endpoints/accounts.
```

See [accessing private data page](https://mgnipy.mgnify.org/notebooks/fundamentals/6_access_private_data.html) on how to configure for private data. 


