from pathlib import Path
import re

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
FILE_PATTERNS = ["../README.md", "../Contributing.md", "**/*.md"]

ALERT_PATTERN = re.compile(
    r"^>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*$",
    re.IGNORECASE,
)
FENCE_PATTERN = re.compile(r"^\s*(`{3,}|~{3,})")


def markdown_files(patterns):
    """
    Returns a sorted list of Markdown files matching the given patterns.
    """

    files = set()

    for pattern in patterns:
        files.update(
            path
            for path in SCRIPT_DIR.glob(pattern)
            if path.is_file() and path.suffix == ".md"
        )

    return sorted(files)


def convert(text):
    """
    Converts GitHub-style alerts to MyST admonitions.
    """
    output = []
    in_code_fence = False
    alert_type = None

    for line in text.splitlines(keepends=True):
        if alert_type is not None:
            if line.startswith(">"):
                body = line[1:]
                if body.startswith(" "):
                    body = body[1:]
                output.append(body)
                continue

            output.append("```\n")
            alert_type = None

        if not in_code_fence:
            match = ALERT_PATTERN.match(line.rstrip("\r\n"))
            if match:
                alert_type = match.group(1).lower()
                output.append(f"```{{{alert_type}}}\n")
                continue

        output.append(line)

        if FENCE_PATTERN.match(line):
            in_code_fence = not in_code_fence

    if alert_type is not None:
        output.append("```\n")

    return "".join(output)


def main():
    patterns = FILE_PATTERNS
    converted = 0

    for path in markdown_files(patterns):
        original = path.read_text()
        updated = convert(original)

        if updated != original:
            path.write_text(updated)
            converted += 1
            print(f"Converted {path.relative_to(REPO_ROOT)}")

    print(f"Converted {converted} Markdown file(s).")


if __name__ == "__main__":
    main()
