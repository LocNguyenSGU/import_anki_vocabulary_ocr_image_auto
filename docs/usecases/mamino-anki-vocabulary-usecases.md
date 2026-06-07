# Use case: Tạo bộ từ vựng Mamino để import vào Anki

## 1. Mục tiêu

Dự án hỗ trợ tạo dữ liệu từ vựng tiếng Nhật từ sách Mamino, bài 1 đến bài 50, để import vào Anki và học kèm phát âm.

Quy trình ban đầu không cần xây app OCR riêng. Người dùng gửi ảnh chụp màn hình trực tiếp trong chat. Trợ lý đọc nội dung trong ảnh, tách từ vựng thành các trường cần thiết, tạo file CSV, tạo hoặc ghi nhận file audio, và lưu lịch sử xử lý để các lần chạy sau chỉ xử lý phần chưa làm.

Đầu ra giai đoạn đầu gồm:

- File CSV theo bài.
- File audio phát âm theo từng từ.
- File lịch sử JSON ghi lại các lần xử lý.

CSV đầu ra mặc định có 5 cột:

```csv
kana,kanji,romaji,vietnamese,audio
```

Trong đó:

- `kana`: chữ hiragana hoặc katakana.
- `kanji`: chữ kanji tương ứng, để trống nếu từ không có kanji.
- `romaji`: cách đọc bằng chữ Latin, phục vụ kiểm tra nhanh và người mới học.
- `vietnamese`: nghĩa tiếng Việt.
- `audio`: tên file audio dùng trong Anki, ví dụ `[sound:lesson-01-001.mp3]`.

Ví dụ:

```csv
kana,kanji,romaji,vietnamese,audio
あさ,朝,asa,buổi sáng,[sound:lesson-01-001.mp3]
コーヒー,,koohii,cà phê,[sound:lesson-01-002.mp3]
がくせい,学生,gakusei,học sinh / sinh viên,[sound:lesson-01-003.mp3]
```

## 2. Phạm vi ban đầu

Phạm vi ban đầu gồm:

- Nhận ảnh chụp màn hình do người dùng gửi trong chat.
- Xác định bài học từ thông tin người dùng cung cấp, ví dụ "Bài 1".
- Đọc bảng từ vựng trong ảnh.
- Chuyển mỗi dòng từ vựng thành các trường: `kana`, `kanji`, `romaji`, `vietnamese`, `audio`.
- Tạo file CSV mới nếu bài đó chưa có file.
- Thêm dòng vào file CSV hiện có nếu cùng một bài có nhiều ảnh.
- Tạo hoặc chuẩn bị audio phát âm cho từng từ.
- Lưu lịch sử xử lý vào file JSON.
- Khi chạy lại, chỉ xử lý những từ hoặc audio chưa có trong lịch sử.
- Báo lại các dòng không rõ để người dùng xác nhận trước khi ghi vào CSV.
- Thiết kế một skill riêng cho workflow này để sau này người dùng chỉ cần gọi skill là có thể tạo CSV/audio từ ảnh.

Ngoài phạm vi ban đầu:

- Chưa xây giao diện web upload ảnh.
- Chưa tích hợp OCR tự động bằng app local.
- Chưa import trực tiếp vào Anki bằng AnkiConnect.
- Chưa tự động lấy ví dụ câu.

## 3. Cấu trúc file đầu ra

CSV sẽ được lưu theo từng bài:

```text
csv/
  lesson-01.csv
  lesson-02.csv
  ...
  lesson-50.csv
```

Audio sẽ được lưu riêng:

```text
audio/
  lesson-01/
    lesson-01-001.mp3
    lesson-01-002.mp3
  lesson-02/
    lesson-02-001.mp3
```

Lịch sử xử lý sẽ được lưu ở dạng JSON:

```text
history/
  runs.json
```

Mỗi file CSV có header:

```csv
kana,kanji,romaji,vietnamese,audio
```

Nếu một bài có nhiều ảnh, các ảnh tiếp theo sẽ được thêm vào cùng file bài đó.

