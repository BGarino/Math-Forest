"""
Local save system using JSON file.
"""
import json
import os
from kivy.app import App

SAVE_FILE = 'mathforest_save.json'

DEFAULT_SAVE = {
    'language': 'en',
    'age_group': '8-10',
    'gender': 'princess',
    'diamonds': 0,
    'current_level': 1,
    'unlocked_levels': [1],
    'completed_levels': [],
    'owned_outfits': ['outfit_default'],
    'owned_accessories': ['acc_none'],
    'owned_companions': ['comp_none'],
    'equipped_outfit': 'outfit_default',
    'equipped_accessory': 'acc_none',
    'equipped_companion': 'comp_none',
    'collected_cards': [],
    'total_stars': 0,
}


class SaveSystem:
    def __init__(self):
        self.data = dict(DEFAULT_SAVE)

    def _path(self):
        try:
            from kivy.app import App
            app = App.get_running_app()
            return os.path.join(app.user_data_dir, SAVE_FILE)
        except Exception:
            return SAVE_FILE

    def load(self):
        path = self._path()
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                self.data.update(loaded)
            except Exception:
                self.data = dict(DEFAULT_SAVE)

    def save(self):
        path = self._path()
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2)
        except Exception:
            pass

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()

    def add_diamonds(self, amount: int):
        self.data['diamonds'] = self.data.get('diamonds', 0) + amount
        self.save()

    def spend_diamonds(self, amount: int) -> bool:
        if self.data.get('diamonds', 0) >= amount:
            self.data['diamonds'] -= amount
            self.save()
            return True
        return False

    def unlock_level(self, level: int):
        unlocked = self.data.get('unlocked_levels', [])
        if level not in unlocked:
            unlocked.append(level)
            self.data['unlocked_levels'] = unlocked
            self.save()

    def complete_level(self, level: int, stars: int = 3):
        completed = self.data.get('completed_levels', [])
        if level not in completed:
            completed.append(level)
            self.data['completed_levels'] = completed
        self.data['total_stars'] = self.data.get('total_stars', 0) + stars
        self.unlock_level(level + 1)
        self.save()

    def add_card(self, card_id: str):
        cards = self.data.get('collected_cards', [])
        if card_id not in cards:
            cards.append(card_id)
            self.data['collected_cards'] = cards
            self.save()

    def own_item(self, item_id: str, category: str) -> bool:
        key = f'owned_{category}'
        return item_id in self.data.get(key, [])

    def buy_item(self, item_id: str, category: str):
        key = f'owned_{category}'
        owned = self.data.get(key, [])
        if item_id not in owned:
            owned.append(item_id)
            self.data[key] = owned
            self.save()

    def equip_item(self, item_id: str, category: str):
        self.data[f'equipped_{category}'] = item_id
        self.save()

    def t(self, key: str) -> str:
        """Quick translation helper"""
        try:
            from data.lang import get_text
            return get_text(self.data.get('language', 'en'), key)
        except Exception:
            return key
