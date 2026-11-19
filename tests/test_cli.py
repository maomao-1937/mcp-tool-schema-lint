import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "mcp_tool_schema_lint.py"


def run(document):
    return subprocess.run([sys.executable, str(SCRIPT)], input=document, text=True,
                          capture_output=True, cwd=ROOT, timeout=5)


class SchemaLintTests(unittest.TestCase):
    def test_valid_schema_exact_example(self):
        doc = '{"tools":[{"name":"lookup","description":"Find a record.","inputSchema":{"type":"object","properties":{"key":{"type":"string","description":"Record key."}},"required":["key"]}}]}'
        result = run(doc)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '{"error_count":0,"issues":[],"ok":true,"tool_count":1,"warning_count":0}\n')

    def test_missing_object_type_is_error(self):
        result = run('{"tools":[{"name":"x","description":"x","inputSchema":{"properties":{}}}]}')
        self.assertEqual(result.returncode, 1)
        self.assertIn('"code":"input_schema_type_must_be_object"', result.stdout)

    def test_required_name_missing_from_local_properties_is_warning(self):
        result = run('{"tools":[{"name":"x","inputSchema":{"type":"object","properties":{},"required":["secret-name"]}}]}')
        self.assertEqual(result.returncode, 0)
        self.assertIn("required_not_listed_locally", result.stdout)
        self.assertNotIn("secret-name", result.stdout)

    def test_duplicate_tool_name_is_flagged(self):
        tool = '{"name":"internal_tool_7","description":"ok","inputSchema":{"type":"object"}}'
        result = run('{"tools":[' + tool + ',' + tool + ']}')
        self.assertIn('"code":"duplicate_tool_name"', result.stdout)
        self.assertNotIn("internal_tool_7", result.stdout)

    def test_missing_descriptions_are_warnings(self):
        result = run('{"tools":[{"name":"x","inputSchema":{"type":"object","properties":{"n":{"type":"integer"}}} }]}')
        self.assertEqual(result.returncode, 0)
        self.assertIn('"severity":"warning"', result.stdout)

    def test_invalid_enum_and_required(self):
        result = run('{"tools":[{"name":"x","inputSchema":{"type":"object","properties":{},"required":[4],"enum":[]}}]}')
        self.assertEqual(result.returncode, 1)
        self.assertIn("required_must_be_string_array", result.stdout)

    def test_duplicate_json_key_rejected(self):
        result = run('{"tools":[],"tools":[]}')
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, '{"error":"duplicate_json_key"}\n')

    def test_size_cap(self):
        result = run(' ' * (256 * 1024 + 1))
        self.assertEqual(result.stdout, '{"error":"input_too_large"}\n')

    def test_boolean_schema_and_referenced_required_name_are_not_errors(self):
        result = run('{"tools":[{"name":"x","description":"ok","inputSchema":{"type":"object","required":["external"],"properties":{"flag":false},"$defs":{"anything":true}}}]}')
        self.assertEqual(result.returncode, 0)
        self.assertIn("required_not_listed_locally", result.stdout)
        self.assertNotIn('"severity":"error"', result.stdout)


if __name__ == "__main__":
    unittest.main()
