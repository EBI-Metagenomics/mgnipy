# MGnipy API Features

---

---

### Current State

The existing MGnipy API uses a procedural, explicit approach:

```python
# Current API
from mgnipy import Mgnifier

mgnifier = Mgnifier(resource="analyses")
mgnifier.plan()  # Check what will be retrieved
mgnifier.preview()  # See first page
df = mgnifier.collect()  # Fetch all data
```
I think it's good to keep this current state and then provide users to also interact with the client as suggested below.

### Target State

The new API should be fluent, pythonic, and intuitive:

```python
# New API - Simple cases
df = mgnipy.analyses.get(100).to_df()
json_data = mgnipy.analyses.get().to_json()

# Finding specific resources
analysis = mgnipy.analyses.find(accession='MGYA00001231')
annotations = analysis.annotations.get()

# Pythonic slicing
first_five = mgnipy.analyses[:5]
single = mgnipy.analyses["MGYA00001231"]

# Resource discovery
resources = mgnipy.list_resources()
```

**Benefits:**
- Natural, readable syntax
- Leverages Python's `__getitem__` protocol
- Lazy evaluation for efficiency
- Chainable operations
- Self-documenting API

---

## Design Principles

### 1. Lazy Evaluation
Queries should build up without executing until needed:
```python
query = mgnipy.analyses.filter(biome='root:soil')  # No API call
df = query.to_df()  # API call happens here
```

### 2. Pythonic Patterns
Use familiar Python idioms:
- `__getitem__` for indexing: `mgnipy.analyses[0]`
- `__iter__` for iteration: `for analysis in mgnipy.analyses[:10]`
- Context managers where appropriate
- Method chaining for fluent API

### 3. Endpoints to focus on:
- Analyses
- Studies
- Genomes
- Biomes
- Assemblies
- Samples
- Publications

### 4. Progressive Disclosure
Simple things should be simple; complex things should be possible:
```python
# Simple: Just get data
mgnipy.analyses.get(10)

# Medium: Filter and format
mgnipy.analyses.filter(experiment_type='Amplicon').to_df()

# Complex: Multi-level queries with relationships
mgnipy.studies.find(accession='MGYS00001').samples.filter(...)
```

### 4. Type Safety
Use type hints and Pydantic validation:
```python
def get(self, limit: Optional[int] = None) -> 'QuerySet':
    """Get resources with optional limit."""
    ...
```

### 5. Transparency
Users should understand what's happening:
- Clear error messages
- Optional verbose mode
- Progress bars for long operations
- Warning when large datasets will be fetched

---

## API Specification

### Core API Surface

#### 1. Entry Point: `MGnipy` Class

```python
from mgnipy import MGnipy

# Initialize with optional API version
mgnipy = MGnipy(api_version='v1')  # or 'v2', 'latest'

# Access resources as attributes
mgnipy.analyses
mgnipy.samples
mgnipy.studies
mgnipy.runs
mgnipy.biomes

# Discover available resources
resources = mgnipy.list_resources()
# Returns: ['analyses', 'samples', 'studies', 'runs', 'biomes', ...]
```

#### 2. Resource Proxy: Dynamic Resource Access

```python
# Each resource type returns a ResourceProxy
analyses_proxy = mgnipy.analyses  # ResourceProxy instance

# Get all resources (with optional limit)
analyses_proxy.get()           # Returns QuerySet (lazy)
analyses_proxy.get(100)        # Limit to 100 results

# Find specific resource(s)
analyses_proxy.find(accession='MGYA00001231')
analyses_proxy.filter(biome='root:soil', experiment_type='amplicon')

# Pythonic indexing
analyses_proxy[0]              # First analysis (SingleResource)
analyses_proxy["MGYA00001231"] # By accession (SingleResource)
analyses_proxy[:10]            # First 10 (QuerySet)
analyses_proxy[5:15]           # Slice notation (QuerySet)
```

#### 3. QuerySet: Lazy Query Builder

```python
# Building queries (no API calls yet)
query = (
    mgnipy.analyses
    .filter({
        "biome": "root:soil",
        "experiment_type": "amplicon"
    })
    .order_by("-created")
    .limit(100)
)


# Executing queries (API calls happen here)
df = query.to_df()                    # As pandas DataFrame
json_data = query.to_json()           # As JSON list
list_data = query.to_list()           # As Python list

# Iteration triggers execution
for analysis in query:
    print(analysis.accession)

# Pagination handling
query.page_size(50)                   # Control page size
query.page(2)                         # Get specific page
```

