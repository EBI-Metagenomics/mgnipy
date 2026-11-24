#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

# Required fields to drop anywhere they appear in a schema.required list
DROP_REQUIRED_FIELDS = {"parent_identifier", "path"}

# Matches random suffixes like _c073800d at the end of operationIds
RANDOM_SUFFIX_RE = re.compile(r"_[0-9a-fA-F]{8}(?=(_|$))")


def clean_operation_id(op_id: str) -> str:
    return RANDOM_SUFFIX_RE.sub("", op_id)


def walk_and_patch(node, seen_operation_ids):
    if isinstance(node, dict):
        # Clean operationId and keep uniqueness
        if "operationId" in node and isinstance(node["operationId"], str):
            base = clean_operation_id(node["operationId"])
            candidate = base
            node["operationId"] = candidate
            seen_operation_ids.add(candidate)

        # Remove selected fields from required arrays
        if "required" in node and isinstance(node["required"], list):
            node["required"] = [
                field for field in node["required"] if field not in DROP_REQUIRED_FIELDS
            ]

        for value in node.values():
            walk_and_patch(value, seen_operation_ids)

    elif isinstance(node, list):
        for item in node:
            walk_and_patch(item, seen_operation_ids)


def main() -> int:
    if len(sys.argv) not in (2, 3):
        print(
            "Usage: preprocess_openapi_json.py <input.json> [output.json]",
            file=sys.stderr,
        )
        return 2

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) == 3 else input_path

    if not input_path.exists():
        print(f"File not found: {input_path}", file=sys.stderr)
        return 2

    data = json.loads(input_path.read_text(encoding="utf-8"))

    seen_operation_ids = set()
    walk_and_patch(data, seen_operation_ids)

    output_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
