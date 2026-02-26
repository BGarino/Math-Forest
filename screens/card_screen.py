"""
Card Collection Screen - shows all 10 sets x 15 animals.
Collected cards are shown in full color, locked ones are grayed out.
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp
from kivy.app import App
from kivy.animation import Animation
from data.lang import get_text
from data.levels_config import ANIMALS_PER_SET, THEMES
import json, os


ANIMAL_EMOJIS = [
    '🦊','🐺','🦌','🐻','🦉','🐰','🐿','🦔','🦝','🦫',
    '🦦','🐸','🐢','🦋','🐝','🦎','🐍','🦜','🐧','🦈',
]

SET_COLORS = [
    (0.13,0.45,0.13,1), (0.25,0.20,0.15,1), (0.55,0.80,0.30,1),
    (0.05,0.05,0.20,1), (0.05,0.35,0.65,1), (0.60,0.15,0.05,1),
    (0.60,0.75,0.85,1), (0.55,0.70,0.95,1), (0.75,0.60,0.20,1),
    (0.20,0.08,0.25,1),
]


class CardTile(Label):
    def __init__(self, emoji, name, collected, set_color, **kwargs):
        super().__init__(**kwargs)
        self.text = emoji if collected else '🔒'
        self.font_size = dp(28)
        self.size_hint = (None, None)
        self.size = (dp(58), dp(72))
        self.halign = 'center'
        self.valign = 'middle'
        self._collected = collected
        self._color = set_color
        self._name = name
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            if self._collected:
                Color(*self._color)
            else:
                Color(0.18, 0.18, 0.18, 0.9)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and self._collected:
            anim = Animation(font_size=dp(38), duration=0.12) + \
                   Animation(font_size=dp(28), duration=0.12)
            anim.start(self)
        return super().on_touch_down(touch)


class CardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._root = FloatLayout()
        self.add_widget(self._root)

    def on_enter(self):
        self._root.clear_widgets()
        self._build()

    def _build(self):
        app = App.get_running_app()
        save = app.save
        lang = save.get('language', 'en')
        collected = save.get('collected_cards', [])
        root = self._root

        with root.canvas.before:
            Color(0.05, 0.10, 0.18, 1)
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(size=lambda *_: setattr(self._bg, 'size', root.size))

        # Title
        total_cards = sum(len(s) for s in ANIMALS_PER_SET)
        root.add_widget(Label(
            text=f'[b]🃏 {get_text(lang, "cards")}  [{len(collected)}/{total_cards}][/b]',
            markup=True, font_size=dp(20),
            color=(0.9, 1.0, 0.5, 1),
            size_hint=(1, None), height=dp(44),
            pos_hint={'center_x': 0.5, 'top': 0.99}
        ))

        # Back
        back = Button(
            text=get_text(lang, 'back'), font_size=dp(14),
            background_normal='', background_color=(0.3, 0.3, 0.3, 1),
            size_hint=(None, None), size=(dp(80), dp(34)),
            pos_hint={'x': 0.02, 'top': 0.99}
        )
        back.bind(on_release=lambda *_: setattr(self.manager, 'current', 'main_menu'))
        root.add_widget(back)

        scroll = ScrollView(
            size_hint=(1, None),
            height=root.height * 0.88,
            pos_hint={'center_x': 0.5, 'top': 0.92}
        )
        grid = GridLayout(cols=1, spacing=dp(10), padding=dp(8),
                          size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        for set_idx, (theme, animals) in enumerate(zip(THEMES, ANIMALS_PER_SET)):
            color = SET_COLORS[set_idx % len(SET_COLORS)]
            # Set header
            grid.add_widget(Label(
                text=f'[b]{get_text(lang, theme["name_key"])}[/b]',
                markup=True, font_size=dp(15),
                color=(1, 0.88, 0.25, 1),
                size_hint_y=None, height=dp(32)
            ))
            # Cards row
            row = GridLayout(cols=5, spacing=dp(5),
                             size_hint_y=None, height=dp(78))
            for animal_name in animals:
                card_id = f'set{set_idx}_{animal_name}'
                emoji = ANIMAL_EMOJIS[animals.index(animal_name) % len(ANIMAL_EMOJIS)]
                tile = CardTile(
                    emoji=emoji,
                    name=animal_name,
                    collected=(card_id in collected),
                    set_color=color
                )
                row.add_widget(tile)
            # Pad to 5 cols if needed
            while len(row.children) < 5:
                row.add_widget(Label(size_hint_y=None, height=dp(72)))
            grid.add_widget(row)

        scroll.add_widget(grid)
        root.add_widget(scroll)
