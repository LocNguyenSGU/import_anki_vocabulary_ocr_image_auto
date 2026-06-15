import csv
from pathlib import Path

from mamino_anki.anki_importer import AnkiImporter


class FakeAnkiClient:
    def __init__(self):
        self.models = []
        self.actions = []
        self.can_add = []
        self.model_fields = {}
        self.find_notes = [1000, 1001]
        self.notes_info = []

    def request(self, action, **params):
        self.actions.append((action, params))
        if action == "version":
            return 6
        if action == "modelNames":
            return self.models
        if action == "modelFieldNames":
            return self.model_fields[params["modelName"]]
        if action == "createDeck":
            return 123
        if action == "createModel":
            self.models.append(params["modelName"])
            self.model_fields[params["modelName"]] = params["inOrderFields"]
            return {"id": 456}
        if action == "modelFieldAdd":
            fields = self.model_fields[params["modelName"]]
            index = params.get("index")
            if index is None:
                fields.append(params["fieldName"])
            else:
                fields.insert(index, params["fieldName"])
            return None
        if action == "storeMediaFile":
            return params["filename"]
        if action == "canAddNotes":
            return self.can_add or [True for _ in params["notes"]]
        if action == "addNotes":
            return list(range(1000, 1000 + len(params["notes"])))
        if action == "findNotes":
            return self.find_notes
        if action == "notesInfo":
            return self.notes_info
        if action == "updateNoteFields":
            return None
        raise AssertionError(f"unexpected action: {action}")


def write_csv(path: Path):
    path.parent.mkdir(parents=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["kana", "kanji", "romaji", "vietnamese", "audio"])
        writer.writeheader()
        writer.writerow(
            {
                "kana": "わたし",
                "kanji": "私",
                "romaji": "watashi",
                "vietnamese": "tôi",
                "audio": "[sound:lesson-01-001.mp3]",
            }
        )
        writer.writerow(
            {
                "kana": "あなた",
                "kanji": "",
                "romaji": "anata",
                "vietnamese": "bạn",
                "audio": "[sound:lesson-01-002.mp3]",
            }
        )


def write_templates(path: Path):
    path.mkdir(parents=True)
    for name in [
        "styling.css",
        "card-1-japanese-to-vietnamese-front.html",
        "card-1-japanese-to-vietnamese-back.html",
        "card-2-audio-to-japanese-front.html",
        "card-2-audio-to-japanese-back.html",
        "card-3-vietnamese-to-japanese-front.html",
        "card-3-vietnamese-to-japanese-back.html",
    ]:
        (path / name).write_text(name, encoding="utf-8")


def test_importer_creates_model_uploads_media_and_adds_notes(tmp_path):
    csv_path = tmp_path / "csv" / "lesson-01.csv"
    audio_dir = tmp_path / "audio" / "lesson-01"
    templates_dir = tmp_path / "templates"
    write_csv(csv_path)
    write_templates(templates_dir)
    audio_dir.mkdir(parents=True)
    (audio_dir / "lesson-01-001.mp3").write_bytes(b"audio1")
    (audio_dir / "lesson-01-002.mp3").write_bytes(b"audio2")
    client = FakeAnkiClient()

    result = AnkiImporter(client).import_lesson(
        csv_path=csv_path,
        audio_dir=audio_dir,
        templates_dir=templates_dir,
        deck_name="Mamino Vocabulary",
        model_name="Mamino Vocabulary",
        tags=["mamino", "lesson_01"],
    )

    assert result.rows == 2
    assert result.media_uploaded == 2
    assert result.notes_added == 2
    assert result.notes_skipped_duplicate == 0
    assert result.notes_found == 2
    assert ("createDeck", {"deck": "Mamino Vocabulary"}) in client.actions
    assert any(action == "createModel" for action, _ in client.actions)
    assert any(action == "addNotes" for action, _ in client.actions)


def test_importer_creates_model_with_entry_key_primary_field(tmp_path):
    csv_path = tmp_path / "csv" / "lesson-01.csv"
    audio_dir = tmp_path / "audio" / "lesson-01"
    templates_dir = tmp_path / "templates"
    write_csv(csv_path)
    write_templates(templates_dir)
    audio_dir.mkdir(parents=True)
    (audio_dir / "lesson-01-001.mp3").write_bytes(b"audio1")
    (audio_dir / "lesson-01-002.mp3").write_bytes(b"audio2")
    client = FakeAnkiClient()

    AnkiImporter(client).import_lesson(
        csv_path=csv_path,
        audio_dir=audio_dir,
        templates_dir=templates_dir,
        deck_name="Mamino Vocabulary",
        model_name="Mamino Vocabulary",
        tags=["mamino", "lesson_01"],
    )

    create_model = next(params for action, params in client.actions if action == "createModel")
    assert create_model["inOrderFields"][0] == "EntryKey"

    can_add = next(params for action, params in client.actions if action == "canAddNotes")
    assert can_add["notes"][0]["fields"]["EntryKey"] == "わたし|私|tôi"
    assert can_add["notes"][1]["fields"]["EntryKey"] == "あなた||bạn"


