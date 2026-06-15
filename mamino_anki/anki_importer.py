from __future__ import annotations

import base64
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import requests

MODEL_FIELDS = ["EntryKey", "Kana", "Kanji", "Romaji", "Vietnamese", "Audio"]


class AnkiClient(Protocol):
    def request(self, action: str, **params):
        pass


class AnkiConnectClient:
    def __init__(self, url: str = "http://localhost:8765"):
        self.url = url

    def request(self, action: str, **params):
        response = requests.post(
            self.url,
            json={"action": action, "version": 6, "params": params},
            timeout=30,
        ).json()
        if response.get("error") is not None:
            raise RuntimeError(f"{action}: {response['error']}")
        return response.get("result")


@dataclass(frozen=True)
class ImportResult:
    rows: int
    media_uploaded: int
    notes_added: int
    notes_skipped_duplicate: int
    notes_found: int


class AnkiImporter:
    def __init__(self, client: AnkiClient):
        self.client = client

    def import_lesson(
        self,
        *,
        csv_path: Path,
        audio_dir: Path,
        templates_dir: Path,
        deck_name: str,
        model_name: str,
        tags: list[str],
    ) -> ImportResult:
        self.client.request("version")
        self.client.request("createDeck", deck=deck_name)
        self._ensure_model(model_name=model_name, templates_dir=templates_dir)
        media_uploaded = self._upload_media(audio_dir)
        rows = self._read_rows(csv_path)
        notes = self._build_notes(rows=rows, deck_name=deck_name, model_name=model_name, tags=tags)
        can_add = self.client.request("canAddNotes", notes=notes)
        notes_to_add = [note for note, ok in zip(notes, can_add) if ok]
        if notes_to_add:
            self.client.request("addNotes", notes=notes_to_add)
        notes_found = self.client.request("findNotes", query=self._find_query(deck_name, tags))
        return ImportResult(
            rows=len(rows),
            media_uploaded=media_uploaded,
            notes_added=len(notes_to_add),
            notes_skipped_duplicate=len(notes) - len(notes_to_add),
            notes_found=len(notes_found),
        )

    def _ensure_model(self, *, model_name: str, templates_dir: Path) -> None:
        models = self.client.request("modelNames")
        if model_name in models:
            self._ensure_entry_key_field(model_name=model_name)
            return
        self.client.request(
            "createModel",
            modelName=model_name,
            inOrderFields=MODEL_FIELDS,
            css=self._read_template(templates_dir, "styling.css"),
            cardTemplates=[
                {
                    "Name": "Japanese to Vietnamese",
                    "Front": self._read_template(
                        templates_dir, "card-1-japanese-to-vietnamese-front.html"
                    ),
                    "Back": self._read_template(
                        templates_dir, "card-1-japanese-to-vietnamese-back.html"
                    ),
                },
                {
                    "Name": "Audio to Japanese",
                    "Front": self._read_template(templates_dir, "card-2-audio-to-japanese-front.html"),
                    "Back": self._read_template(templates_dir, "card-2-audio-to-japanese-back.html"),
                },
                {
                    "Name": "Vietnamese to Japanese",
                    "Front": self._read_template(
                        templates_dir, "card-3-vietnamese-to-japanese-front.html"
                    ),
                    "Back": self._read_template(
                        templates_dir, "card-3-vietnamese-to-japanese-back.html"
                    ),
                },
            ],
        )

    def _ensure_entry_key_field(self, *, model_name: str) -> None:
        fields = self.client.request("modelFieldNames", modelName=model_name)
        if "EntryKey" not in fields:
            self.client.request("modelFieldAdd", modelName=model_name, fieldName="EntryKey", index=0)
        self._backfill_entry_keys(model_name=model_name)

    def _backfill_entry_keys(self, *, model_name: str) -> None:
        note_ids = self.client.request("findNotes", query=f'note:"{model_name}"')
        if not note_ids:
            return

        for note in self.client.request("notesInfo", notes=note_ids):
            fields = note["fields"]
            entry_key = fields.get("EntryKey", {}).get("value", "").strip()
            if entry_key:
                continue
            self.client.request(
                "updateNoteFields",
                note={
                    "id": note["noteId"],
                    "fields": {
                        "EntryKey": self._entry_key(
                            kana=fields["Kana"]["value"],
                            kanji=fields["Kanji"]["value"],
                            vietnamese=fields["Vietnamese"]["value"],
                        )
                    },
                },
            )

    def _upload_media(self, audio_dir: Path) -> int:
        count = 0
        for path in sorted(audio_dir.glob("*.mp3")):
            self.client.request(
                "storeMediaFile",
                filename=path.name,
                data=base64.b64encode(path.read_bytes()).decode("ascii"),
            )
            count += 1
        return count

    def _read_rows(self, csv_path: Path) -> list[dict[str, str]]:
        with csv_path.open(encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))

    def _build_notes(
        self,
        *,
        rows: list[dict[str, str]],
        deck_name: str,
        model_name: str,
        tags: list[str],
    ) -> list[dict]:
        notes = []
        for row in rows:
            notes.append(
                {
                    "deckName": deck_name,
                    "modelName": model_name,
                    "fields": {
                        "EntryKey": self._entry_key(
                            kana=row["kana"],
                            kanji=row["kanji"],
                            vietnamese=row["vietnamese"],
                        ),
                        "Kana": row["kana"],
                        "Kanji": row["kanji"],
                        "Romaji": row["romaji"],
                        "Vietnamese": row["vietnamese"],
                        "Audio": row["audio"],
                    },
                    "tags": tags,
                    "options": {"allowDuplicate": False, "duplicateScope": "collection"},
                }
            )
        return notes

    def _find_query(self, deck_name: str, tags: list[str]) -> str:
        tag_query = " ".join(f"tag:{tag}" for tag in tags)
        return f'deck:"{deck_name}" {tag_query}'.strip()

    def _read_template(self, templates_dir: Path, name: str) -> str:
        return (templates_dir / name).read_text(encoding="utf-8")

    def _entry_key(self, *, kana: str, kanji: str, vietnamese: str) -> str:
        return f"{kana.strip()}|{kanji.strip()}|{vietnamese.strip()}"
