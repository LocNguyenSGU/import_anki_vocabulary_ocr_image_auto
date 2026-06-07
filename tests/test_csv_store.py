import csv

from mamino_anki.csv_store import CsvStore
from mamino_anki.models import VocabularyItem


def test_appends_new_rows_and_writes_header(tmp_path):
    store = CsvStore(tmp_path)
    item = VocabularyItem(1, "わたし", "私", "watashi", "tôi", "lesson-01-001.mp3")

    added = store.append_missing(1, [item])

    assert added == 1
    path = tmp_path / "csv" / "lesson-01.csv"
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert rows == [
        {
            "kana": "わたし",
            "kanji": "私",
            "romaji": "watashi",
            "vietnamese": "tôi",
            "audio": "[sound:lesson-01-001.mp3]",
        }
    ]


def test_does_not_append_duplicate_kana_kanji(tmp_path):
    store = CsvStore(tmp_path)
    first = VocabularyItem(1, "わたし", "私", "watashi", "tôi", "lesson-01-001.mp3")
    second = VocabularyItem(1, "わたし", "私", "watashi", "mình / tôi", "lesson-01-001.mp3")

    assert store.append_missing(1, [first]) == 1
    assert store.append_missing(1, [second]) == 0

    rows = store.read_rows(1)
    assert len(rows) == 1
    assert rows[0]["vietnamese"] == "tôi"
