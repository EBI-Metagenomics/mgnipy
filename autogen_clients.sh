# Usage: sh autogen_clients.sh [FOLDER_PATH] [CONFIG_V1] [CONFIG_V2]
# requires uv, openapi-python-client installed
# should have config files"

FOLDER_PATH=${1:-"openapi"}
CONFIG_V1=${2:-"openapi/config-v1.yaml"}
CONFIG_V2=${3:-"openapi/config-v2.yaml"}
V1_SCHEMA_FILE="$FOLDER_PATH/MGnify API (emgapi_v1).yaml"
V2_SCHEMA_FILE="$FOLDER_PATH/openapi_v2.json"
DEST_V1_DIR="mgnipy"
DEST_V2_DIR="mgnipy"

# python helper to read yaml keys, used for getting project and package names from config files
read_yaml_key() {
  local config_file="$1"
  local key="$2"
  python3 - "$config_file" "$key" <<'PY'
import pathlib
import sys
import yaml

cfg = pathlib.Path(sys.argv[1])
key = sys.argv[2]

data = yaml.safe_load(cfg.read_text(encoding="utf-8")) or {}
value = data.get(key, "")
print("" if value is None else str(value))
PY
}


#####------------------ NOW DOING STUFF ##------------------###
# make FOLDER_PATH if it doesn't exist
mkdir -p "$FOLDER_PATH"

##------------------FOR API V2------------------##
# config
PROJECT_NAME_TWO="$(read_yaml_key "$CONFIG_V2" "project_name_override")"
PACKAGE_NAME_TWO="$(read_yaml_key "$CONFIG_V2" "package_name_override")"
# Fallbacks if config keys are missing
PROJECT_NAME_TWO=${PROJECT_NAME_TWO:-"emgapi-v2-client"}
PACKAGE_NAME_TWO=${PACKAGE_NAME_TWO:-"emgapi_v2_client"}
# Normalize package dirs for filesystem/import safety
PACKAGE_DIR_TWO="${PACKAGE_NAME_TWO//-/_}"

### ideally would only need to run this:
# openapi-python-client generate \
#     --url "https://www.ebi.ac.uk/metagenomics/api/v2/openapi.json" \
#     --output-path "$FOLDER_PATH/$PROJECT_NAME_TWO" \
#     --config "$CONFIG_V2" \
#     --overwrite
### but openapi spec first needs tweaks to work with generator

# download spec
curl -fL "https://www.ebi.ac.uk/metagenomics/api/v2/openapi.json" \
    -o "$V2_SCHEMA_FILE"

python3 openapi/preprocess_v2.py "$V2_SCHEMA_FILE"

openapi-python-client generate \
    --path "$V2_SCHEMA_FILE" \
    --output-path "$FOLDER_PATH/$PROJECT_NAME_TWO" \
    --config "$CONFIG_V2" \
    --overwrite

### uncomment below to move the generated modules into mgnipy based on config
### WARNING: this will overwrite any existing files in the destination directories, so use with caution and make sure to have backups or version control
mkdir -p "$DEST_V2_DIR"
mv "$FOLDER_PATH/$PROJECT_NAME_TWO/$PACKAGE_DIR_TWO" "$DEST_V2_DIR/$PACKAGE_DIR_TWO"

##------------------FOR API V1------------------##
# config
PROJECT_NAME_ONE="$(read_yaml_key "$CONFIG_V1" "project_name_override")"
PACKAGE_NAME_ONE="$(read_yaml_key "$CONFIG_V1" "package_name_override")"
# Fallbacks if config keys are missing
PROJECT_NAME_ONE=${PROJECT_NAME_ONE:-"emgapi-v1-client"}
PACKAGE_NAME_ONE=${PACKAGE_NAME_ONE:-"emgapi_v1_client"}
# Normalize package dirs for filesystem/import safety
PACKAGE_DIR_ONE="${PACKAGE_NAME_ONE//-/_}"


# file downloaded from https://www.ebi.ac.uk/metagenomics/api/schema
curl -fL "https://www.ebi.ac.uk/metagenomics/api/schema" \
    -o "$V1_SCHEMA_FILE"

openapi-python-client generate \
    --path "$V1_SCHEMA_FILE" \
    --output-path "$FOLDER_PATH/$PROJECT_NAME_ONE" \
    --config "$CONFIG_V1" \
    --overwrite

### uncomment below to move the generated modules into mgnipy based on config
### WARNING: this will overwrite any existing files in the destination directories, so use with caution and make sure to have backups or version control
# mkdir -p "$DEST_V1_DIR"
# mv "$FOLDER_PATH/$PROJECT_NAME_ONE/$PACKAGE_DIR_ONE" "$DEST_V1_DIR/$PACKAGE_DIR_ONE"


##---------if instead as dependency, build whl files and install using uv---------##
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
emgapi-v1-client = { path = "openapi/dist/emgapi_v1_client-1.0.0-py3-none-any.whl" }
emgapi-v2-client = { path = "openapi/dist/emgapi_v2_client-2.0.0-py3-none-any.whl" }
'