#### 4. SingleResource: Individual Resource

```python
# Get a single resource
analysis = mgnipy.analyses["MGYA00001231"]

# Access attributes
print(analysis.accession)
print(analysis.experiment_type)
print(analysis.biome)

# Access relationships (returns ResourceProxy)
annotations = analysis.annotations     # Lazy
downloads = analysis.downloads         # Lazy

# Execute relationship queries
annotations_df = analysis.annotations.to_df()
```

#### 5. Output Formatters

```python
# DataFrame output (default for most use cases)
df = mgnipy.analyses.get(100).to_df()

# JSON output
json_data = mgnipy.analyses.get(100).to_json()
# Returns: [{"id": "...", "accession": "...", ...}, ...]

# Raw Python objects
items = mgnipy.analyses.get(100).to_list()
# Returns: [Analysis(...), Analysis(...), ...]

# Iterator (memory efficient)
for analysis in mgnipy.analyses.get(100):
    process(analysis)
```

### Advanced Features

#### Chaining Filters

```python
query = (mgnipy.samples
         .filter(biome='root:soil')
         .filter(experiment_type='amplicon')
         .filter(study_accession='MGYS00001'))
```

#### Relationship Traversal

```python
# Navigate from study to samples to runs
study = mgnipy.studies["MGYS00001"]
samples = study.samples.filter(biome='root:soil')
runs = samples[0].runs.to_df()

# Or in one chain (if API supports)
df = (mgnipy.studies["MGYS00001"]
      .samples.filter(biome='root:soil')
      .to_df())
```

#### Optional API Version Per Query

```python
# Global version
mgnipy = MGnipy(api_version='v1')

# Override for specific query
result = mgnipy.analyses.find(accession='...').use_version('v2').get()
```

#### Progress & Debugging

```python
# Enable progress bars
query = mgnipy.analyses.get(1000).verbose()

# Explain query (show API URLs that will be called)
query.explain()

# Dry run (don't execute, just show plan)
query.dry_run()
```

---

## Architecture Overview

### Component Hierarchy

```
MGnipy (entry point)
  ├── ResourceProxy (analyses, samples, etc.)
  │     ├── QuerySet (lazy query builder)
  │     │     ├── QueryExecutor (handles API calls)
  │     │     └── ResultFormatter (to_df, to_json, etc.)
  │     └── SingleResource (individual item)
  │           └── RelationshipProxy (nested resources)
  └── Config (API version, base URL, auth, etc.)
```

### Class Design

