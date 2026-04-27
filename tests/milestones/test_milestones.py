"""
Milestone tests for PyPI readiness.

Each class represents one fix milestone. Tests inside each class cover:
  - current_state: documents what the code does RIGHT NOW (should pass without any fix)
  - after_fix:     what should be true AFTER the fix is applied (marked xfail until then)

Usage
-----
Before any fix:
    pytest tests/milestones/test_milestones.py -v
    # xfail tests show as 'x', current_state tests show as '.'

After applying a fix, remove the @pytest.mark.xfail decorator from
the corresponding class's after_fix tests and re-run. They should turn green.

All tests are offline / do not hit the real MGnify API.
"""

import importlib
import subprocess
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# M1 — cli.py must exist
# ---------------------------------------------------------------------------


class TestM1_CLI:
    """
    Milestone 1: Create mgnipy/cli.py with a main() entry point.

    pyproject.toml declares:
        mgnipy-hello = "mgnipy.cli:main"
    but mgnipy/cli.py does not exist, so pip install produces a broken entry point.

    Fix: create mgnipy/cli.py with at minimum:
        def main(): ...
    """

    @pytest.mark.xfail(strict=True, reason="cli.py does not exist yet")
    def test_current_state_no_cli_module(self):
        """Right now, importing mgnipy.cli raises ModuleNotFoundError."""
        with pytest.raises((ModuleNotFoundError, ImportError)):
            importlib.import_module("mgnipy.cli")

    def test_after_fix_cli_importable(self):
        mod = importlib.import_module("mgnipy.cli")
        assert hasattr(mod, "main"), "mgnipy.cli must expose a main() function"
        assert callable(mod.main)

    def test_after_fix_entry_point_runs(self):
        result = subprocess.run(
            [sys.executable, "-m", "mgnipy.cli", "--help"],
            capture_output=True,
            text=True,
        )
        assert (
            result.returncode == 0
        ), f"cli --help exited {result.returncode}: {result.stderr}"


# ---------------------------------------------------------------------------
# M2 — Config must flow from MGnipy into proxies
# ---------------------------------------------------------------------------


class TestM2_ConfigFlow:
    """
    Milestone 2: MGnipy.__getattr__ must pass self._config into the proxy constructor.

    Current bug (mgnipy/mgnipy.py:52):
        return V2_ENDPOINT_ALL_PROXIES[_end]()   # config discarded

    Fix:
        return V2_ENDPOINT_ALL_PROXIES[_end](base_url=str(self._config.base_url))

    After this fix, a custom base_url (or auth token) set on MGnipy will actually
    be used by the proxy when it makes API calls.
    """

    @pytest.mark.xfail(strict=True, reason="MGnipy now passes config to proxy")
    def test_config_used(self):
        from mgnipy import MGnipy
        from mgnipy._models.config import MgnipyConfig

        default_url = MgnipyConfig().base_url
        custom_url = "https://custom.example.com"

        client = MGnipy(base_url=custom_url)
        proxy = client.studies

        assert str(proxy.base_url) == str(default_url), (
            "proxy silently uses default URL even when client was "
            "constructed with a custom base_url."
            f"\nClient base_url: {custom_url}, Proxy base_url: {proxy.base_url}"
        )

    def test_custom_base_url_flows_to_proxy(self):
        from mgnipy import MGnipy

        custom_url = "https://custom.example.com"
        client = MGnipy(base_url=custom_url)
        proxy = client.studies
        assert str(proxy.base_url).strip("/") == str(custom_url).strip("/")

    def test_default_url_still_works(self):
        """Default URL works regardless of fix — this is a regression guard."""
        from mgnipy import MGnipy
        from mgnipy._models.config import MgnipyConfig

        client = MGnipy()
        proxy = client.studies
        assert str(proxy._base_url) == str(MgnipyConfig().base_url)


# ---------------------------------------------------------------------------
# M3 — pytest scope must not require live API calls
# ---------------------------------------------------------------------------


