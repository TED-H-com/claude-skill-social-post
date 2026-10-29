"""E2E tests verifying platform-specific character count enforcement,
hashtag sanitization, and calendar formatting.

As per the requirements, this file provides TDD test cases that interact
with the actual application entry point (`social_validation.py`). Because
the product code does not currently implement these validations, these tests
are expected to fail and will serve as the spec for future implementation.
"""

from __future__ import annotations

import unittest
from social_validation import _validate_post

class TestSocialFormattingLimits(unittest.TestCase):

    @unittest.expectedFailure
    def test_x_character_limit_enforcement(self):
        """Verify that _validate_post enforces the 280 character limit for X (Twitter)
           and counts URLs as 23 characters."""
        post_ids = set()
        errors = []
        warnings = []

        # This post exceeds 280 characters and should produce an error
        caption_over_limit = "a" * 281
        post = {"post_id": "p1", "published_at": "2026-08-13T10:00:00+08:00", "platforms": ["x"], "caption": caption_over_limit}
        _validate_post(post, "test", post_ids, errors, warnings)

        # We expect the validation function to add an error regarding the character limit
        self.assertTrue(
            any("character limit" in err.lower() or "length" in err.lower() or "characters" in err.lower() for err in errors),
            "Expected an error for exceeding X character limit."
        )

        # Verify URL counting (URLs count as 23 characters)
        errors.clear()
        # 260 chars + 1 space + 23 URL chars = 284 chars
        url_post = {"post_id": "p2", "published_at": "2026-08-13T10:00:00+08:00", "platforms": ["x"], "caption": ("a" * 260) + " https://example.com/very/long/path"}
        _validate_post(url_post, "test", post_ids, errors, warnings)
        self.assertTrue(
            any("character limit" in err.lower() or "length" in err.lower() or "characters" in err.lower() for err in errors),
            "Expected an error for exceeding X character limit with URLs."
        )

    @unittest.expectedFailure
    def test_x_hashtag_sanitization(self):
        """Verify that _validate_post enforces the 1-2 hashtag limit for X."""
        post_ids = set()
        errors = []
        warnings = []

        # This post has 3 hashtags, exceeding the recommended limit of 1-2
        caption_many_tags = "Post #one #two #three"
        post = {"post_id": "p2", "published_at": "2026-08-13T10:00:00+08:00", "platforms": ["x"], "caption": caption_many_tags}
        _validate_post(post, "test", post_ids, errors, warnings)

        # We expect the validation function to add an error regarding the hashtag limit
        self.assertTrue(
            any("hashtag" in err.lower() for err in errors),
            "Expected an error for exceeding X hashtag limit."
        )

    @unittest.expectedFailure
    def test_calendar_formatting_validation(self):
        """Verify calendar formatting constraints.
        While _validate_post currently does not handle calendar specific structures,
        this test provides a mock calendar payload expecting validation logic to eventually
        enforce required columns: ['日', '公式', '平台', '主目標', '題材提示']."""
        post_ids = set()
        errors = []
        warnings = []

        # A payload containing a malformed calendar Markdown string in caption
        malformed_calendar_caption = (
            "| Day | Content | Platform | Goal | Prompt |\n"
            "| 1 | Test | FB | Brand | Photo |"
        )
        post = {"post_id": "p3", "published_at": "2026-08-13T10:00:00+08:00", "platforms": ["x"], "caption": malformed_calendar_caption}
        _validate_post(post, "test", post_ids, errors, warnings)

        self.assertTrue(
            any("calendar" in err.lower() or "format" in err.lower() or "columns" in err.lower() for err in errors),
            "Expected an error regarding calendar format."
        )

if __name__ == '__main__':
    unittest.main()
