# AGENTS.md

## Read Order

For this repository, read these files before making assumptions:

1. `docs/agent/overview.md`
2. `docs/agent/architecture.md`
3. `docs/agent/data-contracts.md`
4. `docs/agent/workflows.md`
5. `docs/agent/pitfalls.md`

## Project Rules

- Treat `input/*.json` as the preferred human/agent source of lesson content.
- Treat `csv/`, `audio/`, and `history/` as generated state.
- Do not change lesson identity format unless you also update the Python code and tests.
- Do not change Anki note field order casually. `EntryKey` must remain the first field for duplicate detection to work correctly.

## Fast Path

If the task is about lesson content only:

1. edit `input/*.json`
2. build with `mamino-anki build`
3. import with `mamino-anki import-anki`

If the task is about duplicate behavior or Anki import:

1. inspect `mamino_anki/anki_importer.py`
2. inspect `tests/test_anki_importer.py`
3. read `docs/agent/pitfalls.md`