class TestM3_PytestScope:
    """
    Milestone 3: Narrow pytest's doctest collection so that running the test suite
    offline does not attempt real API calls.

    Current problem (pyproject.toml):
        addopts = "--doctest-modules"
    Without testpaths, pytest scans the entire mgnipy package and runs every >>> example,
    many of which call the live API.

    Fix (pyproject.toml):
        [tool.pytest.ini_options]
        addopts = "--doctest-modules"
        testpaths = ["tests", "mgnipy/_shared_helpers", "mgnipy/mgnipy.py"]
    """

    @pytest.mark.xfail(strict=True, reason="testpaths not yet configured")
    def test_current_state_testpaths_not_set(self):
        """pyproject.toml does not yet have a testpaths restriction."""
        pyproject = Path(__file__).parents[2] / "pyproject.toml"
        content = pyproject.read_text()
        assert (
            "testpaths" not in content
        ), "testpaths is already set — check if M3 has been applied."

    def test_after_fix_testpaths_configured(self):
        pyproject = Path(__file__).parents[2] / "pyproject.toml"
        content = pyproject.read_text()
        print(content)
        assert "testpaths" in content
        assert "mgnipy/_shared_helpers" in content


# ---------------------------------------------------------------------------
# M4 — Package builds and installs cleanly
# ---------------------------------------------------------------------------


class TestM4_BuildAndInstall:
    """
    Milestone 4: `python -m build` must produce a valid wheel and sdist,
    and the wheel must install without errors.

    This test checks the prerequisites (pyproject.toml structure) rather than
    actually running the build (which would be slow and require build tools).
    """

    def test_current_state_entry_point_declared(self):
        """pyproject.toml declares the cli entry point (even though cli.py is missing)."""
        pyproject = Path(__file__).parents[2] / "pyproject.toml"
        content = pyproject.read_text()
        assert "mgnipy-hello" in content
        assert "mgnipy.cli:main" in content

    def test_current_state_package_importable(self):
        """The mgnipy package itself imports without error."""
        import mgnipy

        assert hasattr(mgnipy, "MGnipy")
        assert mgnipy.__version__ is not None

    def test_current_state_version_set(self):
        """Version is available (set via setuptools_scm from git tags)."""
        import mgnipy

        assert isinstance(mgnipy.__version__, str)
        assert len(mgnipy.__version__) > 0

    def test_after_fix_wheel_entry_point_resolves(self):
        """After M1 is fixed, the entry point module must be importable."""
        import mgnipy.cli

        assert callable(mgnipy.cli.main)


# ---------------------------------------------------------------------------
# M5 — README uses accurate class names and working examples
# ---------------------------------------------------------------------------


class TestM5_README:
    """
    Milestone 5: README.md must not reference removed or renamed classes.

    Current problem: README shows StudiesMGnifier and GoSlimCollector,
    neither of which exists in the codebase.

    Fix: rewrite README with accurate examples using MGnifier / MGnipy / proxy classes.
    """

    README = Path(__file__).parents[2] / "README.md"

    @pytest.mark.xfail
    def test_current_state_stale_class_names_present(self):
        """README currently contains at least one stale class name."""
        content = self.README.read_text()
        stale = [
            name for name in ("StudiesMGnifier", "GoSlimCollector") if name in content
        ]
        assert len(stale) > 0, (
            "Expected to find stale class names in README but found none. "
            "Check if M5 has already been applied."
        )

    def test_after_fix_no_stale_class_names(self):
        content = self.README.read_text()
        for stale in ("StudiesMGnifier", "GoSlimCollector"):
            assert (
                stale not in content
            ), f"README still references removed class: {stale}"

    def test_after_fix_has_to_df_example(self):
        """After rewrite, README should show the to_df() output formatter."""
        content = self.README.read_text()
        assert "to_df()" in content

    @pytest.mark.xfail(
        strict=True,
        reason="README not yet updated — TestPyPI workaround should be removed",
    )
    def test_after_fix_no_testpypi_workaround(self):
        """After rewrite, install should be a clean pip install without --index-url TestPyPI."""
        content = self.README.read_text()
        assert "test.pypi.org" not in content


# ---------------------------------------------------------------------------
# Regression: things that must keep working throughout all fixes
# ---------------------------------------------------------------------------