Ví dụ `csv/lesson-01.csv`:

```csv
kana,kanji,romaji,vietnamese,audio
わたし,私,watashi,tôi,[sound:lesson-01-001.mp3]
あなた,,anata,bạn,[sound:lesson-01-002.mp3]
せんせい,先生,sensei,giáo viên,[sound:lesson-01-003.mp3]
```

## 4. Tác nhân

### Người dùng

Người dùng là người học tiếng Nhật bằng sách Mamino và Anki. Người dùng chụp ảnh trang từ vựng, gửi ảnh vào chat, kiểm tra kết quả CSV/audio, sau đó import vào Anki.

### Trợ lý

Trợ lý nhận ảnh, đọc nội dung, chuẩn hóa dữ liệu, hỏi lại khi có dòng không rõ, ghi file CSV, tạo hoặc ghi nhận audio, và cập nhật lịch sử xử lý trong repo.

### Anki

Anki là phần mềm dùng để học từ vựng sau khi người dùng import CSV và copy audio vào thư mục media của Anki.

## 5. Use case chính

### UC-01: Tạo CSV từ ảnh gửi trong chat

**Mục tiêu:** Chuyển ảnh chụp màn hình từ vựng thành file CSV có đủ dữ liệu học từ.

**Điều kiện đầu vào:**

- Người dùng gửi ảnh trong chat.
- Người dùng cho biết ảnh thuộc bài nào, ví dụ "Bài 1".

**Luồng chính:**

1. Người dùng gửi ảnh chụp màn hình.
2. Người dùng ghi rõ bài học, ví dụ "Bài 1".
3. Trợ lý đọc nội dung trong ảnh.
4. Trợ lý tách từng dòng thành `kana`, `kanji`, `romaji`, `vietnamese`.
5. Trợ lý gán tên audio tương ứng cho từng từ.
6. Trợ lý kiểm tra dòng nào không rõ hoặc có khả năng sai.
7. Nếu tất cả dòng rõ ràng, trợ lý ghi vào `csv/lesson-XX.csv`.
8. Trợ lý cập nhật lịch sử xử lý trong `history/runs.json`.
9. Trợ lý báo cáo đã tạo/cập nhật file nào và có bao nhiêu dòng mới.

**Kết quả:**

- File CSV được tạo hoặc cập nhật.
- Dữ liệu có thể import vào Anki.

### UC-02: Tạo audio phát âm cho từng từ

**Mục tiêu:** Mỗi từ vựng có audio để học nghe và phát âm trong Anki.

**Luồng chính:**

1. Trợ lý đọc danh sách từ cần audio từ CSV hoặc từ kết quả vừa nhận diện.
2. Trợ lý kiểm tra lịch sử JSON để biết từ nào đã có audio.
3. Với từ chưa có audio, hệ thống tạo hoặc lấy file audio phát âm.
4. Audio được lưu vào thư mục `audio/lesson-XX/`.
5. Cột `audio` trong CSV được ghi theo format Anki: `[sound:tên-file.mp3]`.
6. Lịch sử JSON được cập nhật trạng thái audio của từng từ.

**Kết quả:**

- Mỗi dòng CSV có thể tham chiếu đến một file audio.
- Khi import vào Anki, card có thể phát âm thanh.

**Ghi chú triển khai:**

- Giai đoạn đầu ưu tiên audio theo `kana`, vì đây là cách đọc trực tiếp.
- Nếu `kanji` có nhiều cách đọc, phát âm phải dựa trên `kana`, không dựa trên kanji.
- Tên file audio cần ổn định để chạy lại không tạo file trùng.

### UC-03: Chạy lại chỉ xử lý phần chưa làm

**Mục tiêu:** Khi thêm ảnh mới hoặc chạy lại tool, hệ thống không xử lý lại toàn bộ dữ liệu đã hoàn thành.

**Luồng chính:**

