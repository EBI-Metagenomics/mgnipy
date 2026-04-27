# MGnipy — PyPI Readiness Plan

## Session Goal

Get the repo into a state suitable for publishing a **draft release on PyPI** in a 2-hour pair programming session.

---

## Actual Status vs. Implementation Plan

The 7-day implementation plan in `IMPLEMENTATION_PLAN.md` was written when the codebase was estimated at ~45% complete. The repo has moved considerably further. Here is the real state:

### What Is Done

| Component | Location | Status |
|---|---|---|
| `QuerySet` — lazy query builder with filter/clone | `V2/query_set.py` | ✅ Done |
| `QueryExecutor` — paginated HTTP execution | `V2/query_executor.py` | ✅ Done |
| `MGnifier` — facade on top of QuerySet | `V2/core.py` | ✅ Done |
| All list proxy classes (Studies, Samples, Analyses, Runs, Biomes, Genomes, Assemblies) | `V2/proxies.py` | ✅ Done |
| All detail proxy classes (`*Detail`) | `V2/proxies.py` | ✅ Done |
| `to_df()` (pandas) | `V2/mixins.py` | ✅ Done |
| `to_polars()` | `V2/mixins.py` | ✅ Done |
| `to_json()` | `V2/mixins.py` | ✅ Done |
| `to_list()` | `V2/mixins.py` | ✅ Done |
| `dry_run()` / `preview()` / `explain()` / `list_urls()` | `V2/query_set.py` | ✅ Done |
| `filter(**kwargs)` — immutable clone | `V2/query_set.py` | ✅ Done |
| `page(n)` / `first()` / `get(limit)` | `V2/core.py` + executor | ✅ Done |
| Async: `aget()`, `apage()`, `afirst()` | `V2/core.py` + executor | ✅ Done |
| Relationship traversal infra | `V2/mixins.py`, `V2/endpoints.py` | ✅ Done |
| `MGazine` streaming/download (TSV, FASTA, GFF3, BIOM, JSON) | `V2/datasets.py` | ✅ Done |
| Auto-generated `emgapi_v2_client` | `emgapi_v2_client/` | ✅ Done |
| `MgnipyConfig` (Pydantic v2) | `_models/config.py` | ✅ Done |
| `MGnipy` facade + `list_resources()` | `mgnipy.py` | ✅ Done |

### What Is Missing or Broken

| Issue | Location | Severity |
|---|---|---|
| `cli.py` does not exist — entry point `mgnipy-hello` in `pyproject.toml` is broken | `pyproject.toml:93` | 🔴 **PyPI blocker** — breaks `pip install` |
| Config is never passed from `MGnipy` to proxies | `mgnipy.py:52` | 🔴 Silent bug — auth tokens, custom URLs silently ignored |
| README references non-existent classes (`StudiesMGnifier`, `GoSlimCollector`) | `README.md` | 🔴 First thing users see on PyPI |
| `--doctest-modules` in pytest config runs doctests across the entire package | `pyproject.toml:80` | 🟡 Breaks `pytest` in many envs without API access |
| `SingleResource` not implemented — `proxy["MGYS00001234"]` fetches immediately | `V2/mixins.py:496` | 🟡 Plan Day 2, not blocking publish |
| `.order_by()` / `.exists()` not implemented | — | 🟡 Nice-to-have |
| `describe_resources()` is a `pass` stub | `mgnipy.py:58` | 🟡 Non-blocking |
| `MGazine.__init__` indexes `_results` as a list but it is a dict | `V2/datasets.py` | 🟡 Runtime error if used |
| No CHANGELOG | — | 🟡 PyPI convention |
| Test coverage is very thin (one integration test, no unit tests, no mocking) | `tests/` | 🟡 Not blocking publish |

---

## 2-Hour Session Plan

### Hour 1 — Fix the Blockers

**M1 — Create `cli.py`** (~15 min)

`pyproject.toml` declares `mgnipy-hello = "mgnipy.cli:main"`. The file does not exist.
Any `pip install mgnipy` results in a broken entry point.

Steps:
- Create `mgnipy/cli.py` with a `main()` that accepts basic subcommands:
  `list-resources`, `get <resource> [--limit N] [--biome X]`
- Keep it minimal — just enough for the entry point to be valid and useful.

Before/after test: `tests/milestones/test_milestones.py::TestM1_CLI`

---

**M2 — Wire config through proxies** (~10 min)

`MGnipy.__getattr__` at `mgnipy.py:52` calls `V2_ENDPOINT_ALL_PROXIES[_end]()` with no arguments.
The `self._config` that was constructed in `__init__` is silently discarded.

Fix: pass config into the proxy constructor:
```python
return V2_ENDPOINT_ALL_PROXIES[_end](base_url=str(self._config.base_url))
```

Before/after test: `tests/milestones/test_milestones.py::TestM2_ConfigFlow`

---

**M3 — Fix pytest scope** (~20 min)

`pyproject.toml` has `addopts = "--doctest-modules"` which collects doctests from every file
in the package. This makes `pytest` hit the real API just by running tests.

Fix: narrow the doctest scope in `pyproject.toml`:
```toml
[tool.pytest.ini_options]
addopts = "--doctest-modules"
testpaths = ["tests", "mgnipy/_shared_helpers", "mgnipy/mgnipy.py"]
```

Before/after test: `tests/milestones/test_milestones.py::TestM3_PytestScope`

---

**M4 — Verify `python -m build` and test-install** (~15 min)

Run:
```bash
python -m build
pip install dist/mgnipy-*.whl --force-reinstall
mgnipy-hello --help
python -c "import mgnipy; print(mgnipy.__version__)"
```

All four must succeed.

---

### Hour 2 — Polish for PyPI

**M5 — Rewrite README** (~20 min)

The README shows `StudiesMGnifier` and `GoSlimCollector` — neither exists.
Replace with accurate, runnable examples using the current API.

Minimum viable README sections:
- What is MGnipy
- Install
- Quick start (3-5 lines of working code)
- Output formats
- License

Before/after test: `tests/milestones/test_milestones.py::TestM5_README`

---

**M6 — Add CHANGELOG** (~5 min)

Standard PyPI convention. Minimum entry:
```markdown
## 0.1.0 — 2026-04-22
Initial public release.
```

---

**M7 — Tag version and push** (~10 min)

CI in `.github/workflows/cicd.yml` publishes to TestPyPI on git tags.

```bash
git tag v0.1.0
git push origin v0.1.0
```

Then verify at: https://test.pypi.org/project/mgnipy/

---

### Deferred (after publish)

These are valid improvements but not needed to ship a draft:

- `SingleResource` (plan Day 2) — lazy accession-keyed objects
- `.order_by()`, `.exists()`
- `describe_resources()` implementation
- >85% test coverage with mocked API calls
- Full docstring pass on all public methods

---

## Running the Milestone Tests

```bash
# See all milestones and their current status
uv run pytest tests/milestones/test_milestones.py -v

# Run only a specific milestone
uv run pytest tests/milestones/test_milestones.py::TestM1_CLI -v

# Run after a fix — the xfail test for that milestone should now XPASS
# Remove the @pytest.mark.xfail decorator and re-run to confirm green
```

---

## Capability Demo

See `docs/tutorial/capabilities_demo.ipynb` for a runnable Jupyter notebook
demonstrating everything that works today and calling out what is broken.

```bash
uv run jupyter notebook docs/tutorial/capabilities_demo.ipynb
```