class TestRegressions:
    """
    These tests verify core functionality that exists today and must not break
    as the milestones above are applied.

    All tests here are expected to PASS right now. If any fail, something regressed.

    Note: these tests hit the real MGnify API. Skip them offline with:
        pytest -m "not live_api"
    """

    def test_mgnifier_imports(self):
        from mgnipy.V2.core import MGnifier

        assert MGnifier is not None

    def test_queryset_imports(self):
        from mgnipy.V2.query_set import QuerySet

        assert QuerySet is not None

    def test_proxy_classes_import(self):
        from mgnipy.V2.proxies import (
            Analyses,
            Biomes,
            Genomes,
            Runs,
            Samples,
            Studies,
        )

        for cls in (Analyses, Biomes, Genomes, Runs, Samples, Studies):
            assert cls is not None

    def test_mgnipy_facade_imports(self):
        from mgnipy import MGnipy

        assert MGnipy is not None

    def test_mgnipy_instantiates(self):
        from mgnipy import MGnipy

        client = MGnipy()
        assert client is not None

    def test_mgnipy_list_resources(self):
        from mgnipy import MGnipy

        client = MGnipy()
        resources = client.list_resources()
        assert isinstance(resources, list)
        assert len(resources) > 0
        assert "studies" in resources

    def test_queryset_filter_is_immutable_clone(self):
        from mgnipy.V2.query_set import QuerySet

        qs = QuerySet(resource="studies")
        qs2 = qs.filter(biome="root:Environmental")
        assert qs is not qs2
        assert "biome" not in qs.params
        assert qs2.params.get("biome") == "root:Environmental"

    def test_queryset_page_size_clone(self):
        from mgnipy.V2.query_set import QuerySet

        qs = QuerySet(resource="studies")
        qs2 = qs.page_size(10)
        assert qs is not qs2
        assert qs2.params.get("page_size") == 10

    def test_queryset_request_url_builds(self):
        from mgnipy.V2.query_set import QuerySet

        qs = QuerySet(resource="studies", params={"page_size": 5})
        url = qs.request_url
        assert "studies" in url or "metagenomics" in url

    def test_config_defaults(self):
        from mgnipy._models.config import MgnipyConfig

        config = MgnipyConfig()
        assert config.base_url is not None
        assert (
            "ebi.ac.uk" in str(config.base_url)
            or "mgnipy" in str(config.base_url).lower()
        )

    @pytest.mark.live_api
    def test_mgnifier_first_page_studies(self):
        from mgnipy.V2.core import MGnifier

        mg = MGnifier(resource="studies", params={"page_size": 3})
        mg.first()
        df = mg.to_df()
        assert df is not None
        assert len(df) == 3

    @pytest.mark.live_api
    def test_mgnifier_to_polars(self):
        from mgnipy.V2.core import MGnifier

        mg = MGnifier(resource="studies", params={"page_size": 3})
        mg.first()
        df = mg.to_polars()
        assert df is not None
        assert df.height == 3

    @pytest.mark.live_api
    def test_mgnifier_to_list(self):
        from mgnipy.V2.core import MGnifier

        mg = MGnifier(resource="studies", params={"page_size": 3})
        mg.first()
        result = mg.to_list()
        assert isinstance(result, list)
        assert len(result) == 3

    @pytest.mark.live_api
    def test_mgnifier_to_json(self):
        from mgnipy.V2.core import MGnifier

        mg = MGnifier(resource="studies", params={"page_size": 3})
        mg.first()
        result = mg.to_json()
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.live_api
    def test_mgnifier_filter_then_fetch(self):
        from mgnipy.V2.core import MGnifier

        mg = MGnifier(resource="studies")
        filtered = mg.filter(biome_lineage="root:Environmental:Aquatic", page_size=2)
        filtered.first()
        df = filtered.to_df()
        assert df is not None

    @pytest.mark.live_api
    def test_mgnifier_dry_run_sets_count(self):
        from mgnipy.V2.core import MGnifier

        mg = MGnifier(resource="studies", params={"page_size": 5})
        mg.dry_run()
        assert mg.count is not None
        assert mg.total_pages is not None
        assert mg.count > 0
