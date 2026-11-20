# Adopting any API changes

If [APIv2](https://www.ebi.ac.uk/metagenomics/api/v2/) has been changed (i.e., [the openapi.json](https://www.ebi.ac.uk/metagenomics/api/v2/openapi.json) file has changed),

then we can **automatically** adopt those changes into `mgnipy` 
 
by running the provided script [./autogen_clients.sh](../../../autogen_clients.sh): 

```bash 
# in the repo root
sh autogen_clients.sh
```

---


## What this does

1. Downloads the [openapi.json](https://www.ebi.ac.uk/metagenomics/api/v2/openapi.json) spec 
<br>
2. Does some light cleaning which is in [./openapi/preprocess_v2.py](../../../openapi/preprocess_v2.py)
<br>
3. Uses the openapi-python-client python package to recreate the submodule [emgapi_v2_client](../../../mgnipy/emgapi_v2_client/)