1. Người dùng gửi thêm ảnh hoặc yêu cầu chạy lại tool.
2. Trợ lý đọc `history/runs.json`.
3. Trợ lý so sánh dữ liệu mới với dữ liệu đã ghi nhận.
4. Nếu từ đã có trong CSV và đã có audio, bỏ qua.
5. Nếu từ đã có trong CSV nhưng thiếu audio, chỉ tạo audio.
6. Nếu từ chưa có trong CSV, thêm dòng mới và tạo audio.
7. Trợ lý cập nhật lịch sử sau khi xử lý xong.

**Kết quả:**

- Chạy lại không tạo dữ liệu trùng.
- Chỉ các mục thiếu mới được xử lý.
- Có thể tiếp tục từ trạng thái đang dở nếu lần trước bị gián đoạn.

### UC-04: Lưu lịch sử xử lý bằng JSON

**Mục tiêu:** Ghi lại các lần chạy để hỗ trợ chạy lại an toàn và kiểm tra lịch sử.

File lịch sử đề xuất:

```text
history/runs.json
```

Cấu trúc JSON đề xuất:

```json
{
  "version": 1,
  "lessons": {
    "lesson-01": {
      "csv_path": "csv/lesson-01.csv",
      "audio_dir": "audio/lesson-01",
      "items": [
        {
          "id": "lesson-01:わたし:私",
          "kana": "わたし",
          "kanji": "私",
          "romaji": "watashi",
          "vietnamese": "tôi",
          "audio": "lesson-01-001.mp3",
          "csv_written": true,
          "audio_created": true,
          "source": "chat-image",
          "created_at": "2026-06-07T00:00:00+07:00",
          "updated_at": "2026-06-07T00:00:00+07:00"
        }
      ]
    }
  },
  "runs": [
    {
      "run_id": "2026-06-07T00:00:00+07:00",
      "lesson": "lesson-01",
      "added": 3,
      "skipped_existing": 0,
      "audio_created": 3,
      "needs_review": 0
    }
  ]
}
```

**Quy tắc định danh từ vựng:**

- `id` nên dựa trên `lesson + kana + kanji`.
- Nếu `kanji` trống, dùng `lesson + kana`.
- Không dùng nghĩa tiếng Việt làm khóa chính vì nghĩa có thể được chỉnh sửa sau.

### UC-05: Xử lý dòng không rõ trong ảnh

**Mục tiêu:** Tránh ghi sai từ vựng vào CSV.

**Tình huống kích hoạt:**

- Ảnh mờ, nhòe, bị cắt mất chữ.
- Kanji/kana khó phân biệt.
- Nghĩa tiếng Việt bị che hoặc không đủ dòng.
- Romaji không chắc chắn.

**Luồng chính:**

1. Trợ lý phát hiện một hoặc nhiều dòng không chắc chắn.
2. Trợ lý tạm dừng việc ghi các dòng đó.
3. Trợ lý báo lại danh sách dòng cần xác nhận.
4. Người dùng xác nhận hoặc sửa lại.
5. Trợ lý ghi dữ liệu đã xác nhận vào CSV.
6. Trợ lý cập nhật lịch sử JSON.

**Kết quả:**

- Chỉ dữ liệu đã rõ ràng hoặc đã được người dùng xác nhận mới được ghi vào file.

### UC-06: Thêm nhiều ảnh vào cùng một bài

**Mục tiêu:** Một bài có thể gồm nhiều ảnh, nhưng đầu ra vẫn là một file CSV duy nhất.

**Luồng chính:**

1. Người dùng gửi ảnh đầu tiên của bài.
2. Trợ lý tạo `csv/lesson-XX.csv`.
3. Người dùng gửi thêm ảnh tiếp theo của cùng bài.
4. Trợ lý đọc ảnh mới.
5. Trợ lý thêm các dòng mới vào cùng file.
6. Trợ lý tránh thêm trùng dựa trên lịch sử JSON và nội dung CSV hiện có.
7. Trợ lý chỉ tạo audio cho từ chưa có audio.

**Kết quả:**

