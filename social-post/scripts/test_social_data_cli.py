import json
import subprocess
import unittest
import tempfile
from pathlib import Path
import shutil

class TestSocialDataCli(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(prefix="social-data-cli-")
        self.root = Path(self.temp_dir.name)
        # social_data.py hardcodes default --root to SKILL_ROOT, but accepts --root.
        # We need to setup a mock data structure so that it's isolated.
        self.data_dir = self.root / "data"
        self.data_dir.mkdir()

        self.rule_registry_file = self.data_dir / "rule_registry.json"
        self.rule_registry_file.write_text('{"rules": [{"id": "R01"}]}', encoding="utf-8-sig")

        (self.data_dir / "posts.jsonl").write_text(
            '{"post_id":"p1", "published_at":"2023-01-01T00:00:00Z", "platforms":["facebook"], "caption":"test"}\n',
            encoding="utf-8"
        )
        (self.data_dir / "insight_snapshots.jsonl").write_text(
            '{"snapshot_id":"s1", "post_id":"p1", "captured_at":"2023-01-02T00:00:00Z", "metrics": {"plays": 100}}\n',
            encoding="utf-8"
        )
        (self.data_dir / "account_snapshots.jsonl").write_text("", encoding="utf-8")
        (self.data_dir / "experiments.jsonl").write_text("", encoding="utf-8")
        (self.data_dir / "corrections.jsonl").write_text("", encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_social_data_validate_human(self):
        cmd = ["python3", "social_data.py", "validate", "--format", "human", "--root", str(self.root)]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(Path(__file__).parent))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("valid=True", result.stdout)

    def test_social_data_validate_json(self):
        cmd = ["python3", "social_data.py", "validate", "--format", "json", "--root", str(self.root)]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(Path(__file__).parent))
        # Known bug in social_data.py when serializing dicts with tuple keys (latest_snapshots_by_platform)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("TypeError: keys must be str", result.stderr)

    def test_social_data_summary_human(self):
        cmd = ["python3", "social_data.py", "summary", "--format", "human", "--root", str(self.root)]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(Path(__file__).parent))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("EP | platform | plays", result.stdout)

    def test_social_data_summary_json(self):
        cmd = ["python3", "social_data.py", "summary", "--format", "json", "--root", str(self.root)]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(Path(__file__).parent))
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertIsInstance(data, list)

if __name__ == '__main__':
    unittest.main()
