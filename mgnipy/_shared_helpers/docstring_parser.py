import inspect
import re
from typing import Optional

HEADER_ALIASES = {
    "Args": "args",
    "Arguments": "args",
    "Parameters": "args",
    "Raises": "raises",
    "Returns": "returns",
    "Yields": "yields",
    "Examples": "examples",
    "Example": "examples",
    "Notes": "notes",
    "Note": "notes",
    "See Also": "see_also",
    "References": "references",
    "Warnings": "warnings",
}

SECTION_FIELDS = tuple(
    sorted(set(HEADER_ALIASES.values()) | {"title", "description", "raw"})
)


def is_numpy_header(lines: list[str], i: int) -> bool:
    """
    Detect if lines[i] and lines[i+1] form a NumPy-style header

    Parameters
    ----------
    lines : list[str]
        The docstring split into lines
    i : int
        The index of the potential header line

    Returns
    -------
    bool
        True if lines[i] is a header and lines[i+1] is an underline of dashes, False otherwise
    """
    if i + 1 >= len(lines):
        return False
    header = lines[i].strip()
    underline = lines[i + 1].strip()
    return (
        header in HEADER_ALIASES
        and len(underline) >= len(header)
        and set(underline) <= {"-"}
    )


def extract_doc_sections(doc: str) -> dict[str, str]:
    """
    Extract sections from a docstring into a dict with keys like
    'title', 'description', 'args', 'returns', etc.
    Supports both Google-style and NumPy-style docstring formats.
    The 'raw' key contains the full cleaned docstring.

    Parameters
    ----------
    doc : str
        The docstring to parse

    Returns
    -------
    dict[str, str]
        A dictionary with keys for each section and the corresponding text

    Examples
    --------
    >>> doc = '''
    ... My Function
    ...
    ... This function does something.
    ...
    ... Args:
    ...     x (int): The first parameter.
    ...     y (str): The second parameter.
    ...
    ... Returns:
    ...     bool: True if successful, False otherwise.
    ... '''
    >>> sections = extract_doc_sections(doc)
    >>> sections['title']
    'My Function'
    >>> sections['description']
    'This function does something.'
    """
    if not doc:
        return {key: "" for key in SECTION_FIELDS}

    lines = inspect.cleandoc(doc).splitlines()
    sections = {key: "" for key in SECTION_FIELDS}
    sections["raw"] = inspect.cleandoc(doc)

    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1

    if i < len(lines):
        sections["title"] = lines[i].strip()
        i += 1

    current_key = "description"
    buffer = []

    while i < len(lines):
        line = lines[i].rstrip()

        if line.strip().endswith(":") and line.strip()[:-1] in HEADER_ALIASES:
            if buffer:
                sections[current_key] = "\n".join(buffer).strip()
                buffer = []
            current_key = HEADER_ALIASES[line.strip()[:-1]]
            i += 1
            continue

        if is_numpy_header(lines, i):
            if buffer:
                sections[current_key] = "\n".join(buffer).strip()
                buffer = []
            current_key = HEADER_ALIASES[lines[i].strip()]
            i += 2
            continue

        buffer.append(line)
        i += 1

    if buffer:
        sections[current_key] = "\n".join(buffer).strip()

    return sections


def parse_args_block(args_block: str) -> dict[str, str]:
    """
    Parse Args/Parameters text into {param_name: description}.
    Supports Google-style and NumPy-style parameter lines.

    Parameters
    ----------
    args_block : str
        The text block containing parameter descriptions

    Returns
    -------
    dict[str, str]
        A dictionary mapping parameter names to their descriptions
    """
    if not args_block.strip():
        return {}

    result: dict[str, str] = {}
    current_key: str | None = None
    pattern = re.compile(r"^\s*([a-zA-Z_]\w*)\s*(?:\((.*?)\)|:\s*(.*?))\s*:\s*(.*)$")

    for raw_line in args_block.splitlines():
        line = raw_line.rstrip()

        match = pattern.match(line)
        if match:
            name = match.group(1)
            type_a = match.group(2)
            type_b = match.group(3)
            desc = match.group(4)

            type_text = type_a or type_b or ""
            result[name] = (
                f"({type_text}) {desc}".strip() if type_text else desc.strip()
            )
            current_key = name
            continue

        if current_key and line.strip():
            result[current_key] += " " + line.strip()

    return result


def get_docstring(module: object, callable_name: str) -> str:
    """
    Extract the docstring from a callable within a module, falling back to the module docstring if the callable has no docstring.

    Parameters
    ----------
    module : object
        The module from which to extract the docstring.
    callable_name : str
        The name of the callable within the module.

    Returns
    -------
    str
        The extracted docstring.
    """
    fn = getattr(module, callable_name, None)
    doc = inspect.getdoc(fn) or inspect.getdoc(module) or ""
    return doc


def parse_docstring(
    docstring: str,
    arg_block: str = "args",
    as_dict: bool = False,
    schema_link: Optional[
        str
    ] = "https://www.ebi.ac.uk/metagenomics/api/v2/openapi.json",
) -> dict[str, str] | None:
    """
    Describes the supported parameters for the endpoint by parsing the docstring of the endpoint module.
    This allows for dynamic retrieval of parameter descriptions directly from the source documentation:
    [openapi.json spec](https://www.ebi.ac.uk/metagenomics/api/v2/openapi.json) via
    [openapi-python-client](https://github.com/openapi-generators/openapi-python-client)

    Parameters
    ----------
    docstring : str
        The docstring to parse.
    arg_block : str
        The block of the docstring containing argument descriptions.
    as_dict : bool
        If True, returns the description as a dictionary. If False, prints the description.

    Returns
    -------
    dict of str to str or None
        A dictionary mapping parameter names to their descriptions if as_dict is True, otherwise None.
    """
    sections = extract_doc_sections(docstring)
    parsed_args = parse_args_block(sections.get(arg_block, ""))

    # supported = self.list_supported_params()
    # parsed_args = {k: parsed_args.get(k, "") for k in supported}

    result = {
        "title": sections.get("title", ""),
        "description": sections.get("description", ""),
        "args": parsed_args,
        "raises": sections.get("raises", ""),
        "returns": sections.get("returns", ""),
        "examples": sections.get("examples", ""),
        "notes": sections.get("notes", ""),
        "schema_link": schema_link or "",
    }

    if as_dict:
        return result

    if result["title"]:
        print(result["title"])
    if result["description"]:
        print()
        print(result["description"])

    print("\nSupported parameters:")
    for key, value in result["args"].items():
        print(f"- {key}: {value}" if value else f"- {key}")

    return None
