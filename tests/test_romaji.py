from mamino_anki.romaji import kana_to_romaji


def test_hiragana_words():
    assert kana_to_romaji("わたし") == "watashi"
    assert kana_to_romaji("せんせい") == "sensei"
    assert kana_to_romaji("がくせい") == "gakusei"


def test_katakana_words_and_long_vowels():
    assert kana_to_romaji("コーヒー") == "koohii"
    assert kana_to_romaji("スーパー") == "suupaa"


def test_small_tsu_and_youon():
    assert kana_to_romaji("きって") == "kitte"
    assert kana_to_romaji("きょう") == "kyou"
    assert kana_to_romaji("シャツ") == "shatsu"


def test_extended_katakana_sounds():
    assert kana_to_romaji("フィリピン") == "firipin"
    assert kana_to_romaji("ヒンディーご") == "hindiigo"
