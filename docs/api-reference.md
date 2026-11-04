# CLI API Reference

This document provides a reference for the core Python CLI tools available in the `social-post` skill. All scripts should be executed from the `social-post/` directory.

## `social_data.py`

Manages social media metrics and rule validation.

**Usage:** `python scripts/social_data.py [-h] [--root ROOT] [--series SERIES] [--format {human,json}] {validate,summary}`

**Commands:**
*   `validate`: Validates the integrity of the data store.
*   `summary`: Generates a summary of performance metrics, optionally filtered by a specific series.

**Options:**
*   `--root ROOT`: Path to the skill data root (default is the skill directory).
*   `--series SERIES`: Filter the summary by a specific series ID.
*   `--format {human,json}`: Output format for the summary (default is `human`).

## `log_outcome.py`

Records social media performance outcomes from a JSON bundle.

**Usage:** `python scripts/log_outcome.py [-h] [--write] bundle`

**Positional arguments:**
*   `bundle`: Path to a JSON object file containing the snapshot, optional post, and optional experiment data.

**Options:**
*   `--write`: Commits the outcome to the data store. If not provided, the script runs in dry-run mode (validates without saving).

## `comment_assistant.py`

Handles the lifecycle of managing, drafting, and approving social media comments. Also includes the bridge to interact with the Chrome actuator.

**Usage:** `python scripts/comment_assistant.py [-h] {browser-scan-request,browser-scan,browser-action,browser-begin,browser-finish,browser-reconcile,validate,queue,ingest,draft,grant-auto,revoke-grant,approve,begin-send,finish-send,reconcile,deferred,skipped,revoked} ...`

**Commands:**
*   `validate`: Verifies the integrity of the comment state ledger.
*   `queue`: Lists pending comments that require action or approval. Use `--mode` to filter.
*   `ingest`: Imports comment events from an external JSON source.
*   `draft`: Drafts a reply to a specific comment.
*   `approve`: Approves an intent to send a reply.
*   `grant-auto`: Grants an authorization to perform automatic bounded actions.
*   `revoke-grant`: Revokes a previously granted auto-action authorization.
*   `begin-send` / `finish-send` / `reconcile`: Legacy test environment ledger mutations for the send lifecycle.
*   `deferred` / `skipped` / `revoked`: Marks a comment's disposition state.
*   `browser-scan-request`: Initiates a scanning request.
*   `browser-scan`: Processes the output of a browser scan.
*   `browser-action`: Prepares an action for the Chrome actuator.
*   `browser-begin`: Begins a browser interaction sequence.
*   `browser-finish`: Concludes a browser interaction sequence.
*   `browser-reconcile`: Reconciles ambiguous states after a browser interaction.

**Common Options:**
*   Most commands support `--root` to specify the ledger directory.
*   Mutating commands require the `--write` flag to apply changes to the ledger; otherwise, they operate in dry-run mode.
*   Many browser and authorization commands require a `--session-id` for traceability.

## `build_rule_registry.py`

Compiles the internal rule registry from Markdown rules into a machine-readable JSON structure.

**Usage:** `python scripts/build_rule_registry.py [-h] [--write]`

**Options:**
*   `--write`: Overwrites the `data/rule_registry.json` file. If omitted, the compilation is verified without saving.