- Mỗi bài có một file CSV tập trung, dễ quản lý và import.
- Nhiều lần chạy vẫn giữ dữ liệu ổn định.

### UC-07: Import CSV và audio vào Anki

**Mục tiêu:** Người dùng import file CSV và audio vào Anki để học.

**Luồng chính:**

1. Người dùng copy file audio vào thư mục media của Anki.
2. Người dùng mở Anki.
3. Người dùng tạo hoặc chọn note type có 5 field:
   - `Kana`
   - `Kanji`
   - `Romaji`
   - `Vietnamese`
   - `Audio`
4. Người dùng import file CSV từ `csv/lesson-XX.csv`.
5. Người dùng map cột CSV vào field Anki tương ứng.
6. Người dùng học từ vựng bằng card template.

**Kết quả:**

- Từ vựng Mamino được đưa vào Anki.
- Card Anki có thể phát âm thanh.

### UC-08: Tạo skill riêng cho workflow Mamino

**Mục tiêu:** Sau này người dùng có thể gọi một skill riêng để xử lý ảnh Mamino thành CSV/audio theo đúng quy tắc đã thống nhất.

**Luồng chính:**

1. Người dùng gọi skill xử lý từ vựng Mamino.
2. Skill kiểm tra bài học, ảnh đầu vào, file CSV, thư mục audio và file lịch sử.
3. Skill đọc ảnh và chuẩn hóa từ vựng.
4. Skill chỉ xử lý các mục chưa hoàn thành.
5. Skill ghi CSV, tạo audio, cập nhật JSON.
6. Skill báo cáo kết quả xử lý.

**Kết quả:**

- Workflow được chuẩn hóa.
- Người dùng không cần nhắc lại quy tắc CSV/audio mỗi lần gửi ảnh.

## 6. Đề xuất deck và card Anki

### Cấu trúc deck khuyến nghị

Khuyến nghị dùng một deck cha và subdeck theo từng bài:

```text
Mamino Vocabulary
Mamino Vocabulary::Bài 01
Mamino Vocabulary::Bài 02
...
Mamino Vocabulary::Bài 50
```

Lý do:

- Mỗi bài nằm riêng trong một subdeck, tránh lẫn bài 1 và bài 2.
- Deck cha `Mamino Vocabulary` vẫn cho phép ôn tổng hợp toàn bộ.
- Tag `lesson_XX` vẫn được giữ để lọc hoặc tìm kiếm nhanh.

Giai đoạn đầu nên ưu tiên CSV theo bài, audio theo bài, subdeck theo bài, và lịch sử xử lý JSON.

### Note type khuyến nghị

Ban đầu:

```text
Kana
Kanji
Romaji
Vietnamese
Audio
```

Mở rộng sau này:

```text
Kana
Kanji
Romaji
Vietnamese
Lesson
Tags
Audio
ExampleJapanese
ExampleVietnamese
```

### Card 1: Nhìn tiếng Nhật, nhớ nghĩa

Front:

```text
{{Kanji}}
{{Kana}}
{{Audio}}
```

Back:

```text
{{Vietnamese}}
{{Romaji}}
```

Ghi chú hiển thị:

- Nếu `Kanji` trống, chỉ hiện `Kana`.
- Chữ tiếng Nhật nên hiện lớn, rõ, dễ đọc.
- Audio nên có nút phát rõ ràng để luyện phát âm.

### Card 2: Nghe phát âm, nhớ từ và nghĩa

Front:

```text
{{Audio}}
```

Back:

```text
{{Kanji}}
{{Kana}}
{{Romaji}}
{{Vietnamese}}
```

Card này giúp luyện nghe và nhận diện từ.

### Card 3: Nhìn tiếng Việt, nhớ tiếng Nhật

Front:

```text
{{Vietnamese}}
```

Back:

```text
{{Kanji}}
{{Kana}}
{{Romaji}}
{{Audio}}
```

Card này giúp luyện khả năng chủ động nhớ từ.

