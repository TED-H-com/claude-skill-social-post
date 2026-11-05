#!/usr/bin/env python3
"""E2E tests for the log_outcome.py CLI."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
import uuid
from pathlib import Path

class TestLogOutcomeCli(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(prefix="social-post-cli-test-")
        self.root = Path(self.temp_dir.name)
        self.bundle_file = self.root / "valid_bundle.json"

        # We need to generate a unique snapshot id and post id so it doesn't conflict
        unique_id = uuid.uuid4().hex

        bundle_data = {
            "post": {
                "post_id": f"test-post-{unique_id}",
                "published_at": "2026-08-13T10:00:00+08:00",
                "platforms": ["facebook"],
                "caption": "test caption"
            },
            "snapshot": {
                "snapshot_id": f"test-snapshot-{unique_id}",
                "post_id": f"test-post-{unique_id}",
                "captured_at": "2026-08-13T11:00:00+08:00",
                "metrics": {}
            }
        }
        self.bundle_file.write_text(json.dumps(bundle_data), encoding="utf-8-sig")

        self.invalid_bundle_file = self.root / "invalid_bundle.json"
        self.invalid_bundle_file.write_text("{ invalid json ", encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_log_outcome_dry_run(self):
        """Test log_outcome.py dry run behavior."""
        cmd = ["python3", "log_outcome.py", str(self.bundle_file)]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(Path(__file__).parent))

        self.assertEqual(result.returncode, 0, f"Expected success but got {result.returncode}. Stderr: {result.stderr}")
        self.assertIn("DRY_RUN valid bundle; add --write to commit", result.stdout)

    def test_log_outcome_write(self):
        """Test log_outcome.py write behavior."""
        cmd = ["python3", "log_outcome.py", str(self.bundle_file), "--write"]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(Path(__file__).parent))

        self.assertEqual(result.returncode, 0, f"Expected success but got {result.returncode}. Stderr: {result.stderr}")
        self.assertIn("WRITE_OK revision=", result.stdout)

    def test_log_outcome_invalid_json(self):
        """Test log_outcome.py error handling with invalid JSON."""
        cmd = ["python3", "log_outcome.py", str(self.invalid_bundle_file)]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(Path(__file__).parent))

        self.assertEqual(result.returncode, 2, f"Expected error code 2 but got {result.returncode}")
        self.assertIn("log outcome error:", result.stderr)

if __name__ == '__main__':
    unittest.main()
