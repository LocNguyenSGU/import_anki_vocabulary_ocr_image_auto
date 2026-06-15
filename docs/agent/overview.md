# Agent Overview

## Purpose

This repository builds Japanese vocabulary lessons into Anki-ready assets:

- input lesson JSON in `input/`
- generated CSV in `csv/`
- generated MP3 audio in `audio/`
- processing history in `history/runs.json`
- direct import into Anki via AnkiConnect

The primary workflow is not OCR automation inside the repo. In practice, a human or AI agent prepares lesson JSON first, then the CLI builds artifacts and imports them.

## Read This First

When working in this repo, read in this order:

1. `docs/agent/overview.md`
2. `docs/agent/architecture.md`
3. `docs/agent/data-contracts.md`
4. `docs/agent/workflows.md`
5. `docs/agent/pitfalls.md`

Only after that should you infer behavior from source files or old generated artifacts.

## Fast Orientation

If you only need the minimum mental model:

- Lesson input is a JSON file with numeric `lesson` and `items`.
- `mamino-anki build --input ...` generates or extends CSV, audio, and history.
- `mamino-anki import-anki --csv ... --audio-dir ...` uploads media and adds notes to Anki.
- Lesson numbering is numeric and normalized to `lesson-XX`.
- Duplicate handling in Anki depends on the technical `EntryKey` field, not only `Kana`.

## Scope Boundaries

This repo currently focuses on:

- lesson data preparation
- deterministic CSV generation
- deterministic audio naming per lesson
- idempotent rebuilds using history
- Anki import through AnkiConnect

It does not currently include:

- a local OCR UI
- sentence/example generation
- grammar explanations
- a generalized spaced-repetition authoring system beyond this note model

## Source of Truth

Use these files as the stable source of truth:

- lesson identity and keys: `mamino_anki/models.py`
- build flow and audio numbering: `mamino_anki/processor.py`
- CLI commands: `mamino_anki/cli.py`
- Anki import and duplicate behavior: `mamino_anki/anki_importer.py`
- example workflow and user-facing setup: `README.md`

Generated files in `csv/`, `audio/`, and `history/` describe state, not architecture.
