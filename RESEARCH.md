# Research notes: mcp-tool-schema-lint

## Observed source facts

The MCP Python SDK migration guide documents stricter protocol validation and the required object type for Tool.inputSchema. MCP Inspector issue #1388 requests showing data types and validation details in its tool form. The linter deliberately emits normative errors separately from advisory warnings.

Sources:
- https://github.com/modelcontextprotocol/python-sdk/blob/main/docs/migration.md
- https://github.com/modelcontextprotocol/inspector/issues/1388
- https://github.com/modelcontextprotocol/python-sdk/blob/main/docs/servers/tools.md

## Selection judgment

Lint a captured MCP tools/list response for basic protocol shape errors and actionable schema-description gaps. This is a narrowly scoped offline utility derived from those observations. The sources do not establish prevalence, market size, or expected stars.
