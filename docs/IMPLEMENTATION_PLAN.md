# MGnipy Fluent API — Gap Analysis & Implementation Plan

## Gap Analysis

### What's Already Built (~45%)

| Feature                               | Guide Target          | Current Location                                   | Status     |
| ------------------------------------- | --------------------- | -------------------------------------------------- | ---------- |
| `MGnipy` entry point w/ `__getattr__` | `MGnipy` class        | `mgnipy/mgnipy.py`                                 | ✅ Done    |
| Resource proxy base class             | `ResourceProxy`       | `V2/metadata.py` (BiomesProxy, StudiesProxy, etc.) | ✅ Done    |
| `filter(**filters)` chaining          | Immutable clone       | `V2/core.py` `Mgnifier.filter()`                   | ✅ Done    |
| `to_df()` output                      | DataFrame export      | `V2/core.py` `to_df()` (rename needed)             | ✅ Done    |
| `dry_run()`                           | Plan without fetching | `V2/core.py`                                       | ✅ Done    |
| `list_resources()`                    | Resource discovery    | `mgnipy/mgnipy.py`                                 | ✅ Done    |
| `count`                               | Total count           | Property on `Mgnifier`                             | ✅ Done    |
| `__iter__` / `__getitem__`            | Pythonic iteration    | `V2/core.py` `Mgnifier`                            | ✅ Done    |
| `Config` class                        | `MgnipyConfig`        | `_models/config.py` (pydantic)                     | ✅ Done    |
| Async support (`aget()`)              | Optional extra        | `V2/core.py`                                       | ✅ Done    |
| Relationship traversal                | `study.samples...`    | `DEFAULT_LINKED_PROXY_CONFIG` in `V2/metadata.py`  | ⚠️ Partial |

### What's Missing (~55%)

#### Core Architecture

| Component        | Guide Spec                                                                  | Current State                            | Gap                   |
| ---------------- | --------------------------------------------------------------------------- | ---------------------------------------- | --------------------- |
| `QuerySet`       | Lazy query builder, separate from execution, with `_clone()`                | `Mgnifier` combines building + execution | Full class needed     |
| `SingleResource` | Individual item with lazy-loaded attribute access + relationship navigation | Not implemented                          | Full class needed     |
| `QueryExecutor`  | Dedicated API call + pagination handler                                     | Logic embedded in `Mgnifier`             | Extraction + refactor |

#### Missing API Methods

| Method                           | Description                                                 | Status     |
| -------------------------------- | ----------------------------------------------------------- | ---------- |
| `.to_json()`                     | Return results as `List[dict]`                              | ✅ Done    |
| `.to_list()`                     | Return results as raw Python list                           | ✅ Done    |
| `.order_by(*fields)`             | Add ordering params                                         | ❌ Missing |
| `.verbose()`                     | Progress bars via tqdm (instead `hide_progress: bool` flag) | ✅ alt     |
| `.page_size(n)`                  | Control pagination page size                                | ✅ Done    |
| `.page(n)`                       | Fetch a specific page                                       | ✅ Done    |
| `.exists()`                      | Boolean existence check                                     | ❌ Missing |
| `.first()`                       | Return first result                                         | ✅ Done    |
| `.explain()`                     | Print URLs that would be called                             | ✅ Done    |
| `analyses[:5]` slicing via proxy | Slice through proxy chain, not just Mgnifier                | ⚠️ Partial |
| `analyses["MGYA00001231"]`       | Return `SingleResource`, not proxy                          | ❌ Missing |

#### Quality & Completeness

| Item                     | Target                                        | Status     |
| ------------------------ | --------------------------------------------- | ---------- |
| Test suite               | >85% coverage                                 | ⚠️ Started |
| CLI (`cli.py`)           | Functional CLI                                | ❌ Stub    |
| `GenomesProxy`           | Query genomes endpoint                        | ❌ TODO    |
| `DatasetBuilder` exports | `.to_df()` on annotations                     | ❌ TODO    |
| `describe_resources()`   | Human-readable resource info                  | ❌ TODO    |
| `to_df()` naming         | Guide uses `to_df()`, code uses `to_pandas()` | ✅ Done    |

