from __future__ import annotations

import re
from pathlib import Path

from mamino_anki.audio import AudioProvider
from mamino_anki.csv_store import CsvStore
from mamino_anki.history import HistoryStore
from mamino_anki.models import ProcessResult, VocabularyItem, lesson_key
from mamino_anki.romaji import kana_to_romaji


_AUDIO_NAME_RE = re.compile(r"lesson-\d{2}-(\d{3})\.mp3$")


class Processor:
    def __init__(self, *, root: Path, audio_provider: AudioProvider):
        self.root = root
        self.audio_provider = audio_provider
        self.csv_store = CsvStore(root)
        self.history = HistoryStore(root)

    def process(self, *, lesson: int, raw_items: list[dict[str, str]], now: str) -> ProcessResult:
        items = self._build_items(lesson, raw_items)
        to_process: list[VocabularyItem] = []
        skipped_existing = 0

        for item in items:
            audio_path = self._audio_path(item)
            if self.history.has_item(item.item_id) and audio_path.exists():
                skipped_existing += 1
                continue
            to_process.append(item)

        audio_created = 0
        for item in to_process:
            if self.audio_provider.ensure_audio(text=item.kana, output_path=self._audio_path(item)):
                audio_created += 1

        added = self.csv_store.append_missing(lesson, to_process)
        self.history.record_run(
            lesson=lesson,
            items=to_process,
            added=added,
            skipped_existing=skipped_existing,
            audio_created=audio_created,
            needs_review=0,
            now=now,
        )
        return ProcessResult(
            added=added,
            skipped_existing=skipped_existing,
            audio_created=audio_created,
            needs_review=0,
        )

    def _build_items(self, lesson: int, raw_items: list[dict[str, str]]) -> list[VocabularyItem]:
        items = []
        next_audio_index = self._next_audio_index(lesson)
        for raw in raw_items:
            kana = raw["kana"].strip()
            kanji = raw.get("kanji", "").strip()
            vietnamese = raw["vietnamese"].strip()
            romaji = raw.get("romaji", "").strip() or kana_to_romaji(kana)
            item_id = self._item_id(lesson, kana, kanji)
            existing = self.history.get_item(item_id)
            if existing:
                audio = existing["audio"]
            else:
                audio = f"{lesson_key(lesson)}-{next_audio_index:03d}.mp3"
                next_audio_index += 1
            items.append(VocabularyItem(lesson, kana, kanji, romaji, vietnamese, audio))
        return items

    def _audio_path(self, item: VocabularyItem) -> Path:
        return self.root / "audio" / item.lesson_key / item.audio

    def _next_audio_index(self, lesson: int) -> int:
        indexes = []
        for item in self.history.lesson_items(lesson):
            match = _AUDIO_NAME_RE.match(item.get("audio", ""))
            if match:
                indexes.append(int(match.group(1)))

        audio_dir = self.root / "audio" / lesson_key(lesson)
        if audio_dir.exists():
            for path in audio_dir.glob("*.mp3"):
                match = _AUDIO_NAME_RE.match(path.name)
                if match:
                    indexes.append(int(match.group(1)))

        return max(indexes, default=0) + 1

    def _item_id(self, lesson: int, kana: str, kanji: str) -> str:
        if kanji:
            return f"{lesson_key(lesson)}:{kana}:{kanji}"
        return f"{lesson_key(lesson)}:{kana}"
