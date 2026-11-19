#!/usr/bin/env python3
"""Offline, bounded linter for captured MCP tools/list snapshots."""
import json
import sys

MAX_BYTES = 256 * 1024
MAX_DEPTH = 64
MAX_TOOLS = 1024
MAX_NODES = 20000
JSON_TYPES = {"object", "array", "string", "number", "integer", "boolean", "null"}


class InputError(Exception):
    pass


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InputError("duplicate_json_key")
        result[key] = value
    return result


def walk_depth(value, depth=0):
    if depth > MAX_DEPTH:
        raise InputError("maximum_depth_exceeded")
    if isinstance(value, dict):
        for child in value.values():
            walk_depth(child, depth + 1)
    elif isinstance(value, list):
        for child in value:
            walk_depth(child, depth + 1)


def lint_schema(schema, base, issues, counter):
    counter[0] += 1
    if counter[0] > MAX_NODES:
        raise InputError("maximum_schema_nodes_exceeded")
    if isinstance(schema, bool):
        return  # JSON Schema permits true/false schemas.
    if not isinstance(schema, dict):
        issues.append({"tool": counter[1], "severity": "error", "code": "schema_must_be_object", "path": base})
        return
    kind = schema.get("type")
    if kind is not None:
        valid_type = (kind in JSON_TYPES if isinstance(kind, str) else
                      isinstance(kind, list) and bool(kind) and all(isinstance(t, str) and t in JSON_TYPES for t in kind)
                      and len(set(kind)) == len(kind))
        if not valid_type:
            issues.append({"tool": counter[1], "severity": "error", "code": "invalid_type_keyword", "path": base + "/type"})
    if "enum" in schema and (not isinstance(schema["enum"], list) or not schema["enum"]):
        issues.append({"tool": counter[1], "severity": "error", "code": "enum_must_be_nonempty_array", "path": base + "/enum"})
    properties = schema.get("properties")
    if properties is not None and not isinstance(properties, dict):
        issues.append({"tool": counter[1], "severity": "error", "code": "properties_must_be_object", "path": base + "/properties"})
        properties = {}
    if "required" in schema:
        required = schema["required"]
        if not isinstance(required, list) or any(not isinstance(name, str) for name in required):
            issues.append({"tool": counter[1], "severity": "error", "code": "required_must_be_string_array", "path": base + "/required"})
        else:
            if len(required) != len(set(required)):
                issues.append({"tool": counter[1], "severity": "error", "code": "required_contains_duplicate", "path": base + "/required"})
            for name in required:
                if isinstance(properties, dict) and name not in properties:
                    # JSON Schema permits required names supplied through $ref/allOf.
                    issues.append({"tool": counter[1], "severity": "warning", "code": "required_not_listed_locally", "path": base + "/required"})
    extra = schema.get("additionalProperties")
    if extra is not None and not isinstance(extra, (bool, dict)):
        issues.append({"tool": counter[1], "severity": "error", "code": "additional_properties_type_invalid", "path": base + "/additionalProperties"})
    if isinstance(extra, dict):
        lint_schema(extra, base + "/additionalProperties", issues, counter)
    items = schema.get("items")
    if items is not None:
        lint_schema(items, base + "/items", issues, counter)
    if isinstance(properties, dict):
        for key, child in sorted(properties.items()):
            child_path = base + "/properties/" + key.replace("~", "~0").replace("/", "~1")
            if isinstance(child, bool):
                lint_schema(child, child_path, issues, counter)
                continue
            if not isinstance(child, dict):
                issues.append({"tool": counter[1], "severity": "error", "code": "property_schema_must_be_object", "path": child_path})
                continue
            if not isinstance(child.get("description"), str) or not child["description"].strip():
                issues.append({"tool": counter[1], "severity": "warning", "code": "property_description_missing", "path": child_path + "/description"})
            lint_schema(child, child_path, issues, counter)
    for keyword in ("$defs", "definitions", "allOf", "anyOf", "oneOf", "not", "if", "then", "else", "prefixItems"):
        if keyword not in schema:
            continue
        child = schema[keyword]
        child_path = base + "/" + keyword
        if keyword in {"allOf", "anyOf", "oneOf", "prefixItems"}:
            if not isinstance(child, list):
                issues.append({"tool": counter[1], "severity": "error", "code": "schema_array_keyword_invalid", "path": child_path})
            else:
                for index, item in enumerate(child):
                    lint_schema(item, child_path + "/" + str(index), issues, counter)
        elif keyword in {"$defs", "definitions"}:
            if not isinstance(child, dict):
                issues.append({"tool": counter[1], "severity": "error", "code": "schema_definitions_must_be_object", "path": child_path})
            else:
                for key, item in sorted(child.items()):
                    lint_schema(item, child_path + "/" + key.replace("~", "~0").replace("/", "~1"), issues, counter)
        else:
            lint_schema(child, child_path, issues, counter)


def inspect(document):
    if not isinstance(document, dict) or set(document) != {"tools"}:
        raise InputError("top_level_keys_must_be_tools")
    tools = document["tools"]
    if not isinstance(tools, list) or len(tools) > MAX_TOOLS:
        raise InputError("tools_must_be_bounded_array")
    issues = []
    seen = set()
    counter = [0, 0]
    for ordinal, tool in enumerate(tools, 1):
        counter[1] = ordinal
        base = "/tools/" + str(ordinal - 1)
        if not isinstance(tool, dict):
            raise InputError("tool_entry_must_be_object")
        name = tool.get("name")
        if not isinstance(name, str) or not name.strip():
            issues.append({"tool": ordinal, "severity": "error", "code": "tool_name_missing", "path": base + "/name"})
        elif name in seen:
            issues.append({"tool": ordinal, "severity": "error", "code": "duplicate_tool_name", "path": base + "/name"})
        else:
            seen.add(name)
        if not isinstance(tool.get("description"), str) or not tool["description"].strip():
            issues.append({"tool": ordinal, "severity": "warning", "code": "tool_description_missing", "path": base + "/description"})
        schema = tool.get("inputSchema")
        if not isinstance(schema, dict):
            issues.append({"tool": ordinal, "severity": "error", "code": "input_schema_missing_or_invalid", "path": base + "/inputSchema"})
        else:
            if schema.get("type") != "object":
                issues.append({"tool": ordinal, "severity": "error", "code": "input_schema_type_must_be_object", "path": base + "/inputSchema/type"})
            lint_schema(schema, base + "/inputSchema", issues, counter)
    issues.sort(key=lambda row: (row.get("tool", 0), row["path"], row["code"]))
    errors = sum(row["severity"] == "error" for row in issues)
    return {"ok": errors == 0, "tool_count": len(tools), "error_count": errors,
            "warning_count": len(issues) - errors, "issues": issues}


def fail(code):
    sys.stdout.write(json.dumps({"error": code}, sort_keys=True, separators=(",", ":")) + "\n")
    return 2


def main():
    if sys.argv[1:] in (["--help"], ["-h"]):
        print("usage: mcp_tool_schema_lint.py < tools-list.json")
        return 0
    if sys.argv[1:]:
        return fail("arguments_not_supported")
    raw = sys.stdin.buffer.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        return fail("input_too_large")
    try:
        document = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_pairs)
        walk_depth(document)
        result = inspect(document)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return fail("invalid_json")
    except InputError as exc:
        return fail(str(exc))
    except RecursionError:
        return fail("maximum_depth_exceeded")
    sys.stdout.write(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