---

## Implementation Plan — 1 Week

### Guiding Principles

- Preserve the existing `Mgnifier` and proxy classes; refactor and extend, don't rewrite.
- Each day ends with working, testable code.
- Tests are written alongside code, not after.
- The old `Mgnifier`-based API must not break (backwards compatibility).

---

### Day 1 — `QuerySet` + `QueryExecutor`

**Goal:** Extract the query-building and execution logic from `Mgnifier` into dedicated `QuerySet` and `QueryExecutor` classes. This is the foundation everything else builds on.

**Files to create/modify:**

- Create `mgnipy/V2/query_set.py` — `QuerySet` class
- Create `mgnipy/V2/query_executor.py` — `QueryExecutor` class
- Modify `mgnipy/V2/core.py` — have `Mgnifier` delegate to `QuerySet`

**`QuerySet` must support:**

```python
qs = QuerySet("analyses", config)
qs.filter(biome="root:soil")       # returns cloned QS
qs.order_by("-created")            # returns cloned QS
qs.limit(100)                      # returns cloned QS
qs.offset(20)                      # returns cloned QS
qs.page_size(50)                   # returns cloned QS
qs.verbose()                       # returns cloned QS
qs.to_df()                         # triggers execution → DataFrame
qs.to_json()                       # triggers execution → List[dict]
qs.to_list()                       # triggers execution → List
qs.count()                         # lightweight count-only call
qs.exists()                        # bool
qs.first()                         # single item or None
qs.explain()                       # prints URLs, no API call
qs.dry_run()                       # alias for explain()
for item in qs: ...                # __iter__
qs[0], qs[:5]                      # __getitem__ after execution
```

**`QueryExecutor` must:**

- Accept resource name + config
- Instantiate the correct v1/v2 client
- Handle paginated fetching with optional tqdm progress bar
- Return raw result list

**Tests to write (`tests/unit/test_query_set.py`):**

- Filter cloning doesn't mutate original
- `to_df()` / `to_json()` / `to_list()` return correct types
- `explain()` outputs correct URL without making API call
- Pagination logic (mock the client)

---

### Day 2 — `SingleResource`

**Goal:** Implement `SingleResource` so that `mgnipy.analyses["MGYA00001231"]` returns a lazy-loaded object with attribute access and relationship navigation.

**Files to create/modify:**

- Create `mgnipy/V2/single_resource.py` — `SingleResource` class
- Modify `mgnipy/V2/metadata.py` — update proxy `__getitem__` to return `SingleResource` for string/accession keys

**`SingleResource` must support:**

```python
analysis = mgnipy.analyses["MGYA00001231"]

# Lazy attribute access (no API call until here)
print(analysis.accession)
print(analysis.experiment_type)
print(analysis.biome)

# Relationship navigation → returns ResourceProxy (lazy)
annotations_df = analysis.annotations.to_df()
downloads = analysis.downloads.to_df()

# Utility
analysis.to_dict()    # raw dict
analysis.refresh()    # re-fetch from API
```

**Key design notes:**

- Data is not fetched until the first attribute access (`_load()` pattern).
- Relationships detected from `_data["relationships"]` keys → return a `ResourceProxy`.
- Use `SUPPORTED_RELATIONSHIPS` dict to validate relationship names and avoid bad API calls.

**Tests to write (`tests/unit/test_single_resource.py`):**

- No API call on instantiation
- Attribute access triggers exactly one load
- Second attribute access uses cache (no second API call)
- Unknown attribute raises `AttributeError`
- `refresh()` clears cache and re-fetches
- Relationship access returns a proxy

---

### Day 3 — Wire Proxies to `QuerySet` + `SingleResource`

**Goal:** Make the full proxy chain (`mgnipy.analyses.filter(...).to_df()` and `mgnipy.analyses["MGYA00001231"]`) work end-to-end using the new components.

**Files to modify:**

- `mgnipy/V2/metadata.py` — refactor all proxy classes to use `QuerySet` internally
- `mgnipy/mgnipy.py` — pass `config` through to proxies