## 7. Quy tắc chuẩn hóa dữ liệu

### Kana

- Ghi hiragana hoặc katakana đúng như trong sách.
- Không tự ý chuyển katakana sang hiragana.
- Đây là nguồn chính để tạo phát âm.

### Kanji

- Ghi kanji nếu ảnh có cung cấp.
- Nếu từ không có kanji, để trống.
- Nếu kanji không rõ, hỏi lại người dùng trước khi ghi.

### Romaji

- Romaji được sinh từ `kana`.
- Không dùng romaji làm nguồn phát âm chính.
- Với âm dài, dùng cách viết dễ học và nhất quán, ví dụ `koohii` cho `コーヒー`.

### Tiếng Việt

- Ghi nghĩa ngắn gọn, dễ học.
- Có thể dùng dấu `/` nếu có nhiều nghĩa gần nhau.
- Không viết giải thích dài trong CSV ban đầu.

### Audio

- Audio phải phát âm theo `kana`.
- Tên file audio phải ổn định giữa các lần chạy.
- Không tạo lại audio nếu file đã tồn tại và lịch sử JSON ghi nhận `audio_created: true`.
- Nếu file audio mất nhưng lịch sử báo đã tạo, hệ thống cần phát hiện và tạo lại.

### Trùng lặp

Một dòng được xem là có khả năng trùng lặp nếu cùng `lesson`, cùng `kana` và cùng `kanji`.

Khi phát hiện trùng lặp:

- Không tự động xóa nếu nghĩa tiếng Việt khác nhau.
- Báo lại để người dùng quyết định gộp nghĩa hay giữ riêng.
- Không tạo thêm audio mới nếu từ đã có audio hợp lệ.

## 8. Lỗi và tình huống cần hỏi lại

Trợ lý cần hỏi lại người dùng khi:

- Không rõ bài học của ảnh.
- Ảnh quá mờ không đọc được.
- Một dòng có nhiều cách đọc hợp lý.
- Kanji không rõ.
- Kana không rõ, vì ảnh hưởng trực tiếp tới audio.
- Nghĩa tiếng Việt bị cắt mất.
- Cột trong ảnh không theo format quen thuộc.
- Dữ liệu mới trùng với dữ liệu cũ nhưng nghĩa tiếng Việt khác nhau.

Trợ lý không nên đoán bừa khi thông tin không chắc chắn.

## 9. Tiêu chí hoàn thành

Một lần xử lý ảnh được xem là hoàn thành khi:

- Ảnh đã được đọc xong.
- Tất cả dòng rõ ràng đã được chuyển thành CSV.
- Các dòng không rõ đã được báo lại hoặc bỏ qua theo yêu cầu người dùng.
- File `csv/lesson-XX.csv` đã được tạo hoặc cập nhật.
- Audio cho các dòng mới đã được tạo hoặc được ghi nhận là đã tồn tại.
- File `history/runs.json` đã được cập nhật.
- Trợ lý báo cáo số dòng đã thêm, số dòng bỏ qua vì đã tồn tại, số audio đã tạo, và file đã thay đổi.

## 10. Hướng phát triển sau

Các tính năng có thể bổ sung sau khi workflow CSV/audio ổn định:

- Thêm cột `lesson` và `tags`.
- Tạo file tổng hợp `csv/mamino-all.csv`.
- Tạo template Anki HTML/CSS đẹp hơn.
- Thêm ví dụ câu tiếng Nhật và dịch tiếng Việt.
- Viết script import từ CSV vào Anki bằng AnkiConnect.
- Xây web local để upload ảnh, sửa bảng, export CSV.

## 11. Cách chạy hiện tại

Build CSV/audio/history từ input JSON:

```bash
mamino-anki build --input input/lesson-01-20260607-images.json
```

Import vào Anki:

```bash
mamino-anki import-anki --csv csv/lesson-01.csv --audio-dir audio/lesson-01
```

Template card Anki được lưu tại:

```text
anki-templates/mamino-vocabulary/
```
