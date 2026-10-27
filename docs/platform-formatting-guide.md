# Platform Formatting Guide

This document outlines the supported platforms, character length limits, hashtag rules, and media constraints based on the platform references.

## Supported Platforms

- Facebook
- Instagram
- Threads
- X (Twitter)
- YouTube

## Character Length Limits

- **X (Twitter):** Free accounts 280 characters, Premium accounts 25,000 characters. Chinese characters count as 1 character. URLs count as 23 characters. Exceeding 280 characters should be split into threads.

*Other platforms do not explicitly define a hard character limit in the references, but best practices dictate concise and native prose.*

## Hashtag Rules

- **Instagram:** Use only relevant hashtags; their count is an experiment, not a timeless rule.
- **X (Twitter):** 1-2 hashtags are enough (hashtag diffusion on X has weakened). Place them at the end of the sentence.

## Media Asset Schemas and Constraints

- **Facebook:**
  - The official server-side Reel collection documents 9:16 aspect ratio, at least 540x960 resolution, 23 fps, and 4-60 second duration.
  - *Note:* Treat long-form API support as unverified and run one isolated canary instead of assuming no length restrictions.
- **Instagram:**
  - For server-side Reel publishing, the documented constraints are MP4/MOV, H.264 or HEVC, AAC 48 kHz at no more than 128 kbps, 23-60 fps, 3 seconds to 15 minutes, and no more than 1 GB.
  - The opening visual must communicate the object, conflict, or payoff without relying on the caption.
- **YouTube:**
  - Make the subject and payoff legible in the first frame.
