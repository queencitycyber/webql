# tests/test_vulnerable_examples.py

import unittest
from pathlib import Path
import json
from webql.commands.scan import scan_command
from webql.commands.generate import generate_command
from webql.commands.parse import parse_command
from webql.commands.results import results_command

class TestVulnerableExamples(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project_root = Path(__file__).parent.parent
        cls.vulnerable_examples_dir = cls.project_root / 'vulnerable_examples'
        cls.output_dir = cls.project_root / 'test_output'
        cls.output_dir.mkdir(exist_ok=True)

    def analyze_file(self, file_name):
        file_path = self.vulnerable_examples_dir / file_name
        output_path = self.output_dir / f"{file_name}_output"
        db_path = self.output_dir / f"{file_name}_db"
        sarif_file = self.output_dir / f"{file_name}_results.sarif"

        scan_command([str(file_path)], str(output_path))
        generate_command(str(output_path), str(db_path), overwrite=True)
        parse_command(str(db_path), str(sarif_file))
        return results_command(str(sarif_file))

    def test_test_js(self):
        results = self.analyze_file('test.js')
        self.assertIn('eval', str(results), "Should detect eval usage")
        self.assertIn('XSS', str(results), "Should detect XSS vulnerability")
        self.assertIn('SQL', str(results), "Should detect SQL Injection vulnerability")
        self.assertIn('Math.random', str(results), "Should flag weak random number generation")
        self.assertIn('Path', str(results), "Should detect path traversal vulnerability")

    def test_xss_vulnerable_js(self):
        results = self.analyze_file('xss_vulnerable.js')
        self.assertIn('XSS', str(results), "Should detect XSS vulnerabilities")
        self.assertIn('innerHTML', str(results), "Should flag innerHTML usage")

    def test_sql_injection_js(self):
        results = self.analyze_file('sql_injection.js')
        self.assertIn('SQL', str(results), "Should detect SQL Injection vulnerabilities")
        self.assertIn('WHERE', str(results), "Should flag vulnerable WHERE clause")
        self.assertIn('UPDATE', str(results), "Should detect SQL Injection in UPDATE statement")

if __name__ == '__main__':
    unittest.main()