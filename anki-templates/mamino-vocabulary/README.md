# Mamino Vocabulary Anki Template

Use these templates with a note type that has these fields:

- `EntryKey`
- `Kana`
- `Kanji`
- `Romaji`
- `Vietnamese`
- `Audio`

`EntryKey` là field kỹ thuật để detect duplicate chính xác hơn. Không cần dùng field này trong card template.

Recommended deck:

```text
Mamino Vocabulary
```

## Import CSV

1. Copy MP3 files from `audio/lesson-XX/` into Anki's `collection.media` folder.
2. Open Anki.
3. Create a note type with the six fields above, và giữ `EntryKey` là field đầu tiên.
4. Import `csv/lesson-XX.csv`.
5. Map columns in this order:
   - `kana` -> `Kana`
   - `kanji` -> `Kanji`
   - `romaji` -> `Romaji`
   - `vietnamese` -> `Vietnamese`
   - `audio` -> `Audio`

Nếu dùng CLI `mamino-anki import-anki`, tool sẽ tự sinh `EntryKey`.

On macOS, Anki media is usually under:

```text
~/Library/Application Support/Anki2/<profile>/collection.media
```

## Cards

Create three card templates:

- Card 1: Japanese -> Vietnamese
- Card 2: Audio -> Japanese + Vietnamese
- Card 3: Vietnamese -> Japanese

Paste `styling.css` into the note type Styling tab, then paste each card's front/back HTML into the matching card template.
