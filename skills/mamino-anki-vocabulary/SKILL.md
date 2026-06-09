---
name: mamino-anki-vocabulary
description: Use when the user sends Mamino Japanese vocabulary screenshots and wants CSV/audio/history files for Anki.
---

# Mamino Anki Vocabulary

Use this workflow when the user sends one or more screenshots of Mamino vocabulary pages.

## Steps

1. Confirm the lesson number if the user did not provide it.
2. Read the image manually from chat context.
3. Extract **vocabulary rows** (section "I. Từ vựng") into `kana`, `kanji`, and `vietnamese`.
4. Extract **conversation rows** (section "会話" or "【会話】") into `kana`, `kanji`, and `vietnamese`.
5. Ask the user before writing rows with unclear kana, kanji, or Vietnamese meaning.
6. Create an input JSON file under `input/lesson-XX-YYYYMMDD-HHMMSS.json`.
7. Run build:

```bash
python3 -c "from mamino_anki.cli import main; main()" build --input input/lesson-XX-YYYYMMDD-HHMMSS.json
```

8. Run import to Anki:

```bash
python3 -c "from mamino_anki.cli import main; main()" import-anki --csv csv/lesson-XX.csv --audio-dir audio/lesson-XX
```

9. Report results:
   - `csv/lesson-XX.csv` (updated with new items)
   - `audio/lesson-XX/` (new audio files created)
   - Anki import results (notes_added, notes_skipped_duplicate)

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