**Proxy `__getitem__` logic:**

```python
def __getitem__(self, key):
    if isinstance(key, str):          # accession
        return SingleResource(self.resource_name, key, self.config)
    elif isinstance(key, int):        # index
        return QuerySet(...).offset(key).limit(1).first()
    elif isinstance(key, slice):      # slice
        return QuerySet(...).slice(key)
```

**Proxy forwarding — proxies should delegate to `QuerySet`:**

```python
def filter(self, **filters) -> QuerySet:
    return QuerySet(self.resource_name, self.config).filter(**filters)

def get(self, limit=None) -> QuerySet:
    return QuerySet(self.resource_name, self.config).limit(limit)

def order_by(self, *fields) -> QuerySet:
    return QuerySet(self.resource_name, self.config).order_by(*fields)
```

**Relationship traversal** (`DEFAULT_LINKED_PROXY_CONFIG`) should remain, but return a `QuerySet` (not a bare proxy) when chained after `SingleResource`.

**Tests to write (`tests/integration/test_proxy_chain.py`):**

- `mgnipy.analyses.filter(biome="root:soil")` returns `QuerySet` (no API call)
- `mgnipy.analyses["MGYA00001231"]` returns `SingleResource`
- `mgnipy.analyses[:5]` returns `QuerySet` with correct limit/offset
- Full chain `mgnipy.studies.filter(...).to_df()` makes API call and returns DataFrame

---

### Day 4 — Output Formatters + Verbose/Progress

**Goal:** Complete all output formatters and add `verbose()` / progress bar support.

**Files to modify:**

- `mgnipy/V2/query_set.py` — add `to_json()`, `to_list()`, fix `to_df()` naming, add verbose tqdm

**Output methods:**

```python
def to_df(self) -> pd.DataFrame:
    results = self._execute()
    return pd.DataFrame([r for r in results])  # flatten attributes

def to_json(self) -> list[dict]:
    return [item if isinstance(item, dict) else item.to_dict()
            for item in self._execute()]

def to_list(self) -> list:
    return self._execute()
```

**Verbose / progress:**

```python
def verbose(self, enabled: bool = True) -> "QuerySet":
    new_qs = self._clone()
    new_qs._verbose = enabled
    return new_qs

# In QueryExecutor.execute():
pbar = tqdm(total=total_pages, desc=f"Fetching {resource_name}", disable=not verbose)
```

**Rename `to_df()` → `to_df()`** on `Mgnifier` (keep `to_pandas` as deprecated alias).

**Tests to write (`tests/unit/test_formatters.py`):**

- `to_df()` returns a `pd.DataFrame`
- `to_json()` returns a list of dicts
- `to_list()` returns a plain list
- `verbose()` clone doesn't mutate original
- Progress bar appears with `verbose=True` (capture stdout)

---

### Day 5 — `GenomesProxy` + `DatasetBuilder` + `describe_resources()`

**Goal:** Close the remaining TODO items in the proxy layer and entry point.

**Files to modify:**

- `mgnipy/V2/metadata.py` — implement `GenomesProxy`
- `mgnipy/V2/datasets.py` — add `to_df()` / `to_json()` to `DatasetBuilder`
- `mgnipy/mgnipy.py` — implement `describe_resources()`

**`GenomesProxy`:**

```python
class GenomesProxy(ResourceProxy):
    resource_name = SupportedEndpoints.GENOMES.value

    def filter(self, **filters) -> QuerySet:
        return QuerySet(self.resource_name, self._config).filter(**filters)
```

**`DatasetBuilder` exports:**

```python
class DatasetBuilder:
    def to_df(self) -> pd.DataFrame: ...
    def to_json(self) -> list[dict]: ...
    def to_list(self) -> list: ...
```

**`describe_resources()`:** fetch first page of the API root and return a dict of resource → description strings.

**Tests to write (`tests/unit/test_genomes.py`, `tests/unit/test_datasets.py`):**

- GenomesProxy returns correct `QuerySet`
- DatasetBuilder exports work for each format

---

