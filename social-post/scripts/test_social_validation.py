import unittest
from social_validation import (
    validate_posts, validate_snapshots, validate_account_snapshots, validate_experiments,
    materialize_corrections, non_negative_numbers, validate_metric_qualifiers,
    validate_percent_mapping, parse_time, _validate_post, _validate_breakdown,
    _validate_audience, _validate_snapshot, _validate_experiment_row
)

class TestSocialValidation(unittest.TestCase):

    def test_validate_posts(self):
        posts = [
            {"post_id": "p1", "published_at": "2026-08-13T10:00:00+08:00", "platforms": ["facebook"], "caption": "test", "duration_seconds": 30},
            {"post_id": "", "published_at": "invalid", "platforms": [], "caption": 123} # invalid
        ]
        errors = []
        warnings = []
        result = validate_posts(posts, errors, warnings)
        self.assertIn("p1", result)
        self.assertTrue(len(errors) > 0)

    def test_validate_snapshots(self):
        posts_by_id = {
            "p1": {"post_id": "p1", "published_at": "2026-08-13T10:00:00+08:00", "platforms": ["facebook"]}
        }
        snapshots = [
            {"snapshot_id": "s1", "post_id": "p1", "captured_at": "2026-08-13T11:00:00+08:00", "metrics": {"plays": 100}, "platform_scope": "facebook"}
        ]
        errors = []
        warnings = []
        latest_by_post, latest_by_platform = validate_snapshots(snapshots, posts_by_id, errors, warnings)
        self.assertIn("p1", latest_by_post)
        self.assertIn(("p1", "facebook"), latest_by_platform)
        self.assertEqual(len(errors), 0)

    def test_validate_account_snapshots(self):
        snapshots = [
            {"account_snapshot_id": "a1", "platform": "facebook", "captured_at": "2026-08-13T11:00:00+08:00", "window_days": 30, "metrics": {"plays": 100}}
        ]
        errors = []
        warnings = []
        result = validate_account_snapshots(snapshots, errors, warnings)
        self.assertIn("facebook", result)
        self.assertEqual(len(errors), 0)

    def test_materialize_corrections(self):
        posts = [{"post_id": "p1", "platforms": ["facebook"], "caption": "old"}]
        snapshots = [{"snapshot_id": "s1", "post_id": "p1"}]
        account_snapshots = []
        corrections = [
            {
                "correction_id": "c1",
                "target_type": "post",
                "target_id": "p1",
                "recorded_at": "2026-08-13T12:00:00+08:00",
                "changes": {"caption": "new"},
                "reason": "typo"
            }
        ]
        errors = []
        m_posts, m_snapshots, m_account_snapshots = materialize_corrections(posts, snapshots, account_snapshots, corrections, errors)
        self.assertEqual(len(errors), 0)
        self.assertEqual(m_posts[0]["caption"], "new")

    def test_non_negative_numbers(self):
        errors = []
        non_negative_numbers({"a": 1, "b": -1, "c": "invalid", "d": True}, "test", errors)
        self.assertTrue(len(errors) > 0)

    def test_validate_metric_qualifiers(self):
        errors = []
        validate_metric_qualifiers({"metrics": {"plays": 10}, "metric_qualifiers": {"plays": "rounded", "views": "exact"}}, "test", errors)
        self.assertTrue(len(errors) > 0)

    def test_validate_percent_mapping(self):
        errors = []
        validate_percent_mapping({"a": 50, "b": 60, "c": -10, "d": "bad"}, "test", errors)
        self.assertTrue(len(errors) > 0)

        errors.clear()
        validate_percent_mapping({"a": None}, "test", errors)
        self.assertEqual(len(errors), 0)

    def test_parse_time(self):
        with self.assertRaises(ValueError):
            parse_time("2023-01-01T12:00:00") # no offset
        self.assertIsNotNone(parse_time("2023-01-01T12:00:00Z"))
        self.assertIsNotNone(parse_time("2023-01-01T12:00:00+08:00"))

    def test_validate_post_missing(self):
        errors = []
        warnings = []
        _validate_post({}, "test", set(), errors, warnings)
        self.assertTrue(len(errors) > 0)

    def test_validate_breakdown(self):
        errors = []
        warnings = []
        _validate_breakdown({"rates_reported": {"watch_percent": 100}}, {}, "test", errors, warnings)

    def test_validate_audience(self):
        errors = []
        warnings = []
        _validate_audience({"metrics": {"plays": 10, "reached_accounts": 150}}, "test", errors, warnings)

    def test_validate_snapshot_missing(self):
        errors = []
        warnings = []
        _validate_snapshot({}, "test", {"p1": {}}, set(), errors, warnings)
        self.assertTrue(len(errors) > 0)

    def test_validate_experiment_row(self):
        errors = []
        warnings = []
        result = _validate_experiment_row({"experiment_id": "e1", "revision": 1, "post_ids": ["p1"], "evidence": {"status": "validated", "independent_samples": 2}}, "test", {"p1"}, set(), errors, warnings)
        self.assertEqual(result, ("e1", 1))

    def test_validate_experiments_invalid(self):
        experiments = [
            {"experiment_id": "e1", "revision": 1, "post_ids": ["p1"], "rule_ids": ["r1"], "evidence": {"status": "validated", "independent_samples": 2}},
            {"experiment_id": "e1", "revision": 1}, # duplicate
            {"experiment_id": "e2", "revision": 2, "supersedes_revision": 1, "post_ids": ["p2"]} # not contiguous from 1
        ]
        errors = []
        warnings = []
        result = validate_experiments(experiments, {"p1", "p2"}, {"r1"}, errors, warnings)
        self.assertTrue(len(errors) > 0)
        self.assertIn("e1", result)
        self.assertIn("e2", result)

    def test_validate_post_invalid(self):
        post = {
            "post_id": "p1", "published_at": "invalid", "platforms": ["invalid_platform", "facebook", "facebook"],
            "published_at_confidence": "invalid", "episode_number": -1,
            "caption": 123, "content_type": "reel"
        }
        errors = []
        warnings = []
        _validate_post(post, "test", set(), errors, warnings)
        self.assertTrue(len(errors) > 0)
        self.assertTrue(len(warnings) > 0)

    def test_validate_snapshots_invalid(self):
        posts_by_id = {
            "p1": {"post_id": "p1", "published_at": "2026-08-13T10:00:00+08:00", "platforms": ["facebook"]}
        }
        snapshots = [
            {"snapshot_id": "s1", "post_id": "p2", "captured_at": "2026-08-13T11:00:00+08:00"},
            {"snapshot_id": "s2", "post_id": "p1", "captured_at": "invalid"},
            {"snapshot_id": "s3", "post_id": "p1", "captured_at": "2026-08-13T09:00:00+08:00"},
            {"snapshot_id": "s4", "post_id": "p1", "captured_at": "2026-08-13T11:00:00+08:00", "hours_since_publish": -1},
            {"snapshot_id": "s5", "post_id": "p1", "captured_at": "2026-08-13T11:00:00+08:00", "hours_since_publish": 10},
            {"snapshot_id": "s6", "post_id": "p1", "captured_at": "2026-08-13T11:00:00+08:00", "maturity": "invalid"},
            {"snapshot_id": "s7", "post_id": "p1", "captured_at": "2026-08-13T11:00:00+08:00", "captured_at_confidence": "invalid"},
            {"snapshot_id": "s8", "post_id": "p1", "captured_at": "2026-08-13T11:00:00+08:00", "platform_scope": "youtube"},
            {"snapshot_id": "s9", "post_id": "p1", "captured_at": "2026-08-13T11:00:00+08:00", "metrics": "invalid"},
        ]
        errors = []
        warnings = []
        validate_snapshots(snapshots, posts_by_id, errors, warnings)
        self.assertTrue(len(errors) > 0)
        self.assertTrue(len(warnings) > 0)

    def test_validate_breakdown_full(self):
        snapshot = {
            "rates_reported": {"watch_percent": 100, "skip_percent": 20},
            "metrics": {"average_watch_seconds": 30},
            "platform_scope": "youtube"
        }
        post = {"duration_seconds": 30}
        errors = []
        warnings = []
        _validate_breakdown(snapshot, post, "test", errors, warnings)
        self.assertEqual(len(errors), 0)

    def test_validate_experiment_row_invalid(self):
        experiment = {
            "experiment_id": "", "revision": -1, "post_ids": [], "rule_ids": [123], "evidence": "invalid"
        }
        errors = []
        warnings = []
        result = _validate_experiment_row(experiment, "test", set(), set(), errors, warnings)
        self.assertIsNone(result)
        self.assertTrue(len(errors) > 0)

        experiment2 = {
            "experiment_id": "e1", "revision": 1, "post_ids": ["p1"], "evidence": {"status": "invalid_status", "independent_samples": -1}, "rule_ids": ["unknown"]
        }
        errors.clear()
        _validate_experiment_row(experiment2, "test", {"p1"}, {"r1"}, errors, warnings)
        self.assertTrue(len(errors) > 0)

        experiment3 = {
            "experiment_id": "e1", "revision": 1, "post_ids": ["p1"], "evidence": {"status": "validated", "independent_samples": 1}
        }
        errors.clear()
        warnings.clear()
        _validate_experiment_row(experiment3, "test", {"p1"}, set(), errors, warnings)
        self.assertTrue(len(warnings) > 0)

    def test_validate_percent_mapping_non_int(self):
        errors = []
        validate_percent_mapping({"a": "not_int"}, "test", errors)
        self.assertTrue(len(errors) > 0)

    def test_validate_breakdown_various(self):
        errors = []
        warnings = []
        _validate_breakdown({"rates_reported": {"watch_percent": 100}, "platform_scope": "youtube"}, {"duration_seconds": 30}, "test", errors, warnings)

        errors.clear()
        warnings.clear()
        _validate_breakdown({
            "metrics": {"plays": 100},
            "platform_breakdown": {"plays": {"facebook": 100}},
            "platform_scope": "combined"
        }, {"duration_seconds": 30, "platforms": ["facebook", "instagram"]}, "test", errors, warnings)

        errors.clear()
        warnings.clear()
        _validate_breakdown({
            "metrics": {"plays": 100},
            "platform_breakdown": {"plays": {"facebook": 110}},
            "platform_scope": "combined"
        }, {"duration_seconds": 30, "platforms": ["facebook", "instagram"]}, "test", errors, warnings)
        self.assertTrue(any("exceeds total" in e for e in errors))

        errors.clear()
        warnings.clear()
        _validate_breakdown({
            "metrics": {"plays": 100},
            "platform_breakdown": {"plays": {"facebook": -1}},
            "platform_scope": "combined"
        }, {"duration_seconds": 30, "platforms": ["facebook"]}, "test", errors, warnings)
        self.assertTrue(any("non-negative numbers" in e for e in errors))

        errors.clear()
        warnings.clear()
        _validate_breakdown({
            "metrics": {"plays": 100},
            "platform_breakdown": {"plays": {"facebook": 50}},
            "platform_scope": "combined"
        }, {"duration_seconds": 30, "platforms": ["facebook"]}, "test", errors, warnings)
        self.assertTrue(any("!= total" in e for e in errors))

    def test_validate_snapshots_duplicate(self):
        errors = []
        warnings = []
        posts_by_id = {"p1": {"post_id": "p1", "published_at": "2026-08-13T10:00:00+08:00", "platforms": ["facebook"]}}
        snapshots = [
            {"snapshot_id": "s1", "post_id": "p1", "captured_at": "2026-08-13T11:00:00+08:00"},
            {"snapshot_id": "s1", "post_id": "p1", "captured_at": "2026-08-13T12:00:00+08:00"}
        ]
        validate_snapshots(snapshots, posts_by_id, errors, warnings)
        self.assertTrue(any("duplicate snapshot_id" in e for e in errors))

    def test_validate_snapshots_update(self):
        errors = []
        warnings = []
        posts_by_id = {"p1": {"post_id": "p1", "published_at": "2026-08-13T10:00:00+08:00", "platforms": ["facebook"]}}
        snapshots = [
            {"snapshot_id": "s1", "post_id": "p1", "captured_at": "2026-08-13T11:00:00+08:00"},
            {"snapshot_id": "s2", "post_id": "p1", "captured_at": "2026-08-13T12:00:00+08:00"}
        ]
        latest_by_post, latest_by_platform = validate_snapshots(snapshots, posts_by_id, errors, warnings)
        self.assertEqual(latest_by_post["p1"]["snapshot_id"], "s2")

    def test_validate_account_snapshots_update(self):
        errors = []
        warnings = []
        snapshots = [
            {"account_snapshot_id": "a1", "platform": "facebook", "captured_at": "2026-08-13T11:00:00+08:00", "window_days": 30, "metrics": {}},
            {"account_snapshot_id": "a2", "platform": "facebook", "captured_at": "2026-08-13T12:00:00+08:00", "window_days": 30, "metrics": {}}
        ]
        latest = validate_account_snapshots(snapshots, errors, warnings)
        self.assertEqual(latest["facebook"]["account_snapshot_id"], "a2")

    def test_validate_experiments_update(self):
        errors = []
        warnings = []
        experiments = [
            {"experiment_id": "e1", "revision": 1, "post_ids": ["p1"], "evidence": {"status": "validated", "independent_samples": 2}},
            {"experiment_id": "e1", "revision": 2, "supersedes_revision": 1, "post_ids": ["p1"], "evidence": {"status": "validated", "independent_samples": 2}}
        ]
        latest = validate_experiments(experiments, {"p1"}, set(), errors, warnings)
        self.assertEqual(latest["e1"]["revision"], 2)

    def test_materialize_corrections_missing(self):
        posts = []
        snapshots = []
        account_snapshots = []
        corrections = [{}]
        errors = []
        materialize_corrections(posts, snapshots, account_snapshots, corrections, errors)
        self.assertTrue(len(errors) > 0)

    def test_validate_post_episode_not_int(self):
        errors = []
        _validate_post({"post_id": "p1", "published_at": "2026-08-13T10:00:00+08:00", "platforms": ["facebook"], "caption": "", "episode_number": "not_int"}, "test", set(), errors, [])
        self.assertTrue(len(errors) > 0)

    def test_validate_experiment_row_evidence_not_dict(self):
        errors = []
        _validate_experiment_row({"experiment_id": "e1", "revision": 1, "post_ids": ["p1"], "evidence": "not_dict"}, "test", {"p1"}, set(), errors, [])
        self.assertTrue(len(errors) > 0)

    def test_materialize_corrections_account_snapshot_invalid_key(self):
        posts = []
        snapshots = []
        account_snapshots = [{"account_snapshot_id": "a1"}]
        corrections = [
            {"correction_id": "c1", "target_type": "account_snapshot", "target_id": "a1", "recorded_at": "2026-08-13T12:00:00+08:00", "changes": {"account_snapshot_id": "a2"}, "reason": "test"}
        ]
        errors = []
        materialize_corrections(posts, snapshots, account_snapshots, corrections, errors)
        self.assertTrue(len(errors) > 0)

    def test_validate_post_duration_boolean(self):
        errors = []
        _validate_post({"post_id": "p1", "published_at": "2026-08-13T10:00:00+08:00", "platforms": ["facebook"], "caption": "", "duration_seconds": True}, "test", set(), errors, [])
        self.assertTrue(len(errors) > 0)

    def test_validate_experiment_row_empty_post_ids(self):
        errors = []
        _validate_experiment_row({"experiment_id": "e1", "revision": 1, "post_ids": "not_list"}, "test", {"p1"}, set(), errors, [])
        self.assertTrue(len(errors) > 0)

    def test_validate_audience_rates_reported(self):
        errors = []
        warnings = []
        _validate_audience({"rates_reported": "not_dict"}, "test", errors, warnings)

    def test_validate_breakdown_not_dict_rates(self):
        errors = []
        warnings = []
        _validate_breakdown({"rates_reported": "not_dict", "platform_scope": "youtube"}, {"duration_seconds": 30}, "test", errors, warnings)

    def test_materialize_corrections_duplicate2(self):
        posts = [{"post_id": "p1", "platforms": ["facebook"], "caption": "old"}]
        snapshots = []
        account_snapshots = []
        corrections = [
            {"correction_id": "c1", "target_type": "post", "target_id": "p1", "recorded_at": "2026-08-13T12:00:00+08:00", "changes": {"caption": "new"}, "reason": "typo"},
            {"correction_id": "c1", "target_type": "snapshot", "target_id": "s1", "recorded_at": "2026-08-13T12:00:00+08:00", "changes": {}, "reason": "typo"}
        ]
        errors = []
        materialize_corrections(posts, snapshots, account_snapshots, corrections, errors)
        self.assertTrue(any("duplicate correction_id" in e for e in errors))

    def test_validate_audience_not_dict_rates_reported(self):
        errors = []
        warnings = []
        _validate_audience({"rates_reported": "not_dict"}, "test", errors, warnings)

    def test_validate_breakdown_not_dict_rates_reported(self):
        errors = []
        warnings = []
        _validate_breakdown({"rates_reported": "not_dict"}, {}, "test", errors, warnings)

    def test_validate_experiments_identity_none(self):
        experiments = [
            {"experiment_id": "", "revision": 1, "post_ids": ["p1"]}
        ]
        errors = []
        warnings = []
        validate_experiments(experiments, {"p1"}, set(), errors, warnings)
        self.assertTrue(len(errors) > 0)

    def test_validate_experiment_row_rule_ids(self):
        errors = []
        warnings = []
        _validate_experiment_row({"experiment_id": "e1", "revision": 1, "post_ids": ["p1"], "rule_ids": ["r1"]}, "test", {"p1"}, {"r2"}, errors, warnings)
        self.assertTrue(any("unknown rule_id" in e for e in errors))

    def test_validate_post_duration_seconds_invalid(self):
        errors = []
        _validate_post({"post_id": "p1", "published_at": "2026-08-13T10:00:00+08:00", "platforms": ["facebook"], "caption": "", "duration_seconds": "invalid"}, "test", set(), errors, [])
        self.assertTrue(any("must be positive" in e for e in errors))

    def test_validate_metric_qualifiers_missing_metric(self):
        errors = []
        validate_metric_qualifiers({"metrics": {"plays": 1}, "metric_qualifiers": {"missing_metric": "exact"}}, "test", errors)
        self.assertTrue(any("missing metric" in e for e in errors))

    def test_validate_metric_qualifiers_invalid_qualifier(self):
        errors = []
        validate_metric_qualifiers({"metrics": {"plays": 1}, "metric_qualifiers": {"plays": "invalid"}}, "test", errors)
        self.assertTrue(any("must be one of" in e for e in errors))

    def test_materialize_corrections_unknown_target_type(self):
        errors = []
        materialize_corrections([], [], [], [{"correction_id": "c1", "target_type": "unknown", "target_id": "t1", "recorded_at": "2026-08-13T12:00:00+08:00", "changes": {}, "reason": "reason"}], errors)
        self.assertTrue(len(errors) > 0)

    def test_account_snapshot_captured_at_valid(self):
        errors = []
        warnings = []
        snapshots = [
            {"account_snapshot_id": "a1", "platform": "facebook", "captured_at": "2026-08-13T11:00:00+08:00", "window_days": 30, "metrics": {"plays": 100}},
        ]
        validate_account_snapshots(snapshots, errors, warnings)
        self.assertEqual(len(errors), 0)

    def test_account_snapshot_captured_at_error_and_missing_window(self):
        errors = []
        warnings = []
        snapshots = [
            {"account_snapshot_id": "a1", "platform": "facebook", "captured_at": "invalid", "window_days": -1, "metrics": "invalid", "captured_at_confidence": "invalid"},
            {"account_snapshot_id": "a1", "platform": "facebook", "captured_at": "2026-08-13T11:00:00+08:00", "window_days": "str", "metrics": {}}
        ]
        validate_account_snapshots(snapshots, errors, warnings)
        self.assertTrue(any("invalid captured_at" in e for e in errors))
        self.assertTrue(any("window_days must be a positive integer" in e for e in errors))
        self.assertTrue(any("metrics must be an object" in e for e in errors))

    def test_validate_experiment_row_edge_cases(self):
        errors = []
        warnings = []
        _validate_experiment_row({"experiment_id": "e1", "revision": 1, "post_ids": ["p1"], "rule_ids": "not_list"}, "test", {"p1"}, set(), errors, warnings)
        self.assertTrue(any("rule_ids must be a list of strings" in e for e in errors))

        errors.clear()
        _validate_experiment_row({"experiment_id": "e1", "revision": 1, "post_ids": ["p1"], "rule_ids": ["r1"]}, "test", {"p1"}, {"r2"}, errors, warnings)
        self.assertTrue(any("unknown rule_id" in e for e in errors))

        errors.clear()
        _validate_experiment_row({"experiment_id": "e1", "revision": 1, "post_ids": ["p1"], "evidence": {"status": "invalid"}}, "test", {"p1"}, set(), errors, warnings)
        self.assertTrue(any("invalid evidence status" in e for e in errors))

        errors.clear()
        _validate_experiment_row({"experiment_id": "e1", "revision": 1, "post_ids": ["p1"], "evidence": {"independent_samples": "str"}}, "test", {"p1"}, set(), errors, warnings)
        self.assertTrue(any("independent_samples must be a boolean or non-negative integer" in e for e in errors))

    def test_materialize_corrections_duplicate_revisions(self):
        errors = []
        corrections = [
            {"correction_id": "c1", "target_type": "post", "target_id": "p1", "recorded_at": "2026-08-13T12:00:00+08:00", "changes": {}, "reason": "reason"},
            {"correction_id": "c1", "target_type": "post", "target_id": "p1", "recorded_at": "2026-08-13T12:00:00+08:00", "changes": {}, "reason": "reason"}
        ]
        materialize_corrections([], [], [], corrections, errors)
        self.assertTrue(any("duplicate correction_id" in e for e in errors))

    def test_account_snapshots_valid(self):
        errors = []
        warnings = []
        snapshots = [
            {"account_snapshot_id": "a1", "platform": "facebook", "captured_at": "2026-08-13T11:00:00+08:00", "window_days": 30, "metrics": {"plays": 100}},
            {"account_snapshot_id": "a2", "platform": "facebook", "captured_at": "2026-08-14T11:00:00+08:00", "window_days": 30, "metrics": {"plays": 200}}
        ]
        res = validate_account_snapshots(snapshots, errors, warnings)
        self.assertEqual(res["facebook"]["account_snapshot_id"], "a2")

    def test_validate_audience_full_with_demographics(self):
        errors = []
        warnings = []
        snapshot = {
            "metrics": {},
            "audience": {
                "followers_percent": 50,
                "non_followers_percent": 50,
                "gender_percent": {"male": 60, "female": 40},
                "age_percent": {"18-24": 50, "25-34": 50},
                "top_countries_percent": {"us": 100}
            }
        }
        _validate_audience(snapshot, "test", errors, warnings)
        self.assertEqual(len(errors), 0)

    def test_validate_audience_demographics_invalid(self):
        errors = []
        warnings = []
        snapshot = {
            "metrics": {},
            "audience": "not_an_object"
        }
        _validate_audience(snapshot, "test", errors, warnings)
        self.assertTrue(any("audience must be an object" in e for e in errors))

        errors.clear()
        warnings.clear()
        snapshot = {
            "metrics": {},
            "audience": {
                "followers_percent": 50,
                "gender_percent": {"male": 10, "female": 10},
                "age_percent": {"18-24": 10}
            }
        }
        _validate_audience(snapshot, "test", errors, warnings)
        self.assertTrue(any("gender_percent does not sum near 100%" in w for w in warnings))
        self.assertTrue(any("age_percent does not sum near 100%" in w for w in warnings))

    def test_validate_post_duplicate_id(self):
        post1 = {"post_id": "p1", "published_at": "2026-08-13T10:00:00+08:00", "platforms": ["facebook"], "caption": "test", "duration_seconds": 30}
        post2 = {"post_id": "p1", "published_at": "2026-08-13T10:00:00+08:00", "platforms": ["facebook"], "caption": "test2", "duration_seconds": 30}
        errors = []
        warnings = []
        result = validate_posts([post1, post2], errors, warnings)
        self.assertTrue(any("duplicate post_id p1" in e for e in errors))

    def test_materialize_corrections_empty_changes(self):
        posts = [{"post_id": "p1", "platforms": ["facebook"], "caption": "old"}]
        snapshots = []
        account_snapshots = []
        corrections = [
            {"correction_id": "c1", "target_type": "post", "target_id": "p1", "recorded_at": "2026-08-13T12:00:00+08:00", "changes": {}, "reason": "reason"}
        ]
        errors = []
        materialize_corrections(posts, snapshots, account_snapshots, corrections, errors)
        self.assertTrue(any("changes must be a non-empty object" in e for e in errors))

if __name__ == '__main__':
    unittest.main()
