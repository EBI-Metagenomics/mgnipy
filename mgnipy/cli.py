import argparse
import json
import sys

from mgnipy import MGnipy
from mgnipy._models.CONSTANTS import SupportedEndpoints
from mgnipy.V2.core import MGnifier


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="MGnipy CLI")

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("list-resources", help="Print supported API resources")

    get = subparsers.add_parser("get", help="Get a resource")
    get.add_argument(
        "resource",
        help="Resource name",
        choices=[e.value for e in SupportedEndpoints],
    )
    get.add_argument("--limit", type=int, help="Maximum number of items to return")
    get.add_argument(
        "--page-size", type=int, help="Number of items per page", default=25
    )

    return parser


def main(argv=None):
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    client = MGnipy()

    if args.command == "list-resources":
        resources = client.list_resources()
        print(json.dumps(resources, indent=2))
    elif args.command == "get":
        mg = MGnifier(resource=args.resource, params={"page_size": args.page_size})
        print(type(args.limit))

        mg.explain()
        mg.get(limit=args.limit, safety=False)

        records = mg.to_list() or []

        print(json.dumps(records[: args.limit], indent=2, default=str))


if __name__ == "__main__":
    main()
