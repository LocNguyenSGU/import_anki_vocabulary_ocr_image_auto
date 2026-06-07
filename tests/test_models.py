from mamino_anki.models import VocabularyItem, lesson_key


def test_lesson_key_is_zero_padded():
    assert lesson_key(1) == "lesson-01"
    assert lesson_key(50) == "lesson-50"


def test_vocabulary_item_id_uses_lesson_kana_and_kanji():
    item = VocabularyItem(
        lesson=1,
        kana="わたし",
        kanji="私",
        romaji="watashi",
        vietnamese="tôi",
        audio="lesson-01-001.mp3",
    )

    assert item.item_id == "lesson-01:わたし:私"


def test_vocabulary_item_id_omits_empty_kanji_suffix():
    item = VocabularyItem(
        lesson=1,
        kana="コーヒー",
        kanji="",
        romaji="koohii",
        vietnamese="cà phê",
        audio="lesson-01-002.mp3",
    )

    assert item.item_id == "lesson-01:コーヒー"
