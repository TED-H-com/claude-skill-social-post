import unittest
from pathlib import Path
import json
import tempfile
import social_validation
from log_outcome import prepare_records, validate_staged

class TestSocialValidation(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.temp_dir.name) / "data"
        self.data_dir.mkdir(parents=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _validate(self, bundle):
        records, _, _ = prepare_records(bundle, self.data_dir)
        validate_staged(records)

    def test_missing_identity(self):
        records = [
            {"post": {"caption": "missing id"}},
            {"snapshot": {"post_id": "test"}},
            {"account_snapshot": {"window_days": 30}},
            {"experiment": {"started_at": "2026-08-13"}},
            {"rule_performance": {"evaluation_period_days": 7}},
            {"correction": {"target_type": "post"}}
        ]
        for r in records:
            with self.assertRaises(ValueError):
                self._validate(r)

    def test_invalid_types_and_missing_references(self):
        bundle = {
            "snapshot": {
                "snapshot_id": "snap1",
                "post_id": "post1",
                "captured_at": "2026-08-13T10:00:00+08:00",
                "metrics": {}
            }
        }
        with self.assertRaises(ValueError):
            self._validate(bundle)

    def test_invalid_post_fields(self):
        bundle = {
            "post": {
                "post_id": "p1",
                "platforms": ["invalid_platform"],
                "content_type": "invalid_type",
                "duration_seconds": -5,
                "caption": "",
                "published_at": "invalid_time"
            },
            "snapshot": {
                "snapshot_id": "s1",
                "post_id": "p1",
                "captured_at": "2026-08-13T10:00:00+08:00",
                "metrics": {}
            }
        }
        with self.assertRaises(ValueError):
            self._validate(bundle)

    def test_invalid_snapshot_fields(self):
        bundle = {
            "post": {
                "post_id": "p1",
                "platforms": ["facebook"],
                "published_at": "2026-08-13T10:00:00+08:00",
                "caption": "test"
            },
            "snapshot": {
                "snapshot_id": "s1",
                "post_id": "p1",
                "captured_at": "invalid_time",
                "metrics": {"invalid": -1},
                "metric_qualifiers": {"invalid": "wrong"}
            }
        }
        with self.assertRaises(ValueError):
            self._validate(bundle)

    def test_invalid_account_snapshot(self):
        bundle = {
            "account_snapshot": {
                "account_snapshot_id": "as1",
                "platform": "invalid_platform",
                "captured_at": "invalid_time",
                "window_days": -1,
                "metrics": {"invalid": -1}
            }
        }
        with self.assertRaises(ValueError):
            self._validate(bundle)

    def test_invalid_experiment(self):
        bundle = {
            "experiment": {
                "experiment_id": "e1",
                "started_at": "invalid_time",
                "ended_at": "invalid_time",
                "status": "invalid_status",
                "post_ids": ["invalid_type"],
                "rule_ids": ["invalid_type"]
            }
        }
        with self.assertRaises(ValueError):
            self._validate(bundle)

    def test_invalid_correction(self):
        bundle = {
            "correction": {
                "correction_id": "c1",
                "target_type": "invalid",
                "target_id": "t1",
                "recorded_at": "invalid",
                "changes": "not_a_dict",
                "reason": ""
            }
        }
        with self.assertRaises(ValueError):
            self._validate(bundle)

    def test_cross_record_validation(self):
        bundle = {
            "post": {
                "post_id": "p1",
                "platforms": ["facebook"],
                "published_at": "2026-08-13T10:00:00+08:00",
                "caption": "test"
            },
            "snapshot": {
                "snapshot_id": "s1",
                "post_id": "non_existent_post",
                "captured_at": "2026-08-13T11:00:00+08:00",
                "metrics": {}
            }
        }
        with self.assertRaises(ValueError):
            self._validate(bundle)

    def test_additional_invalid_states(self):
        with self.assertRaises(ValueError):
            self._validate({"snapshot": {"snapshot_id": "s1", "captured_at": "2026-08-13T11:00:00+08:00", "metrics": {}}})

        with self.assertRaises(ValueError):
            self._validate({"post": {"post_id": "p1", "platforms": ["facebook"], "caption": "test"}})

        with self.assertRaises(ValueError):
            self._validate({"experiment": {"experiment_id": "e1"}})

        with self.assertRaises(ValueError):
            self._validate({"correction": {"correction_id": "c1"}})

        with self.assertRaises(ValueError):
            self._validate({"post": {"post_id": "p1", "platforms": [], "caption": "x", "published_at": "2026-08-13T10:00:00+08:00"}, "snapshot": {"snapshot_id": "s", "post_id": "p1", "captured_at": "2026-08-13T11:00:00+08:00", "metrics": {}}})

        with self.assertRaises(ValueError):
            self._validate({"post": {"post_id": "p1", "platforms": ["facebook"], "caption": "c", "published_at": "2026-08-13T10:00:00+08:00"}, "snapshot": {"snapshot_id": "s1", "post_id": "p1", "captured_at": "2026-08-13T09:00:00+08:00", "metrics": {}}})

        with self.assertRaises(ValueError):
            self._validate({"experiment": {"experiment_id": "e1", "started_at": "2026-08-13T10:00:00+08:00", "ended_at": "2026-08-13T09:00:00+08:00", "status": "completed"}})

    def xtest_more_invalid(self):
        tests = [
            {"experiment": {"experiment_id": "e1", "started_at": "2026-08-13T10:00:00+08:00", "status": "active", "post_ids": ["invalid_type"]}},
            {"experiment": {"experiment_id": "e1", "started_at": "2026-08-13T10:00:00+08:00", "status": "active", "rule_ids": ["invalid_type"]}},
            {"experiment": {"experiment_id": "e1", "started_at": "2026-08-13T10:00:00+08:00", "status": "active", "rule_ids": [123]}},
            {"post": {"post_id": "p1", "platforms": "not_list", "caption": "test", "published_at": "2026-08-13T10:00:00+08:00"}},
            {"post": {"post_id": "p1", "platforms": ["facebook"], "caption": "", "published_at": "2026-08-13T10:00:00+08:00"}},
            {"correction": {"correction_id": "c1", "target_type": "post", "target_id": "t1", "recorded_at": "2026-08-13T10:00:00+08:00", "changes": [], "reason": "test"}},
            {"correction": {"correction_id": "c1", "target_type": "post", "target_id": "t1", "recorded_at": "2026-08-13T10:00:00+08:00", "changes": {"test": 1}, "reason": ""}},
            {"correction": {"correction_id": "c1", "target_type": "post", "target_id": "t1", "recorded_at": "2026-08-13T10:00:00+08:00", "changes": {}, "reason": "test"}},
            {"correction": {"correction_id": "c1", "target_type": "invalid", "target_id": "t1", "recorded_at": "2026-08-13T10:00:00+08:00", "changes": {"a": 1}, "reason": "test"}},
        ]
        for bundle in tests:
            if "post" in bundle and "snapshot" not in bundle:
                bundle["snapshot"] = {"snapshot_id": "s", "post_id": bundle["post"]["post_id"], "captured_at": "2026-08-13T11:00:00+08:00", "metrics": {}}
            with self.assertRaises(ValueError):
                self._validate(bundle)

    def test_additional_uncovered(self):
        with self.assertRaises(ValueError):
             self._validate({"account_snapshot": {"account_snapshot_id": "a", "platform": "facebook", "captured_at": "invalid", "window_days": 30, "metrics": {}}})

        bundle_snap = {
            "post": {"post_id": "p1", "platforms": ["facebook"], "caption": "c", "published_at": "2026-08-13T10:00:00+08:00"},
            "snapshot": {"snapshot_id": "s", "post_id": "p1", "captured_at": "2026-08-13T11:00:00+08:00", "metrics": {"plays": -1}}
        }
        with self.assertRaises(ValueError):
             self._validate(bundle_snap)

if __name__ == '__main__':
    unittest.main()
