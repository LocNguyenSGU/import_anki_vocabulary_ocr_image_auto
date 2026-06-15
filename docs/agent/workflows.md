# Agent Workflows

## Standard Reading Workflow

Before changing code or lesson data:

1. Read `docs/agent/overview.md`
2. Read `docs/agent/data-contracts.md`
3. Read `docs/agent/pitfalls.md`
4. Only then inspect generated files or Anki state

This reduces the chance of confusing history state with Anki state.

## Add a New Lesson

Use this workflow when the user wants a new vocabulary lesson.

1. Create a new JSON file in `input/`.
2. Use a numeric lesson number.
3. Keep the filename descriptive, for example `input/lesson-04-number-20260615-vocabulary.json`.
4. Keep each item to the accepted fields: `kana`, `kanji`, `vietnamese`, optional `romaji`.
5. Validate JSON shape before building.

Recommended quick check:

```bash
rtk python - <<'PY'
import json
from pathlib import Path
path = Path('input/lesson-04-number-20260615-vocabulary.json')
data = json.loads(path.read_text(encoding='utf-8'))
print(data['lesson'], len(data['items']))
PY
```

## Build Lesson Assets

Standard command:

```bash
rtk python -m mamino_anki.cli build --input input/lesson-04-number-20260615-vocabulary.json
```

Expected output shape:

```text
lesson=lesson-04 added=55 skipped_existing=0 audio_created=55 needs_review=0
```

Use `--fake-audio` when validating workflow behavior without creating real TTS output.

## Import Lesson into Anki

Standard command:

```bash
rtk python -m mamino_anki.cli import-anki --csv csv/lesson-04.csv --audio-dir audio/lesson-04
```

Expected output shape:

```text
rows=55 media_uploaded=55 notes_added=55 notes_skipped_duplicate=0 notes_found=55
```

Before import:

- Anki desktop must be open
- AnkiConnect must answer on `http://localhost:8765`

Quick probe:

```bash
rtk curl -s http://localhost:8765
```

## Re-import After Model Changes

If the note model changes, especially around duplicate behavior:

1. update importer code
2. run tests
3. import again for affected lessons
4. inspect `notes_added`, `notes_skipped_duplicate`, and `notes_found`

Re-import is the safe way to backfill Anki state after note-model migration.

## Diagnose Import Gaps

If `rows` is greater than `notes_added`:

1. compare against `notes_skipped_duplicate`
2. inspect whether the duplicate is expected in Anki
3. do not assume build failed

Useful distinction:

- build duplicate behavior comes from repo history
- import duplicate behavior comes from Anki note model identity

## Update Existing Lesson Content

If you edit `input/lesson-XX-*.json` after a prior build:

1. understand whether items are truly new or only edited
2. rebuild the lesson
3. inspect `history/runs.json`
4. re-import if the Anki note set should change

Do not assume changing the input file automatically rewrites older CSV rows or existing notes in Anki.
