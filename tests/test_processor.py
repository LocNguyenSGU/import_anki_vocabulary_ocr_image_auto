import json

from mamino_anki.audio import FakeAudioProvider
from mamino_anki.processor import Processor


def test_processor_writes_csv_audio_and_history(tmp_path):
    processor = Processor(root=tmp_path, audio_provider=FakeAudioProvider())
    raw_items = [{"kana": "わたし", "kanji": "私", "vietnamese": "tôi"}]

    result = processor.process(lesson=1, raw_items=raw_items, now="2026-06-07T00:00:00+07:00")

    assert result.added == 1
    assert result.skipped_existing == 0
    assert result.audio_created == 1
    assert (tmp_path / "csv" / "lesson-01.csv").exists()
    assert (tmp_path / "audio" / "lesson-01" / "lesson-01-001.mp3").exists()
    history = json.loads((tmp_path / "history" / "runs.json").read_text(encoding="utf-8"))
    assert history["runs"][0]["added"] == 1


def test_processor_second_run_skips_existing_complete_item(tmp_path):
    processor = Processor(root=tmp_path, audio_provider=FakeAudioProvider())
    raw_items = [{"kana": "わたし", "kanji": "私", "vietnamese": "tôi"}]

    first = processor.process(lesson=1, raw_items=raw_items, now="2026-06-07T00:00:00+07:00")
    second = processor.process(lesson=1, raw_items=raw_items, now="2026-06-07T00:01:00+07:00")

    assert first.added == 1
    assert second.added == 0
    assert second.skipped_existing == 1
    assert second.audio_created == 0


def test_processor_adds_new_only_input_with_next_audio_number(tmp_path):
    processor = Processor(root=tmp_path, audio_provider=FakeAudioProvider())
    processor.process(
        lesson=1,
        raw_items=[{"kana": "わたし", "kanji": "私", "vietnamese": "tôi"}],
        now="2026-06-07T00:00:00+07:00",
    )

    result = processor.process(
        lesson=1,
        raw_items=[{"kana": "あなた", "kanji": "", "vietnamese": "bạn"}],
        now="2026-06-07T00:01:00+07:00",
    )

    assert result.added == 1
    assert result.skipped_existing == 0
    assert result.audio_created == 1
    assert (tmp_path / "audio" / "lesson-01" / "lesson-01-001.mp3").read_bytes() == (
        b"fake mp3 for: " + "わたし".encode("utf-8")
    )
    assert (tmp_path / "audio" / "lesson-01" / "lesson-01-002.mp3").read_bytes() == (
        b"fake mp3 for: " + "あなた".encode("utf-8")
    )
