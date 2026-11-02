import unittest
from social_validation import _validate_post

class TestSecurityInputValidation(unittest.TestCase):

    def test_strict_schema_validation(self):
        post_ids = set()
        errors = []
        warnings = []
        post = {
            "post_id": "p1",
            "published_at": "2026-08-13T10:00:00+08:00",
            "platforms": ["facebook"],
            "caption": "test",
            "extra_key": "malicious data"
        }
        _validate_post(post, "test", post_ids, errors, warnings)
        self.assertTrue(
            any("unexpected keys" in err.lower() or "schema" in err.lower() or "extra_key" in err for err in errors),
            f"Expected error for unexpected key 'extra_key'. Got errors: {errors}"
        )

    def test_xss_sanitization(self):
        post_ids = set()
        errors = []
        warnings = []
        post = {
            "post_id": "p2",
            "published_at": "2026-08-13T10:00:00+08:00",
            "platforms": ["facebook"],
            "caption": "Hello <script>alert(1)</script>"
        }
        _validate_post(post, "test", post_ids, errors, warnings)
        self.assertTrue(
            any("script" in err.lower() or "xss" in err.lower() or "malicious" in err.lower() for err in errors),
            f"Expected error for <script> tag in caption. Got errors: {errors}"
        )

    def test_credential_exposure(self):
        post_ids = set()
        errors = []
        warnings = []
        post = {
            "post_id": "p3",
            "published_at": "2026-08-13T10:00:00+08:00",
            "platforms": ["facebook"],
            "caption": "My password is Password123!"
        }
        _validate_post(post, "test", post_ids, errors, warnings)
        self.assertTrue(
            any("credential" in err.lower() or "password" in err.lower() or "sensitive" in err.lower() for err in errors),
            f"Expected error for credential exposure in caption. Got errors: {errors}"
        )

if __name__ == '__main__':
    unittest.main()
