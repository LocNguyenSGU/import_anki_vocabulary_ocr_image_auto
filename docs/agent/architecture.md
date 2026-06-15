# Agent Architecture

## End-to-End Flow

The core flow is:

`input JSON -> Processor -> CSV/audio/history -> AnkiImporter -> Anki note model/cards`

More concretely:

1. A lesson JSON file is created under `input/`.
2. `mamino-anki build` parses the JSON.
3. `Processor` normalizes items, assigns audio filenames, and checks prior history.
4. CSV rows are appended only for new items.
5. Audio is generated only for missing items.
6. `history/runs.json` is updated so rebuilds are incremental.
7. `mamino-anki import-anki` uploads audio and adds notes into the per-lesson deck in Anki.

## Main Modules

### `mamino_anki/models.py`

Defines stable domain primitives:

- `lesson_key(lesson)` -> `lesson-XX`
- `VocabularyItem`
- `ProcessResult`

If lesson identity rules change, this file is the first place to inspect.

### `mamino_anki/processor.py`

Owns build-time behavior:

- convert raw JSON items into `VocabularyItem`
- reuse audio names from history if an item already exists
- allocate next audio index for new items
- create missing audio
- append missing CSV rows
- record the run into history

This module is the source of truth for idempotent build behavior.

### `mamino_anki/csv_store.py`

Handles CSV writing and append-missing behavior. It should preserve header shape and avoid duplicate rows for the same item set processed through history.

### `mamino_anki/history.py`

Owns `history/runs.json` read/write behavior. It is the source of truth for whether the build step considers an item already processed.

### `mamino_anki/audio.py`

Owns audio generation. Production uses `edge-tts`; tests often use fake audio providers.

### `mamino_anki/anki_importer.py`

Owns Anki-facing behavior:

- ensure deck exists
- ensure note type exists or migrate it
- upload media
- map CSV rows into note fields
- detect duplicates through AnkiConnect

This file now includes the technical `EntryKey` migration and note-field generation used to avoid false duplicates for same-kana items.

### `mamino_anki/cli.py`

Defines the two operator-facing commands:

- `build`
- `import-anki`

If a command-line workflow seems wrong, inspect this file after checking docs.

## Generated Asset Layout

- `input/lesson-*.json`: human/agent-authored lesson source
- `csv/lesson-XX.csv`: build output for Anki import
- `audio/lesson-XX/*.mp3`: per-item audio files
- `history/runs.json`: incremental processing state

## Anki Model Boundary

The repo treats Anki as an external system reached through AnkiConnect. Local code does not directly manipulate the collection DB; it uses API actions such as:

- `createDeck`
- `createModel`
- `modelFieldNames`
- `modelFieldAdd`
- `notesInfo`
- `updateNoteFields`
- `storeMediaFile`
- `canAddNotes`
- `addNotes`
- `findNotes`

This matters because duplicate behavior follows Anki model rules, not just repo-side history rules.
