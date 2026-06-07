import json

from pathlib import Path

from mamino_anki.cli import build_parser, default_lesson_deck, default_lesson_tags, main


def test_cli_build_with_fake_audio(tmp_path, capsys):
    input_path = tmp_path / "input.json"
    input_path.write_text(
        json.dumps(
            {
                "lesson": 1,
                "items": [{"kana": "わたし", "kanji": "私", "vietnamese": "tôi"}],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    code = main(
        [
            "build",
            "--root",
            str(tmp_path),
            "--input",
            str(input_path),
            "--fake-audio",
            "--now",
            "2026-06-07T00:00:00+07:00",
        ]
    )

    output = capsys.readouterr().out
    assert code == 0
    assert "added=1" in output
    assert "audio_created=1" in output


def test_import_anki_custom_tags_do_not_include_default_lesson_01():
    args = build_parser().parse_args(["import-anki", "--tag", "mamino", "--tag", "lesson_02"])

    assert args.tag == ["mamino", "lesson_02"]


def test_default_lesson_deck_uses_csv_lesson_number():
    assert default_lesson_deck(Path("csv/lesson-02.csv")) == "Mamino Vocabulary::Bài 02"


def test_default_lesson_tags_use_csv_lesson_number():
    assert default_lesson_tags(Path("csv/lesson-02.csv")) == ["mamino", "lesson_02"]
