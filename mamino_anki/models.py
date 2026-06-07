from __future__ import annotations

from dataclasses import dataclass


CSV_HEADER = ["kana", "kanji", "romaji", "vietnamese", "audio"]


def lesson_key(lesson: int) -> str:
    if lesson < 1 or lesson > 50:
        raise ValueError("lesson must be between 1 and 50")
    return f"lesson-{lesson:02d}"


@dataclass(frozen=True)
class VocabularyItem:
    lesson: int
    kana: str
    kanji: str
    romaji: str
    vietnamese: str
    audio: str

    @property
    def lesson_key(self) -> str:
        return lesson_key(self.lesson)

    @property
    def item_id(self) -> str:
        if self.kanji:
            return f"{self.lesson_key}:{self.kana}:{self.kanji}"
        return f"{self.lesson_key}:{self.kana}"

    @property
    def anki_audio(self) -> str:
        return f"[sound:{self.audio}]"

    def to_csv_row(self) -> dict[str, str]:
        return {
            "kana": self.kana,
            "kanji": self.kanji,
            "romaji": self.romaji,
            "vietnamese": self.vietnamese,
            "audio": self.anki_audio,
        }


@dataclass(frozen=True)
class ProcessResult:
    added: int
    skipped_existing: int
    audio_created: int
    needs_review: int
