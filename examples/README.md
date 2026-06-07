# Mamino Anki Example

Run with fake audio:

```bash
rtk mamino-anki build --input examples/lesson-01-input.json --fake-audio
```

Run with MP3 audio through edge-tts:

```bash
rtk mamino-anki build --input examples/lesson-01-input.json
```

Outputs:

- `csv/lesson-01.csv`
- `audio/lesson-01/*.mp3`
- `history/runs.json`