```python
# 1. Entry Point
class MGnipy:
    """Main entry point for the MGnipy API."""

    def __init__(self, api_version: str = 'v1', **config):
        self.api_version = api_version
        self.config = Config(**config)
        self._resource_registry = self._discover_resources()

    def __getattr__(self, name: str) -> ResourceProxy:
        """Dynamic attribute access for resources."""
        if name in self._resource_registry:
            return ResourceProxy(name, self.config)
        raise AttributeError(f"Resource '{name}' not found")

    def list_resources(self) -> List[str]:
        """List all available resources."""
        return list(self._resource_registry.keys())


# 2. Resource Proxy
class ResourceProxy:
    """Proxy for a specific resource type (analyses, samples, etc.)."""

    def __init__(self, resource_name: str, config: Config):
        self.resource_name = resource_name
        self.config = config

    def get(self, limit: Optional[int] = None) -> QuerySet:
        """Get resources with optional limit."""
        return QuerySet(self.resource_name, self.config).limit(limit)

    def find(self, **filters) -> QuerySet:
        """Find resources matching filters."""
        return QuerySet(self.resource_name, self.config).filter(**filters)

    def filter(self, **filters) -> QuerySet:
        """Alias for find()."""
        return self.find(**filters)

    def __getitem__(self, key: Union[int, str, slice]) -> Union[QuerySet, SingleResource]:
        """Support indexing and slicing."""
        if isinstance(key, slice):
            # Convert slice to limit/offset
            return QuerySet(self.resource_name, self.config).slice(key)
        elif isinstance(key, int):
            # Get by index
            return QuerySet(self.resource_name, self.config).limit(1).offset(key).first()
        elif isinstance(key, str):
            # Get by accession
            return SingleResource(self.resource_name, key, self.config)
        else:
            raise TypeError(f"Invalid index type: {type(key)}")


# 3. QuerySet (Query Builder)
class QuerySet:
    """Lazy query builder that executes on iteration or formatting."""

    def __init__(self, resource_name: str, config: Config):
        self.resource_name = resource_name
        self.config = config
        self._filters = {}
        self._limit = None
        self._offset = 0
        self._ordering = []
        self._page_size = 20
        self._verbose = False
        self._executed = False
        self._cache = None

    def filter(self, **filters) -> 'QuerySet':
        """Add filters to query."""
        new_qs = self._clone()
        new_qs._filters.update(filters)
        return new_qs

    def limit(self, n: Optional[int]) -> 'QuerySet':
        """Limit results."""
        new_qs = self._clone()
        new_qs._limit = n
        return new_qs

    def offset(self, n: int) -> 'QuerySet':
        """Offset results."""
        new_qs = self._clone()
        new_qs._offset = n
        return new_qs

    def order_by(self, *fields) -> 'QuerySet':
        """Order results."""
        new_qs = self._clone()
        new_qs._ordering = list(fields)
        return new_qs

    def verbose(self, enabled: bool = True) -> 'QuerySet':
        """Enable verbose mode with progress bars."""
        new_qs = self._clone()
        new_qs._verbose = enabled
        return new_qs

    def page_size(self, size: int) -> 'QuerySet':
        """Set page size for pagination."""
        new_qs = self._clone()
        new_qs._page_size = size
        return new_qs

    # Execution methods (trigger API calls)

    def to_df(self) -> pd.DataFrame:
        """Execute query and return DataFrame."""
        results = self._execute()
        return self._to_dataframe(results)

    def to_json(self) -> List[dict]:
        """Execute query and return JSON."""
        results = self._execute()
        return [item.to_dict() for item in results]

    def to_list(self) -> List:
        """Execute query and return list."""
        return self._execute()

    def count(self) -> int:
        """Get total count without fetching all data."""
        # Make HEAD request or fetch first page for count
        response = self._execute_single_page(page=1)
        return response['meta']['pagination']['count']

    def exists(self) -> bool:
        """Check if any results exist."""
        return self.count() > 0

    def first(self) -> Optional[SingleResource]:
        """Get first result."""
        results = self.limit(1)._execute()
        return results[0] if results else None

    def __iter__(self):
        """Make QuerySet iterable."""
        if not self._executed:
            self._cache = self._execute()
        return iter(self._cache)

    def __len__(self):
        """Get length (triggers execution)."""
        if not self._executed:
            self._cache = self._execute()
        return len(self._cache)

    def __getitem__(self, key):
        """Support indexing after execution."""
        if not self._executed:
            self._cache = self._execute()
        return self._cache[key]

    # Internal methods

    def _clone(self) -> 'QuerySet':
        """Clone QuerySet for immutability."""
        new_qs = QuerySet(self.resource_name, self.config)
        new_qs._filters = self._filters.copy()
        new_qs._limit = self._limit
        new_qs._offset = self._offset
        new_qs._ordering = self._ordering.copy()
        new_qs._page_size = self._page_size
        new_qs._verbose = self._verbose
        return new_qs

    def _execute(self) -> List:
        """Execute the query by calling the API."""
        if self._executed and self._cache is not None:
            return self._cache

        # Build query parameters
        params = self._build_params()

        # Execute with pagination
        executor = QueryExecutor(self.resource_name, self.config)
        results = executor.execute(
            params=params,
            page_size=self._page_size,
            verbose=self._verbose
        )

        self._cache = results
        self._executed = True
        return results

    def _build_params(self) -> dict:
        """Build API query parameters."""
        params = {}

        # Add filters
        params.update(self._filters)

        # Add pagination
        if self._limit:
            params['page[size]'] = min(self._limit, self._page_size)
        else:
            params['page[size]'] = self._page_size

        if self._offset:
            params['page[offset]'] = self._offset

        # Add ordering
        if self._ordering:
            params['ordering'] = ','.join(self._ordering)

        return params


# 4. SingleResource (Individual Item)
class SingleResource:
    """Represents a single resource instance."""

    def __init__(self, resource_name: str, accession: str, config: Config):
        self.resource_name = resource_name
        self.accession = accession
        self.config = config
        self._data = None
        self._loaded = False

    def _load(self):
        """Lazy load resource data."""
        if not self._loaded:
            executor = QueryExecutor(self.resource_name, self.config)
            self._data = executor.get_single(self.accession)
            self._loaded = True

    def __getattr__(self, name: str):
        """Dynamic attribute access for fields and relationships."""
        self._load()

        # Check if it's a field
        if name in self._data.get('attributes', {}):
            return self._data['attributes'][name]

        # Check if it's a relationship
        if name in self._data.get('relationships', {}):
            # Return a ResourceProxy for the related resource
            return ResourceProxy(name, self.config, parent=self)

        raise AttributeError(f"'{self.resource_name}' has no attribute '{name}'")

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        self._load()
        return self._data

    def refresh(self):
        """Reload data from API."""
        self._loaded = False
        self._load()


# 5. QueryExecutor (API Interaction)
class QueryExecutor:
    """Handles actual API calls and pagination."""

    def __init__(self, resource_name: str, config: Config):
        self.resource_name = resource_name
        self.config = config
        self.client = self._get_client()

    def _get_client(self):
        """Get the appropriate OpenAPI client."""
        if self.config.api_version == 'v1':
            from mgni_py_v1 import Client
            return Client(base_url=self.config.base_url)
        elif self.config.api_version == 'v2':
            from mgni_py_v2 import Client
            return Client(base_url=self.config.base_url)
        else:
            raise ValueError(f"Unsupported API version: {self.config.api_version}")

    def execute(self, params: dict, page_size: int, verbose: bool = False) -> List:
        """Execute query with pagination."""
        results = []
        page = 1
        total_pages = None

        # Optional progress bar
        pbar = tqdm(desc=f"Fetching {self.resource_name}", disable=not verbose)

        while True:
            # Fetch page
            params['page[number]'] = page
            response = self._fetch_page(params)

            # Extract data
            data = response.get('data', [])
            results.extend(data)

            # Update progress
            if total_pages is None:
                total_pages = response['meta']['pagination']['pages']
                pbar.total = total_pages
            pbar.update(1)

            # Check if done
            if not response.get('links', {}).get('next'):
                break

            page += 1

        pbar.close()
        return results

    def _fetch_page(self, params: dict) -> dict:
        """Fetch a single page."""
        # Use the OpenAPI client to make the request
        # This is a placeholder - actual implementation depends on client
        response = self.client.get_resource(self.resource_name, params=params)
        return response

    def get_single(self, accession: str) -> dict:
        """Fetch a single resource by accession."""
        response = self.client.get_resource_by_id(self.resource_name, accession)
        return response.get('data', {})


# 6. Configuration
class Config:
    """Configuration for API access."""

    def __init__(
        self,
        api_version: str = 'v1',
        base_url: Optional[str] = None,
        auth_token: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        self.api_version = api_version
        self.base_url = base_url or self._default_base_url(api_version)
        self.auth_token = auth_token
        self.timeout = timeout
        self.max_retries = max_retries

    def _default_base_url(self, version: str) -> str:
        """Get default base URL for API version."""
        return f"https://www.ebi.ac.uk/metagenomics/api/{version}"
```

