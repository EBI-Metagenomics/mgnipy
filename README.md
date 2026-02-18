# MGnipy

MGni.py is a python wrapper for the [MGnify API](https://www.ebi.ac.uk/metagenomics/api/docs/), supporting both version 1 and version 2. 

The python client libraries were auto-generated using [openapi-python-client](https://github.com/openapi-generators/openapi-python-client). Openapi-python-client provides data models and methods for the api reources and uses httpx and attr. 

## Installation

```bash
# TestPypi
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple mgnipy
```

## Usage
You can use the `Mgnifier`s to find study, sample, analyses, genome accessions and associated metadata. 

First instantiate the mgnifier. Search params can be provided as `params: Optional[dict]` or `kwargs`. To see the supported kwargs there is an attribute `Mgnigier.supported_kwargs` 

```python
from mgnipy.V2 import StudiesMgnifier

# init
glass = StudiesMgnifier(
    # GOLD ecosystem classification
    biomes_lineage="root:Host-associated:Plants:Rhizosphere", 
    search="tomato"
)

# to see supported kwargs, uncomment
#print(glass.supported_kwargs)

# checkout the built request url, not sent yet
print(glass)
```

Then `.preview()` (lightweight) or `.plan()` (even lighterweight) the number of pages and records before collecting all their metadata :)
```python
# only prints some info
glass.plan()

# also returns the first page of results as a pd.DataFrame
df = glass.preview()
```

Now that you ahve confirmed that this is the metadta that you want then collect it:
(currently in memory)
```python
import asyncio 

# returns as a pandas df, or asyncio.run()
metadata = await df.get()
```

You can also access `Mgnifier.accessions` and pass the accessions to the mgnipy dataset collectors 
```python
from mgnipy.V2 import GoSlimCollector

# init 
bottle = GoSlimCollector(accessions=glass.accessions)
```

## Additional documentation

- [MGnify API Docs](https://www.ebi.ac.uk/metagenomics/api/docs/)
- [openapi-python-client](https://github.com/openapi-generators/openapi-python-client)

## Development

see [Contributing.md](Contributing.md)

## License

TODO


