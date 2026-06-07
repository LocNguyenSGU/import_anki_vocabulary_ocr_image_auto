from __future__ import annotations

import json
from pathlib import Path

from mamino_anki.models import VocabularyItem, lesson_key


class HistoryStore:
    def __init__(self, root: Path):
        self.root = root
        self.path = root / "history" / "runs.json"

    def load(self) -> dict:
        if not self.path.exists():
            return {"version": 1, "lessons": {}, "runs": []}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save(self, data: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def has_item(self, item_id: str) -> bool:
        item = self.get_item(item_id)
        return bool(item and item.get("csv_written") and item.get("audio_created"))

    def get_item(self, item_id: str) -> dict | None:
        data = self.load()
        for lesson in data["lessons"].values():
            for item in lesson.get("items", []):
                if item["id"] == item_id:
                    return item
        return None

    def lesson_items(self, lesson: int) -> list[dict]:
        data = self.load()
        return data["lessons"].get(lesson_key(lesson), {}).get("items", [])

    def record_run(
        self,
        *,
        lesson: int,
        items: list[VocabularyItem],
        added: int,
        skipped_existing: int,
        audio_created: int,
        needs_review: int,
        now: str,
    ) -> None:
        data = self.load()
        key = lesson_key(lesson)
        lesson_data = data["lessons"].setdefault(
            key,
            {
                "csv_path": f"csv/{key}.csv",
                "audio_dir": f"audio/{key}",
                "items": [],
            },
        )

        existing_by_id = {item["id"]: item for item in lesson_data["items"]}
        for item in items:
            payload = {
                "id": item.item_id,
                "kana": item.kana,
                "kanji": item.kanji,
                "romaji": item.romaji,
                "vietnamese": item.vietnamese,
                "audio": item.audio,
                "csv_written": True,
                "audio_created": True,
                "source": "chat-image",
                "created_at": existing_by_id.get(item.item_id, {}).get("created_at", now),
                "updated_at": now,
            }
            existing_by_id[item.item_id] = payload

        lesson_data["items"] = list(existing_by_id.values())
        data["runs"].append(
            {
                "run_id": now,
                "lesson": key,
                "added": added,
                "skipped_existing": skipped_existing,
                "audio_created": audio_created,
                "needs_review": needs_review,
            }
        )
        self.save(data)
