import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

MODULE = Path(__file__).resolve().parents[1] / "tools" / "validate.py"
spec = importlib.util.spec_from_file_location("devkit_validate", MODULE)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class PackageChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        skill = self.root / "skills" / "hello"
        skill.mkdir(parents=True)
        (self.root / "plugin.json").write_text(json.dumps({"$schema": validator.SCHEMA_URL, "name": "example"}))
        (skill / "SKILL.md").write_text("---\nname: hello\ndescription: Explain a greeting.\n---\n# Hello\n")
        self.schema = {"type": "object", "required": ["name"], "properties": {"name": {"type": "string"}}}

    def test_complete_local_reference_is_valid(self):
        (self.root / "guide.md").write_text("# Guide\n")
        (self.root / "README.md").write_text("[Guide](guide.md)\n[Section](guide.md#guide)\n")
        errors, count = validator.validate(self.root, self.schema)
        self.assertEqual((errors, count), ([], 1))

    def test_broken_reference_reports_source_and_target(self):
        (self.root / "README.md").write_text("[Guide](missing.md)\n")
        errors, _ = validator.validate(self.root, self.schema)
        self.assertTrue(any("README.md" in e and "missing.md" in e for e in errors), errors)

    def test_link_cannot_escape_package_even_if_target_exists(self):
        outside = self.root.parent / (self.root.name + "-outside.md")
        outside.write_text("# External")
        self.addCleanup(outside.unlink)
        (self.root / "README.md").write_text(f"[Guide](../{outside.name})\n")
        errors, _ = validator.validate(self.root, self.schema)
        self.assertTrue(any("outside package" in e for e in errors), errors)

    def test_symlink_cannot_escape_package(self):
        with tempfile.TemporaryDirectory() as outside:
            (self.root / "linked").symlink_to(outside, target_is_directory=True)
            errors, _ = validator.validate(self.root, self.schema)
            self.assertTrue(any("outside package" in e for e in errors), errors)

    def test_skill_name_must_match_directory(self):
        p = self.root / "skills/hello/SKILL.md"
        p.write_text(p.read_text().replace("name: hello", "name: renamed"))
        errors, _ = validator.validate(self.root, self.schema)
        self.assertTrue(any("directory" in e for e in errors), errors)

    def test_missing_entrypoint_is_visible(self):
        (self.root / "skills/hello/SKILL.md").unlink()
        errors, _ = validator.validate(self.root, self.schema)
        self.assertTrue(any("SKILL.md" in e for e in errors), errors)

    def test_examples_are_not_interpreted_as_links(self):
        (self.root / "README.md").write_text("```md\n[Example](not-a-file.md)\n```\n")
        self.assertEqual(validator.validate(self.root, self.schema)[0], [])

    def test_schema_validation_is_not_bypassed(self):
        (self.root / "plugin.json").write_text('{"name": 42}')
        errors, _ = validator.validate(self.root, self.schema)
        self.assertTrue(any("plugin.json" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
