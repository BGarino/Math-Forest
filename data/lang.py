"""
Translation helper - loads translations.json and returns text by key.
"""
import json
import os

_cache = {}


def _load():
    global _cache
    if not _cache:
        path = os.path.join(os.path.dirname(__file__), 'translations.json')
        with open(path, 'r', encoding='utf-8') as f:
            _cache = json.load(f)
    return _cache


def get_text(lang: str, key: str) -> str:
    data = _load()
    return data.get(lang, data.get('en', {})).get(key, key)


def all_languages():
    return list(_load().keys())


LANG_NAMES = {
    'en': 'English',
    'hu': 'Magyar',
    'es': 'Español',
    'pt': 'Português',
    'de': 'Deutsch',
    'tl': 'Tagalog',
}
