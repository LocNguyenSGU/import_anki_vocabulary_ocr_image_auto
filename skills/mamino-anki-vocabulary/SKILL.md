---
name: mamino-anki-vocabulary
description: Use when the user sends Mamino Japanese vocabulary screenshots and wants CSV/audio/history files for Anki.
---

# Mamino Anki Vocabulary

Use this workflow when the user sends one or more screenshots of Mamino vocabulary pages.

## Steps

1. Confirm the lesson number if the user did not provide it.
2. Read the image manually from chat context.
3. Extract each vocabulary row into `kana`, `kanji`, and `vietnamese`.
4. Ask the user before writing rows with unclear kana, kanji, or Vietnamese meaning.
5. Create an input JSON file under `input/lesson-XX-YYYYMMDD-HHMMSS.json`.
6. Run:

```bash
rtk mamino-anki build --input input/lesson-XX-YYYYMMDD-HHMMSS.json
```

7. If audio generation needs to be skipped during testing, run:

```bash
rtk mamino-anki build --input input/lesson-XX-YYYYMMDD-HHMMSS.json --fake-audio
```

8. Report changed files:
   - `csv/lesson-XX.csv`
   - `audio/lesson-XX/`
   - `history/runs.json`

## Input JSON Format

```json
{
  "lesson": 1,
  "items": [
    {
      "kana": "わたし",
      "kanji": "私",
      "vietnamese": "tôi"
    }
  ]
}
```

## Rules

- Audio is generated from `kana`.
- Do not use Vietnamese meaning as the duplicate key.
- Do not guess unclear text.
- Running the tool again should skip complete items.
