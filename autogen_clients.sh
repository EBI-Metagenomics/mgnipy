# Usage: sh autogen_clients.sh [FOLDER_PATH] [PROJECT_NAME_ONE] [PROJECT_NAME_TWO]
# requires uv, poetry, openapi-python-client installed
# should have "MGnify API (emgapi_v1).yaml", config-v1.yaml, config-v2.yaml in FOLDER_PATH"

FOLDER_PATH=${1:-"openapi"}
PROJECT_NAME_ONE=${2:-"mgni-py-v1"}
PROJECT_NAME_TWO=${3:-"mgni-py-v2"}

# for v1
# file downloaded from https://www.ebi.ac.uk/metagenomics/api/schema
openapi-python-client generate \
    --path "$FOLDER_PATH/MGnify API (emgapi_v1).yaml" \
    --output-path "$FOLDER_PATH/$PROJECT_NAME_ONE" \
    --config "$FOLDER_PATH/config-v1.yaml" \
    --overwrite


# for v2
openapi-python-client generate \
    --path "$FOLDER_PATH/openapi_v2.json" \
    --output-path "$FOLDER_PATH/$PROJECT_NAME_TWO" \
    --config "$FOLDER_PATH/config-v2.yaml" \
    --overwrite

# move the generated modules into mgnipy

: '
# build whls 
cd "$FOLDER_PATH/$PROJECT_NAME_ONE"
poetry build -f wheel -o ../dist/
cd -

cd "$FOLDER_PATH/$PROJECT_NAME_TWO"
poetry build -f wheel -o ../dist/
cd -

# install as dependency using uv
for whl in "$FOLDER_PATH"/dist/*.whl; do
  uv add "$whl"
done
uv lock 
uv sync
'

: '
# also add the following to pyproject.toml to use the whl files instead
[tool.uv.sources]
mgni-py-v1 = { path = "openapi/dist/mgni_py_v1-1.0.0-py3-none-any.whl" }
mgni-py-v2 = { path = "openapi/dist/mgni_py_v2-2.0.0-py3-none-any.whl" }
'