### Data Flow

```
1. User creates query:
   mgnipy.analyses.filter(biome='soil')

2. ResourceProxy creates QuerySet:
   QuerySet(resource_name='analyses', filters={'biome': 'soil'})

3. User triggers execution:
   .to_df()

4. QuerySet builds parameters:
   {'biome': 'soil', 'page[size]': 20}

5. QueryExecutor makes API calls:
   - Fetch page 1
   - Fetch page 2
   - ... (with pagination)

6. ResultFormatter converts to DataFrame:
   pd.DataFrame(results)

7. Return to user
```

---

   ```

### Migration Guide

Create `MIGRATION.md`:

```markdown
# Migration Guide: v1 to v2

## Quick Reference

| Old API | New API |
|---------|---------|
| `Mgnifier(resource="analyses")` | `mgnipy.analyses` |
| `.plan()` | Not needed (lazy) |
| `.preview()` | `.limit(10).to_df()` |
| `.collect()` | `.to_df()` |
| `Samplifier(...)` | Use relationships |

## Step-by-Step Migration

### 1. Simple Queries

**Before:**
```python
from mgnipy import Mgnifier

mgnifier = Mgnifier(resource="analyses", biome="root:soil")
mgnifier.plan()
df = mgnifier.collect()
```

**After:**
```python
from mgnipy.fluent import MGnipy

client = MGnipy()
df = client.analyses.filter(biome="root:soil").to_df()
```

