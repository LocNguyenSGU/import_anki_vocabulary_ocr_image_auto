# import_anki_vocabulary_ocr_iamge_auto

Tạo bộ thẻ từ vựng tiếng Nhật cho Anki từ ảnh chụp sách, có CSV, audio phát âm, lịch sử chạy lại, và import trực tiếp vào Anki qua AnkiConnect.

AI agent/Codex should start with `docs/agent/` and local `AGENTS.md` before inferring behavior from generated files.

Project hiện đang dùng cho sách Mamino/Minna theo từng bài. Ví dụ hiện có:

- `lesson-01`: 108 từ, 108 audio, 324 card trong Anki.
- `lesson-02`: 29 từ, 29 audio, 87 card trong Anki.

Mỗi bài được import vào subdeck riêng:

```text
Mamino Vocabulary
├── Bài 01
└── Bài 02
```

## Tính năng

- Tạo CSV theo từng bài: `csv/lesson-XX.csv`.
- Tạo audio MP3 tiếng Nhật bằng `edge-tts`.
- Tự sinh romaji từ kana.
- Lưu lịch sử vào `history/runs.json`.
- Chạy lại không tạo trùng CSV/audio.
- Import trực tiếp vào Anki bằng AnkiConnect.
- Tự tạo note type `Mamino Vocabulary`.
- Tự tạo subdeck theo bài, ví dụ `Mamino Vocabulary::Bài 02`.
- Skip note trùng trên toàn collection.
- Duplicate trong Anki được phân biệt bằng khóa kỹ thuật, không chỉ dựa vào `kana`.
- Có template Anki gồm 3 card:
  - Nhìn tiếng Nhật -> nhớ nghĩa.
  - Nghe audio -> nhớ từ và nghĩa.
  - Nhìn tiếng Việt -> nhớ tiếng Nhật.

## Yêu cầu

- macOS, Linux, hoặc Windows.
- Python 3.12 trở lên.
- Anki desktop.
- Add-on AnkiConnect.
- Internet khi tạo audio bằng `edge-tts`.

## Cài Anki

1. Tải Anki desktop tại:

```text
https://apps.ankiweb.net/
```

2. Cài và mở Anki.
3. Tạo profile hoặc dùng profile mặc định.

## Cài AnkiConnect

1. Mở Anki.
2. Vào menu:

```text
Tools -> Add-ons -> Get Add-ons...
```

3. Nhập mã add-on:

```text
2055492159
```

4. Restart Anki.
5. Kiểm tra AnkiConnect chạy được:

```bash
curl http://localhost:8765
```

Nếu thấy response JSON hoặc lỗi method từ AnkiConnect là được. Khi chạy import, Anki phải đang mở.

## Cài project

Clone repo:

```bash
git clone https://github.com/LocNguyenSGU/import_anki_vocabulary_ocr_iamge_auto.git
cd import_anki_vocabulary_ocr_iamge_auto
```

Cài package:

```bash
python3 -m pip install -e ".[dev]"
```

Kiểm tra:

```bash
python3 -m pytest -q
```

Kỳ vọng:

```text
25 passed
```

## Cấu trúc dữ liệu

Input JSON sau khi đọc ảnh:

```text
input/lesson-01-20260607-images.json
input/lesson-02-20260607-image.json
```

CSV xuất ra:

```text
csv/lesson-01.csv
csv/lesson-02.csv
```

Audio:

```text
audio/lesson-01/*.mp3
audio/lesson-02/*.mp3
```

Lịch sử:

```text
history/runs.json
```

Template Anki:

```text
anki-templates/mamino-vocabulary/
```

## Format input JSON

Ví dụ:

```json
{
  "lesson": 2,
  "items": [
    {
      "kana": "これ",
      "kanji": "",
      "vietnamese": "cái này, đây; vật ở gần người nói"
    },
    {
      "kana": "ほん",
      "kanji": "本",
      "vietnamese": "sách"
    }
  ]
}
```

Field:

- `lesson`: số bài, từ 1 đến 50.
- `kana`: hiragana/katakana.
- `kanji`: kanji nếu có, không có thì để chuỗi rỗng.
- `vietnamese`: nghĩa tiếng Việt.

Tool sẽ tự thêm:

- `romaji`
- tên file audio
- history

## Quy trình từ ảnh sang Anki

### Bước 1: Chụp ảnh từ vựng

Chụp trang từ vựng của sách.

Trong workflow hiện tại, ảnh được đọc bởi trợ lý/Codex trong chat, sau đó tạo file JSON trong `input/`. Ví dụ:

```text
input/lesson-02-20260607-image.json
```

### Bước 2: Build CSV/audio/history

Chạy:

```bash
mamino-anki build --input input/lesson-02-20260607-image.json
```

Kết quả ví dụ:

```text
lesson=lesson-02 added=29 skipped_existing=0 audio_created=29 needs_review=0
```

Nếu chạy lại:

```text
lesson=lesson-02 added=0 skipped_existing=29 audio_created=0 needs_review=0
```

Nghĩa là tool không tạo trùng.

### Bước 3: Import vào Anki

Đảm bảo Anki đang mở, rồi chạy:

```bash
mamino-anki import-anki --csv csv/lesson-02.csv --audio-dir audio/lesson-02
```

Tool tự import vào:

```text
Mamino Vocabulary::Bài 02
```

Kết quả ví dụ:

```text
rows=29 media_uploaded=29 notes_added=29 notes_skipped_duplicate=0 notes_found=29
```

Nếu chạy lại:

```text
rows=29 media_uploaded=29 notes_added=0 notes_skipped_duplicate=29 notes_found=29
```

## Import tất cả bài hiện có

Chạy:

```bash
for file in csv/lesson-*.csv; do
  lesson=$(basename "$file" .csv)
  mamino-anki import-anki --csv "$file" --audio-dir "audio/$lesson"
done
```

## Kiểm tra trong Anki

Sau khi import, trong Anki sẽ có:

```text
Mamino Vocabulary::Bài 01
Mamino Vocabulary::Bài 02
```

Mỗi note tạo 3 card. Ví dụ:

```text
Bài 01: 108 notes -> 324 cards
Bài 02: 29 notes -> 87 cards
```

## Template card

Template nằm ở:

```text
anki-templates/mamino-vocabulary/
```

Các field của note type:

```text
Kana
Kanji
Romaji
Vietnamese
Audio
```

Card 1:

```text
Japanese -> Vietnamese
```

Card 2:

```text
Audio -> Japanese + Vietnamese
```

Card 3:

```text
Vietnamese -> Japanese
```

## Lệnh thường dùng

Chạy test:

```bash
python3 -m pytest -q
```

Build bài 1:

```bash
mamino-anki build --input input/lesson-01-20260607-images.json
```

Import bài 1:

```bash
mamino-anki import-anki --csv csv/lesson-01.csv --audio-dir audio/lesson-01
```

Build bài 2:

```bash
mamino-anki build --input input/lesson-02-20260607-image.json
```

Import bài 2:

```bash
mamino-anki import-anki --csv csv/lesson-02.csv --audio-dir audio/lesson-02
```

## Ghi chú

- Luôn mở Anki trước khi chạy `import-anki`.
- Nếu audio đã tồn tại, tool không tạo lại.
- Nếu note đã tồn tại trong Anki, tool không import trùng.
- Nếu muốn tách bài, không import vào deck cha thủ công; dùng CLI để tự đưa vào `Mamino Vocabulary::Bài XX`.
- `.envrc` là file môi trường local, không nên commit.
