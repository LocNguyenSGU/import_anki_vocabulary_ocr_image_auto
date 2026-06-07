from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

from mamino_anki.anki_importer import AnkiConnectClient, AnkiImporter
from mamino_anki.audio import EdgeTtsAudioProvider, FakeAudioProvider
from mamino_anki.processor import Processor


LESSON_CSV_RE = re.compile(r"lesson-(\d{2})$")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mamino-anki")
    subcommands = parser.add_subparsers(dest="command", required=True)

    build = subcommands.add_parser("build")
    build.add_argument("--root", default=".", help="project root")
    build.add_argument("--input", required=True, help="input JSON file")
    build.add_argument("--fake-audio", action="store_true", help="write deterministic fake audio for tests")
    build.add_argument("--voice", default="ja-JP-NanamiNeural", help="edge-tts Japanese voice")
    build.add_argument("--now", help="ISO timestamp for deterministic tests")

    import_anki = subcommands.add_parser("import-anki")
    import_anki.add_argument("--csv", default="csv/lesson-01.csv", help="lesson CSV path")
    import_anki.add_argument("--audio-dir", default="audio/lesson-01", help="lesson audio directory")
    import_anki.add_argument(
        "--templates-dir",
        default="anki-templates/mamino-vocabulary",
        help="Anki card template directory",
    )
    import_anki.add_argument("--deck", help="Anki deck name")
    import_anki.add_argument("--parent-deck", default="Mamino Vocabulary", help="Anki parent deck name")
    import_anki.add_argument("--model", default="Mamino Vocabulary", help="Anki note type name")
    import_anki.add_argument("--tag", action="append", help="Anki tag")
    import_anki.add_argument("--anki-url", default="http://localhost:8765", help="AnkiConnect URL")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "build":
        return run_build(args)
    if args.command == "import-anki":
        return run_import_anki(args)

    parser.error(f"unsupported command: {args.command}")
    return 2


def run_build(args: argparse.Namespace) -> int:
    root = Path(args.root)
    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    lesson = int(payload["lesson"])
    raw_items = payload["items"]
    now = args.now or datetime.now().astimezone().isoformat(timespec="seconds")

    provider = FakeAudioProvider() if args.fake_audio else EdgeTtsAudioProvider(voice=args.voice)
    result = Processor(root=root, audio_provider=provider).process(
        lesson=lesson,
        raw_items=raw_items,
        now=now,
    )
    print(
        " ".join(
            [
                f"lesson=lesson-{lesson:02d}",
                f"added={result.added}",
                f"skipped_existing={result.skipped_existing}",
                f"audio_created={result.audio_created}",
                f"needs_review={result.needs_review}",
            ]
        )
    )
    return 0


def run_import_anki(args: argparse.Namespace) -> int:
    csv_path = Path(args.csv)
    deck_name = args.deck or default_lesson_deck(csv_path, parent_deck=args.parent_deck)
    result = AnkiImporter(AnkiConnectClient(args.anki_url)).import_lesson(
        csv_path=csv_path,
        audio_dir=Path(args.audio_dir),
        templates_dir=Path(args.templates_dir),
        deck_name=deck_name,
        model_name=args.model,
        tags=args.tag or default_lesson_tags(csv_path),
    )
    print(
        " ".join(
            [
                f"rows={result.rows}",
                f"media_uploaded={result.media_uploaded}",
                f"notes_added={result.notes_added}",
                f"notes_skipped_duplicate={result.notes_skipped_duplicate}",
                f"notes_found={result.notes_found}",
            ]
        )
    )
    return 0


def default_lesson_deck(csv_path: Path, parent_deck: str = "Mamino Vocabulary") -> str:
    match = LESSON_CSV_RE.match(csv_path.stem)
    if not match:
        return parent_deck
    return f"{parent_deck}::Bài {match.group(1)}"


def default_lesson_tags(csv_path: Path) -> list[str]:
    match = LESSON_CSV_RE.match(csv_path.stem)
    if not match:
        return ["mamino"]
    return ["mamino", f"lesson_{match.group(1)}"]


if __name__ == "__main__":
    raise SystemExit(main())
