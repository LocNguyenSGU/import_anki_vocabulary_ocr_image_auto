import json

from mamino_anki.history import HistoryStore
from mamino_anki.models import VocabularyItem


def test_history_starts_empty(tmp_path):
    history = HistoryStore(tmp_path)

    assert history.has_item("lesson-01:わたし:私") is False


def test_history_records_item_and_run(tmp_path):
    history = HistoryStore(tmp_path)
    item = VocabularyItem(1, "わたし", "私", "watashi", "tôi", "lesson-01-001.mp3")

    history.record_run(
        lesson=1,
        items=[item],
        added=1,
        skipped_existing=0,
        audio_created=1,
        needs_review=0,
        now="2026-06-07T00:00:00+07:00",
    )

    assert history.has_item(item.item_id) is True
    path = tmp_path / "history" / "runs.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["version"] == 1
    assert data["lessons"]["lesson-01"]["items"][0]["audio_created"] is True
    assert data["runs"][0]["added"] == 1
