# Agent Data Contracts

## Lesson Input JSON

Path pattern:

- `input/lesson-XX-*.json`

Schema:

```json
{
  "lesson": 4,
  "items": [
    {
      "kana": "れい",
      "kanji": "零",
      "vietnamese": "số không"
    }
  ]
}
```

Rules:

- `lesson` must be an integer from `1` to `50`
- `kana` is required
- `kanji` may be empty string
- `vietnamese` is required
- `romaji` is optional in input; the tool can derive it

Do not invent string lesson IDs such as `lesson-age` unless the code is intentionally changed to support them.

## Lesson Key

Normalized by `lesson_key()` in `mamino_anki/models.py`:

- `1` -> `lesson-01`
- `5` -> `lesson-05`

Many paths and IDs depend on this exact normalization.

## Vocabulary Identity

There are two different identity concepts in the system.

### Build Identity

Used by repo history:

- with kanji: `lesson-XX:kana:kanji`
- without kanji: `lesson-XX:kana`

This is what `history/runs.json` uses to determine whether an item has already been built.

### Anki Duplicate Identity

Used by the Anki note model:

- `EntryKey = kana|kanji|vietnamese`

This is intentionally different from build identity. It prevents Anki from collapsing distinct notes that share the same kana but differ in kanji or meaning.

## CSV Contract

CSV file path:

- `csv/lesson-XX.csv`

CSV columns:

```text
kana,kanji,romaji,vietnamese,audio
```

Important:

- CSV does not store `EntryKey`
- `EntryKey` is computed at import time by `AnkiImporter`
- `audio` is written in Anki-ready form, for example `[sound:lesson-04-001.mp3]`

## Audio Contract

Audio directory:

- `audio/lesson-XX/`

Audio filename pattern:

- `lesson-XX-001.mp3`
- `lesson-XX-002.mp3`

Audio numbering is stable per lesson and reused from history where possible.

## History Contract

History path:

- `history/runs.json`

Relevant shape:

```json
{
  "version": 1,
  "lessons": {
    "lesson-04": {
      "csv_path": "csv/lesson-04.csv",
      "audio_dir": "audio/lesson-04",
      "items": []
    }
  },
  "runs": []
}
```

Important behaviors:

- history tracks build state, not Anki import state
- a successful build can exist without a successful Anki import
- rebuilding uses history and filesystem state to decide whether work is missing

## Anki Note Model Contract

Expected field order:

1. `EntryKey`
2. `Kana`
3. `Kanji`
4. `Romaji`
5. `Vietnamese`
6. `Audio`

Why order matters:

- Anki duplicate detection uses the first field
- `EntryKey` must remain first

Card templates render:

- Japanese to Vietnamese
- Audio to Japanese
- Vietnamese to Japanese

`EntryKey` is technical only and should not be rendered on cards.
