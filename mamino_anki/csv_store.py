from __future__ import annotations

import csv
from pathlib import Path

from mamino_anki.models import CSV_HEADER, VocabularyItem, lesson_key


class CsvStore:
    def __init__(self, root: Path):
        self.root = root

    def path_for_lesson(self, lesson: int) -> Path:
        return self.root / "csv" / f"{lesson_key(lesson)}.csv"

    def read_rows(self, lesson: int) -> list[dict[str, str]]:
        path = self.path_for_lesson(lesson)
        if not path.exists():
            return []
        with path.open(encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))

    def existing_keys(self, lesson: int) -> set[tuple[str, str]]:
        return {(row["kana"], row["kanji"]) for row in self.read_rows(lesson)}

    def append_missing(self, lesson: int, items: list[VocabularyItem]) -> int:
        path = self.path_for_lesson(lesson)
        path.parent.mkdir(parents=True, exist_ok=True)
        existing = self.existing_keys(lesson)
        should_write_header = not path.exists()
        added = 0

        with path.open("a", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADER)
            if should_write_header:
                writer.writeheader()
            for item in items:
                key = (item.kana, item.kanji)
                if key in existing:
                    continue
                writer.writerow(item.to_csv_row())
                existing.add(key)
                added += 1

        return added
