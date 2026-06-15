# Agent Pitfalls

## Pitfall 1: Confusing Build Identity with Anki Duplicate Identity

This repo has two layers of deduplication:

- build-time deduplication via `history/runs.json`
- import-time deduplication via Anki note model

They are not the same key.

If you ignore this, you will misdiagnose imports as build bugs.

## Pitfall 2: Anki Duplicate Detection Uses the First Note Field

This was the root cause of a real bug in this repo.

AnkiConnect duplicate detection follows Anki's first-field duplicate behavior. If `Kana` is first, then same-kana entries can be rejected even when kanji or Vietnamese meaning differs.

The fix in this repo is:

- add `EntryKey`
- keep it as the first field
- compute it as `kana|kanji|vietnamese`

Do not reorder fields casually.

## Pitfall 3: Lesson Numbers Are Numeric Only

The repo currently expects lesson numbers as integers from `1` to `50`.

These will fail without code changes:

- `lesson-number`
- `lesson-age`
- arbitrary string lesson IDs

Use descriptive filenames, but keep `"lesson": <int>` in the JSON.

## Pitfall 4: Generated Files Are State, Not Intent

`csv/`, `audio/`, and `history/` reflect what happened in prior runs. They do not fully explain the intended architecture.

Always read docs and source before inferring design from generated artifacts.

## Pitfall 5: Rebuild Success Does Not Guarantee Import Success

You can have:

- successful build
- correct CSV
- correct audio
- import skips in Anki

This is often expected behavior, not corruption.

## Pitfall 6: Existing Anki Collections May Lag Behind Repo Changes

After importer or note-model changes, old notes in Anki may still reflect pre-migration behavior.

If behavior seems inconsistent:

1. verify code
2. verify tests
3. re-import affected lessons
4. only then conclude there is still a bug

## Pitfall 7: Avoid Overusing Generated CSV as the Edit Surface

Preferred source edit surface:

- `input/*.json`

Less preferred:

- direct manual editing of `csv/*.csv`

Why:

- JSON is closer to the intended lesson source
- CSV is a derived artifact
- direct CSV edits are easier to desynchronize from history
