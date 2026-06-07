from mamino_anki.audio import FakeAudioProvider


def test_fake_audio_provider_writes_mp3_placeholder(tmp_path):
    provider = FakeAudioProvider()
    path = tmp_path / "audio" / "lesson-01" / "lesson-01-001.mp3"

    created = provider.ensure_audio(text="わたし", output_path=path)

    assert created is True
    assert path.read_bytes() == b"fake mp3 for: " + "わたし".encode("utf-8")


def test_fake_audio_provider_skips_existing_file(tmp_path):
    provider = FakeAudioProvider()
    path = tmp_path / "audio" / "lesson-01" / "lesson-01-001.mp3"
    path.parent.mkdir(parents=True)
    path.write_bytes(b"existing")

    created = provider.ensure_audio(text="わたし", output_path=path)

    assert created is False
    assert path.read_bytes() == b"existing"