### 2. With Limit

**Before:**
```python
mgnifier = Mgnifier(resource="analyses")
mgnifier.plan()
df = mgnifier.collect(limit=100)
```

**After:**
```python
df = client.analyses.get(100).to_df()
# or
df = client.analyses.limit(100).to_df()
```

### 3. Multiple Filters

**Before:**
```python
mgnifier = Mgnifier(
    resource="analyses",
    biome="root:soil",
    experiment_type="amplicon"
)
df = mgnifier.collect()
```

**After:**
```python
df = client.analyses.filter(
    biome="root:soil",
    experiment_type="amplicon"
).to_df()
```

### 4. Relationship Queries (Samplifier)

**Before:**
```python
from mgnipy import Samplifier

samplifier = Samplifier(study_accession="MGYS00001")
df = samplifier.collect()
```

**After:**
```python
study = client.studies["MGYS00001"]
df = study.samples.to_df()
```

---

## Learning Resources

### Python Concepts to Study

1. **Magic Methods**
   - `__getattr__`, `__getitem__`, `__iter__`
   - [Python Data Model](https://docs.python.org/3/reference/datamodel.html)

2. **Immutability & Cloning**
   - Why QuerySets return new instances
   - [Copy module](https://docs.python.org/3/library/copy.html)

3. **Lazy Evaluation**
   - Generators and iterators
   - [Itertools](https://docs.python.org/3/library/itertools.html)

4. **Type Hints**
   - `typing` module
   - [PEP 484](https://peps.python.org/pep-0484/)

### Similar APIs to Study

1. **Django ORM**
   - [QuerySet API](https://docs.djangoproject.com/en/stable/ref/models/querysets/)
   - Lazy evaluation, chaining, slicing

2. **SQLAlchemy**
   - [Query API](https://docs.sqlalchemy.org/en/14/orm/query.html)
   - Query building patterns

3. **Pandas**
   - [Indexing and Slicing](https://pandas.pydata.org/docs/user_guide/indexing.html)
   - Method chaining

4. **HTTPx**
   - [Client API](https://www.python-httpx.org/api/)
   - Modern fluent API design

### Testing Resources

1. **unittest.mock**
   - [Mock documentation](https://docs.python.org/3/library/unittest.mock.html)
   - Mocking API calls

2. **pytest**
   - [Pytest documentation](https://docs.pytest.org/)
   - Fixtures, parametrize

3. **pytest-cov**
   - [Coverage.py](https://coverage.readthedocs.io/)
   - Measuring test coverage

### Documentation Tools

1. **Sphinx**
   - [Sphinx documentation](https://www.sphinx-doc.org/)
   - Auto-generating API docs

2. **MyST-NB**
   - [MyST-NB guide](https://myst-nb.readthedocs.io/)
   - Jupyter notebooks in Sphinx

---

## Success Criteria

### Functional Requirements

- [ ] All proposed API examples work as shown
- [ ] Lazy evaluation works correctly (no premature API calls)
- [ ] Slicing and indexing work pythonically
- [ ] Relationship traversal works
- [ ] All output formats (DataFrame, JSON, list) work
- [ ] Ordering and filtering work
- [ ] Progress bars display for long queries
- [ ] Error messages are clear and helpful

### Non-Functional Requirements

- [ ] Test coverage >85%
- [ ] All tests passing
- [ ] Documentation complete and clear
- [ ] Type hints on all public methods
- [ ] Code formatted with black
- [ ] No regressions in old API (if keeping it)
- [ ] Performance comparable to old API

### User Experience

- [ ] API is intuitive for newcomers
- [ ] Common tasks require minimal code
- [ ] Error messages guide users to solutions
- [ ] Examples cover common use cases
- [ ] Migration path is clear

---

## Troubleshooting Common Issues

### Issue: Circular Imports

**Problem:** `ResourceProxy` and `SingleResource` import each other.

**Solution:** Use late imports inside methods:
```python
def __getattr__(self, name):
    # Import here instead of at top
    from .resource_proxy import ResourceProxy
    return ResourceProxy(...)
```

### Issue: Relationship Queries Not Working

**Problem:** Relationship endpoint doesn't exist in API.

**Solution:** Add validation:
```python
SUPPORTED_RELATIONSHIPS = {
    'analysis': ['annotations'],
    'sample': ['runs', 'study'],
    # ...
}

def __getattr__(self, name):
    if name not in SUPPORTED_RELATIONSHIPS.get(self.resource_name, []):
        raise AttributeError(
            f"Relationship '{name}' not supported for '{self.resource_name}'"
        )
```

---

## Checkpoints & Review

### After Each Phase


1. **Demo:**
   - Show working examples
   - Explain design decisions
   - Discuss any challenges

2. **Self-Review Checklist:**
   - [ ] Code follows PEP 8 style guide
   - [ ] All functions have docstrings
   - [ ] Type hints are present
   - [ ] Tests are written and passing
   - [ ] No TODO comments remain
   - [ ] Examples in docstrings work

3. **Run Quality Checks:**
   ```bash
   # Format code
   black mgnipy/fluent
   isort mgnipy/fluent

   # Lint
   ruff check mgnipy/fluent

   # Type check (if using mypy)
   mypy mgnipy/fluent

   # Test
   pytest tests/unit/fluent -v
   pytest --cov=mgnipy.fluent
   ```



---

## Additional Features (Optional)

If time permits, consider these enhancements:

### 1. Async Support

```python
# Async version
async def to_df_async(self):
    """Async execution for better performance."""
    results = await self._execute_async()
    return self._to_dataframe(results)

# Usage
df = await client.analyses.filter(biome='soil').to_df_async()
```

### 2. Caching

```python
class CachedQuerySet(QuerySet):
    """QuerySet with built-in caching."""

    def __init__(self, *args, cache_backend=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache_backend = cache_backend or InMemoryCache()

    def _execute(self):
        cache_key = self._build_cache_key()

        if cached := self.cache_backend.get(cache_key):
            return cached

        results = super()._execute()
        self.cache_backend.set(cache_key, results, ttl=3600)
        return results
```

### 3. Query Validation

```python
def filter(self, **filters):
    """Filter with validation."""
    # Validate filter keys
    valid_filters = self._get_valid_filters()
    invalid = set(filters.keys()) - valid_filters

    if invalid:
        raise ValueError(
            f"Invalid filters: {invalid}. "
            f"Valid filters: {valid_filters}"
        )

    return super().filter(**filters)
```

### 4. Batch Operations: This is really good to have

```python
def bulk_get(self, accessions: List[str]) -> QuerySet:
    """Fetch multiple resources by accession."""
    # Use API batch endpoint if available
    return self.filter(accession__in=accessions)
```

## Final Notes

### Tips for Success

1. **Start Small:** Get basic functionality working before adding features
2. **Test Early:** Write tests as you go, not at the end
3. **Ask Questions:** Don't hesitate to ask for clarification
4. **Document as You Code:** Write docstrings immediately
5. **Review Regularly:** Feel free to commit and submit PRs for feedback
6. **Commit Often:** Make small, focused commits with clear messages

### Git Workflow

```bash
# Start
git checkout -b feature/fluent-api-redesign

# Work on Phase 1
git add mgnipy/fluent/config.py tests/unit/fluent/test_config.py
git commit -m "feat(fluent): add Config class with tests"

# Push regularly
git push origin feature/fluent-api-redesign

```

### Getting Help

- **Stuck on implementation?** Review similar APIs (Django ORM, SQLAlchemy)
- **Test failures?** Read error messages carefully, add debug prints
- **Design questions?** Discuss with mentor before committing to approach
- **API issues?** Check OpenAPI client source code, try API directly

---

## Conclusion

This pacakge will transform MGnipy into a modern, pythonic library that's a joy to use. By following this guide, you'll learn:

- Advanced Python patterns (magic methods, lazy evaluation)
- API design principles
- Test-driven development
- Documentation best practices
- Real-world software engineering

Take it one phase at a time, test thoroughly, and don't hesitate to ask questions. Good luck!

---
