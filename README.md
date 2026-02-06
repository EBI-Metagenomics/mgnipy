# MGnipy

MGni.py is a python wrapper for the [MGnify API](https://www.ebi.ac.uk/metagenomics/api/docs/), supporting both version 1 and version 2. 

The python client libraries were auto-generated using [openapi-python-client](https://github.com/openapi-generators/openapi-python-client). Openapi-python-client provides data models and methods for the api reources and uses httpx and attr. 

## Installation

```bash
pip install mgnipy
```

## Usage
Look in biome resource for studies for a given biome. 

First instantiate the mgnifier:
```python
from mgnipy import Mgnifier

# init
glass = Mgnifier(
    resource="biomes",
    # GOLD ecosystem classification
    lineage="root:Host-associated:Plants:Rhizosphere", 
)

# look at the built request url
print(glass)
```

Then plan or preview the number of pages and records before collecting all their metadata :)
```python
# only prints some info
glass.plan()

# also returns the first page of results as a pd.DataFrame
df = glass.preview()
```

Now that you ahve confirmed that this is the metadta that you want then collect it:
(currently in memory)
```python
metadata = await df.collect()
```

## Additional documentation

- [MGnify API Docs](https://www.ebi.ac.uk/metagenomics/api/docs/)
- [openapi-python-client](https://github.com/openapi-generators/openapi-python-client)

## Development

see [Contributing.md](Contributing.md)

## License

TODO