def test_importer_skips_duplicate_notes(tmp_path):
    csv_path = tmp_path / "csv" / "lesson-01.csv"
    audio_dir = tmp_path / "audio" / "lesson-01"
    templates_dir = tmp_path / "templates"
    write_csv(csv_path)
    write_templates(templates_dir)
    audio_dir.mkdir(parents=True)
    (audio_dir / "lesson-01-001.mp3").write_bytes(b"audio1")
    (audio_dir / "lesson-01-002.mp3").write_bytes(b"audio2")
    client = FakeAnkiClient()
    client.models = ["Mamino Vocabulary"]
    client.model_fields["Mamino Vocabulary"] = ["EntryKey", "Kana", "Kanji", "Romaji", "Vietnamese", "Audio"]
    client.can_add = [False, True]

    result = AnkiImporter(client).import_lesson(
        csv_path=csv_path,
        audio_dir=audio_dir,
        templates_dir=templates_dir,
        deck_name="Mamino Vocabulary",
        model_name="Mamino Vocabulary",
        tags=["mamino", "lesson_01"],
    )

    assert result.notes_added == 1
    assert result.notes_skipped_duplicate == 1
    assert not any(action == "createModel" for action, _ in client.actions)


def test_importer_migrates_existing_model_and_backfills_entry_key(tmp_path):
    csv_path = tmp_path / "csv" / "lesson-01.csv"
    audio_dir = tmp_path / "audio" / "lesson-01"
    templates_dir = tmp_path / "templates"
    write_csv(csv_path)
    write_templates(templates_dir)
    audio_dir.mkdir(parents=True)
    (audio_dir / "lesson-01-001.mp3").write_bytes(b"audio1")
    (audio_dir / "lesson-01-002.mp3").write_bytes(b"audio2")
    client = FakeAnkiClient()
    client.models = ["Mamino Vocabulary"]
    client.model_fields["Mamino Vocabulary"] = ["Kana", "Kanji", "Romaji", "Vietnamese", "Audio"]
    client.notes_info = [
        {
            "noteId": 11,
            "fields": {
                "Kana": {"value": "さん", "order": 0},
                "Kanji": {"value": "", "order": 1},
                "Romaji": {"value": "san", "order": 2},
                "Vietnamese": {"value": "anh, chị", "order": 3},
                "Audio": {"value": "[sound:x.mp3]", "order": 4},
                "EntryKey": {"value": "", "order": 5},
            },
        },
        {
            "noteId": 12,
            "fields": {
                "Kana": {"value": "百", "order": 0},
                "Kanji": {"value": "百", "order": 1},
                "Romaji": {"value": "hyaku", "order": 2},
                "Vietnamese": {"value": "trăm", "order": 3},
                "Audio": {"value": "[sound:y.mp3]", "order": 4},
                "EntryKey": {"value": "百|百|trăm", "order": 5},
            },
        },
    ]

    AnkiImporter(client).import_lesson(
        csv_path=csv_path,
        audio_dir=audio_dir,
        templates_dir=templates_dir,
        deck_name="Mamino Vocabulary",
        model_name="Mamino Vocabulary",
        tags=["mamino", "lesson_01"],
    )

    assert ("modelFieldAdd", {"modelName": "Mamino Vocabulary", "fieldName": "EntryKey", "index": 0}) in client.actions
    assert ("findNotes", {"query": 'note:"Mamino Vocabulary"'}) in client.actions
    assert ("notesInfo", {"notes": [1000, 1001]}) in client.actions
    assert (
        "updateNoteFields",
        {"note": {"id": 11, "fields": {"EntryKey": "さん||anh, chị"}}},
    ) in client.actions
    assert not any(
        action == "updateNoteFields" and params["note"]["id"] == 12
        for action, params in client.actions
    )


def test_importer_uses_collection_duplicate_scope(tmp_path):
    csv_path = tmp_path / "csv" / "lesson-01.csv"
    audio_dir = tmp_path / "audio" / "lesson-01"
    templates_dir = tmp_path / "templates"
    write_csv(csv_path)
    write_templates(templates_dir)
    audio_dir.mkdir(parents=True)
    (audio_dir / "lesson-01-001.mp3").write_bytes(b"audio1")
    (audio_dir / "lesson-01-002.mp3").write_bytes(b"audio2")
    client = FakeAnkiClient()

    AnkiImporter(client).import_lesson(
        csv_path=csv_path,
        audio_dir=audio_dir,
        templates_dir=templates_dir,
        deck_name="Mamino Vocabulary::Bài 01",
        model_name="Mamino Vocabulary",
        tags=["mamino", "lesson_01"],
    )

    can_add_action = next(params for action, params in client.actions if action == "canAddNotes")
    assert can_add_action["notes"][0]["deckName"] == "Mamino Vocabulary::Bài 01"
    assert can_add_action["notes"][0]["options"]["duplicateScope"] == "collection"
