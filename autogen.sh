# for v1
openapi-python-client generate \
    --path "MGnify API (emgapi_v1).yaml" \
    --output-path "auto-client1" \
    --config "config-v1.yaml" \
    --overwrite


# for v2
openapi-python-client generate \
    --url https://www.ebi.ac.uk/metagenomics/api/v2/openapi.json \
    --output-path "auto-client2" \
    --config "config-v2.yaml" \
    --overwrite