### Day 6 — Test Coverage Push + CLI Stub

**Goal:** Get test coverage above 85% and make `cli.py` functional for basic commands.

**Files to modify:**

- `tests/` — fill coverage gaps identified by `pytest --cov`
- `mgnipy/cli.py` — implement basic CLI commands

**CLI commands to implement:**

```bash
mgnipy list-resources                         # print supported endpoints
mgnipy get analyses --limit 10 --biome soil   # fetch and print as JSON
mgnipy get studies --limit 5                  # fetch and print as JSON
mgnipy describe analyses                      # describe a resource
```

**Coverage targets by module:**
| Module | Target |
|---|---|
| `V2/query_set.py` | >90% |
| `V2/single_resource.py` | >90% |
| `V2/metadata.py` | >85% |
| `V2/query_executor.py` | >85% |
| `mgnipy.py` | >85% |

**Run checks:**

```bash
pytest --cov=mgnipy --cov-report=term-missing
ruff check mgnipy/
```

---

### Day 7 — Integration Testing + Documentation + Polish

**Goal:** End-to-end integration tests against the real API, docstrings on all public methods, type hints, and a clean README example.

**Integration tests (`tests/integration/`):**

```python
# These hit the real EBI API — mark with @pytest.mark.integration
def test_get_analyses():
    client = MGnipy()
    df = client.analyses.get(5).to_df()
    assert len(df) == 5
    assert "accession" in df.columns

def test_filter_by_biome():
    client = MGnipy()
    df = client.analyses.filter(biome="root:soil").limit(3).to_df()
    assert len(df) <= 3

def test_single_resource_access():
    client = MGnipy()
    study = client.studies["MGYS00001422"]
    assert study.accession == "MGYS00001422"

def test_relationship_traversal():
    client = MGnipy()
    study = client.studies["MGYS00001422"]
    df = study.samples.to_df()
    assert len(df) > 0
```

**Docstrings + type hints** — add to all public methods in:

- `QuerySet`
- `SingleResource`
- All proxy classes
- `MGnipy`

**Final checklist:**

- [ ] All guide API examples work as shown
- [ ] `to_df()`, `to_json()`, `to_list()` work
- [ ] Lazy evaluation verified (no premature calls)
- [ ] `mgnipy.analyses["MGYA..."]` returns `SingleResource`
- [ ] Slicing `mgnipy.analyses[:5]` works
- [ ] `order_by()` works
- [ ] `verbose()` shows progress bar
- [ ] `explain()` / `dry_run()` prints URL plan
- [ ] Test coverage >85%
- [ ] `ruff` passes with no errors
- [ ] Old `Mgnifier` API still works (no regressions)

---

## File Map — New Files to Create

```
mgnipy/V2/
├── query_set.py          # Day 1 — QuerySet class
├── query_executor.py     # Day 1 — QueryExecutor class
├── single_resource.py    # Day 2 — SingleResource class
└── (existing files, refactored)

tests/
├── unit/
│   ├── test_query_set.py      # Day 1
│   ├── test_single_resource.py # Day 2
│   ├── test_proxy_chain.py    # Day 3
│   ├── test_formatters.py     # Day 4
│   ├── test_genomes.py        # Day 5
│   └── test_datasets.py       # Day 5
└── integration/
    └── test_end_to_end.py     # Day 7
```

---

## Risk Register

| Risk                                                            | Mitigation                                                                   |
| --------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| V2 API endpoint shape differs from what `QueryExecutor` assumes | Read existing `mgni_py_v2` client method signatures before Day 1             |
| Relationship endpoints not consistent across resource types     | Build `SUPPORTED_RELATIONSHIPS` map on Day 2 from actual API docs            |
| `SingleResource` attribute access clashes with Python internals | Use explicit `_data` loading, only intercept unknown attrs via `__getattr__` |
| Breaking the existing `Mgnifier` API                            | Keep `Mgnifier` in place; proxy classes simply delegate to `QuerySet`        |
| Coverage target hard to hit in one day (Day 6)                  | Write tests as you go on Days 1–5, Day 6 is gap-fill only                    |
