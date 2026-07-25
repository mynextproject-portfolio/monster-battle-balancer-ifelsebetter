"""
Translations for Japanese ↔ English language switching.
Japanese is the default language (as agreed with Haruki Sato).
"""

TRANSLATIONS = {
    "ja": {
        # Home screen
        "app_title": "モンスターバトル",
        "app_subtitle": "D&D モンスタービューア",
        "app_description": "2体のモンスターを選んでステータスカードを比較しよう",
        "view_monsters": "モンスターを見る",

        # Monster selection screen
        "monster_selection": "モンスター選択",
        "select_2_monsters": "比較する2体のモンスターを選択",
        "monster_1": "モンスター1",
        "monster_2": "モンスター2",
        "select_monster_1": "モンスター1を選択",
        "select_monster_2": "モンスター2を選択",
        "view_cards": "🃏 カードを見る",
        "select_2_warning": "2体のモンスターを選んでください！",
        "back_to_home": "ホームに戻る",

        # Cards screen
        "monster_cards": "モンスターカード",
        "back_to_selection": "モンスター選択に戻る",
        "hp": "HP",
        "armor_class": "アーマークラス (AC)",
        "strength": "筋力 (STR)",

        # Battle screen & action
        "fight_button": "⚔️ バトル開始！",
        "battle_screen_title": "バトル結果",
        "winner_label": "🏆 勝者:",
        "back_to_cards": "カード画面に戻る",
        "rematch_button": "🔄 再戦",

        # Error messages
        "failed_to_load_monsters": "モンスターの読み込みに失敗しました",
        "check_connection": "インターネット接続を確認してください",
        "failed_to_load_details": "モンスター詳細の読み込みに失敗しました",
        "back": "← 戻る",

        # Language toggle
        "language_label": "English",
    },
    "en": {
        # Home screen
        "app_title": "Monster Battle",
        "app_subtitle": "D&D Monster Viewer",
        "app_description": "Select 2 monsters and compare their stat cards",
        "view_monsters": "View Monsters",

        # Monster selection screen
        "monster_selection": "Monster Selection",
        "select_2_monsters": "Select 2 monsters to compare",
        "monster_1": "Monster 1",
        "monster_2": "Monster 2",
        "select_monster_1": "Select Monster 1",
        "select_monster_2": "Select Monster 2",
        "view_cards": "🃏 View Cards",
        "select_2_warning": "Please select 2 monsters!",
        "back_to_home": "Back to Home",

        # Cards screen
        "monster_cards": "Monster Cards",
        "back_to_selection": "Back to Monster Selection",
        "hp": "HP",
        "armor_class": "Armor Class (AC)",
        "strength": "Strength (STR)",

        # Battle screen & action
        "fight_button": "⚔️ Fight!",
        "battle_screen_title": "Battle Result",
        "winner_label": "🏆 Winner:",
        "back_to_cards": "Back to Cards",
        "rematch_button": "🔄 Rematch",

        # Error messages
        "failed_to_load_monsters": "Failed to load monsters",
        "check_connection": "Please check your internet connection",
        "failed_to_load_details": "Failed to load monster details",
        "back": "← Back",

        # Language toggle
        "language_label": "日本語",
    },
}


def get_lang(page):
    """Get the current language from the page. Defaults to Japanese."""
    return getattr(page, "_language", "ja")


def set_lang(page, lang):
    """Set the current language on the page."""
    page._language = lang


def t(page, key):
    """Translate a key using the current page language."""
    lang = get_lang(page)
    return TRANSLATIONS[lang].get(key, key)
