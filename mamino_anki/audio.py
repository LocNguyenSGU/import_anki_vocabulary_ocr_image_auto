from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Protocol

import edge_tts


class AudioProvider(Protocol):
    def ensure_audio(self, *, text: str, output_path: Path) -> bool:
        """Return True when a new file was created."""


class FakeAudioProvider:
    def ensure_audio(self, *, text: str, output_path: Path) -> bool:
        if output_path.exists():
            return False
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"fake mp3 for: " + text.encode("utf-8"))
        return True


class EdgeTtsAudioProvider:
    def __init__(self, voice: str = "ja-JP-NanamiNeural"):
        self.voice = voice

    def ensure_audio(self, *, text: str, output_path: Path) -> bool:
        if output_path.exists():
            return False
        output_path.parent.mkdir(parents=True, exist_ok=True)
        asyncio.run(self._write_audio(text=text, output_path=output_path))
        return True

    async def _write_audio(self, *, text: str, output_path: Path) -> None:
        communicate = edge_tts.Communicate(text=text, voice=self.voice)
        await communicate.save(str(output_path))
