# mcp-tool-schema-lint

Lint a captured MCP tools/list response for basic protocol shape errors and actionable schema-description gaps.

For MCP developers who want a fast offline check before exposing a tool schema to clients or agents.

## Quick start

Requires Python 3.11 or newer. There are no third-party dependencies. The CLI reads one JSON document from standard input and writes one deterministic JSON line.

```console
python mcp_tool_schema_lint.py < examples/input.json
```

Output:

```json
{"error_count":0,"issues":[],"ok":true,"tool_count":1,"warning_count":0}
```

To run the tests and the exact example check:

```console
python -m unittest discover -s tests -v
python examples/run_examples.py
```

Inputs are limited to 256 KiB; malformed, duplicate-key, or over-depth JSON fails with a fixed error code. Output avoids echoing schema descriptions and values; issue pointers can include schema object keys. No MCP server is started or contacted.

## Problem evidence and scope

The MCP Python SDK migration guide documents stricter protocol validation and the required object type for Tool.inputSchema. MCP Inspector issue #1388 requests showing data types and validation details in its tool form. The linter deliberately emits normative errors separately from advisory warnings.

This evidence describes specific reports and documented behavior. It does not establish how often the problem occurs or predict GitHub stars.

## Limits

Checks a documented subset of JSON Schema; it is not a complete draft validator and does not test any MCP client behavior. Description checks are advisory.

## License and attribution

MIT. This repository contains original code and synthetic fixtures; no upstream source code or assets are included.

## Verified environment

Python 3.11.15 on Windows and GitHub Actions on Ubuntu and Windows using Python 3.11.
