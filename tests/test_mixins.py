from types import SimpleNamespace

from mgnipy.V2.mixins import CheckpointMixin


def checkpoint_handler(tmp_path):
    handler = CheckpointMixin()
    handler.config = SimpleNamespace(cache_dir=tmp_path)
    handler.resource = "studies"
    handler.params = {"search": "marine"}
    handler.count = 3
    handler.num_requests = 1
    handler._results = None
    return handler


def test_checkpoint_writes_and_loads_json_page_and_manifest(tmp_path):
    handler = checkpoint_handler(tmp_path)
    items = [{"accession": "S1"}]

    handler.write_results(1, items)

    loaded = checkpoint_handler(tmp_path)
    assert loaded.load_cache() == [1]
    assert loaded._results == {1: items}
    assert loaded.count == 3
    assert loaded.num_requests == 1


def test_checkpoint_writes_and_loads_binary_page(tmp_path):
    handler = checkpoint_handler(tmp_path)

    handler.write_results(1, b"download")

    loaded = checkpoint_handler(tmp_path)
    assert loaded.load_cache_results() == [1]
    assert loaded._results == {1: b"download"}


def test_checkpoint_skips_disk_when_cache_disabled():
    handler = checkpoint_handler(None)

    handler.write_results(1, [{"id": 1}])

    assert handler.cache_path is None
    assert handler.load_cache() == []


def test_checkpoint_clear_cache_removes_cached_pages(tmp_path):
    handler = checkpoint_handler(tmp_path)
    handler.write_results(1, [{"id": 1}])
    cache_path = handler.cache_path

    handler.clear_cache()

    assert not cache_path.exists()
