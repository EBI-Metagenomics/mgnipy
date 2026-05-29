import json

from mgnipy.cli import _build_parser, main


class FakeClient:
    def __init__(self, *args, **kwargs):
        self.list_resources_called = False

    def list_resources(self):
        self.list_resources_called = True
        return ["studies", "samples"]


class FakeMgifier:
    def __init__(self, resource, params):
        self.resource = resource
        self.params = params
        self.explained = False
        self.get_calls = []

    def explain(self):
        self.explained = True

    def get(self, limit=None, safety=False):
        self.get_calls.append((limit, safety))

    def to_list(self):
        return [{"id": 1}, {"id": 2}, {"id": 3}]


def test_build_parser_includes_supported_resource_choices():
    # Parser choices should reflect the endpoint enum used by the CLI.
    parser = _build_parser()
    get_parser = parser._subparsers._group_actions[0].choices["get"]

    assert (
        "studies" in get_parser._actions[1].choices
    ), "The get command should accept common public resources."
    assert (
        "_downloads" in get_parser._actions[1].choices
    ), "The CLI currently exposes the internal downloads endpoint choice."


def test_main_list_resources_uses_client(monkeypatch, capsys):
    # A list-resources invocation should print the resources returned by the MGnipy client.
    monkeypatch.setattr("mgnipy.cli.MGnipy", FakeClient)

    main(["list-resources"])

    output = capsys.readouterr().out.strip()
    assert json.loads(output) == [
        "studies",
        "samples",
    ], "The CLI should serialize the client's resource list as JSON."


def test_main_get_prints_requested_records(monkeypatch, capsys):
    # The get command should drive the query object and trim the output to the requested limit.
    monkeypatch.setattr("mgnipy.cli.MGnipy", FakeClient)
    monkeypatch.setattr("mgnipy.cli.MGnifier", FakeMgifier)

    main(["get", "studies", "--limit", "2", "--page-size", "10"])

    output_lines = capsys.readouterr().out.strip().splitlines()

    assert (
        output_lines[0] == "<class 'int'>"
    ), "The CLI currently prints the type of the parsed limit argument for debugging."
    assert json.loads("\n".join(output_lines[1:])) == [
        {"id": 1},
        {"id": 2},
    ], "The CLI output should be truncated to the requested record limit."
