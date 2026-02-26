"""
AnimalCard widget - displays a single collectible animal card
with name, emoji, set badge and collected/locked state.
"""
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle
from kivy.animation import Animation
from kivy.metrics import dp


SET_COLORS = [
    (0.13, 0.45, 0.13, 1),
    (0.25, 0.20, 0.15, 1),
    (0.55, 0.80, 0.30, 1),
    (0.05, 0.05, 0.20, 1),
    (0.05, 0.35, 0.65, 1),
    (0.60, 0.15, 0.05, 1),
    (0.60, 0.75, 0.85, 1),
    (0.55, 0.70, 0.95, 1),
    (0.75, 0.60, 0.20, 1),
    (0.20, 0.08, 0.25, 1),
]


class AnimalCard(FloatLayout):
    """
    A collectible card widget.
    Parameters:
        animal_name (str): e.g. 'fox'
        emoji (str): emoji character
        set_index (int): 0-9
        collected (bool): whether player has this card
    """
    def __init__(self, animal_name='fox', emoji='🦊',
                 set_index=0, collected=False, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(80), dp(110))
        self._collected = collected
        self._color = SET_COLORS[set_index % len(SET_COLORS)]

        self.bind(pos=self._draw, size=self._draw)

        # Emoji
        self._emoji_lbl = Label(
            text=emoji if collected else '🔒',
            font_size=dp(36),
            size_hint=(1, None),
            height=dp(56),
            pos_hint={'center_x': 0.5, 'top': 1.0},
            halign='center'
        )
        self.add_widget(self._emoji_lbl)

        # Name
        self._name_lbl = Label(
            text=animal_name.replace('_', ' ').title() if collected else '???',
            font_size=dp(10),
            color=(1, 1, 1, 0.9),
            size_hint=(1, None),
            height=dp(26),
            pos_hint={'center_x': 0.5, 'top': 0.46},
            halign='center'
        )
        self.add_widget(self._name_lbl)

        # Set badge
        badge_color = self._color
        self._badge = Label(
            text=f'Set {set_index + 1}',
            font_size=dp(9),
            color=(1, 1, 0.8, 1),
            size_hint=(None, None),
            size=(dp(40), dp(18)),
            pos_hint={'center_x': 0.5, 'y': 0.02},
            halign='center'
        )
        self.add_widget(self._badge)

    def _draw(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            if self._collected:
                Color(*self._color)
            else:
                Color(0.15, 0.15, 0.15, 1)
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(12)]
            )
            # Shine effect top
            if self._collected:
                Color(1, 1, 1, 0.08)
                RoundedRectangle(
                    pos=(self.x + dp(4), self.y + self.height * 0.55),
                    size=(self.width - dp(8), self.height * 0.40),
                    radius=[dp(10), dp(10), 0, 0]
                )

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and self._collected:
            anim = (
                Animation(size=(self.width * 1.08, self.height * 1.08), duration=0.10) +
                Animation(size=(self.width, self.height), duration=0.10)
            )
            anim.start(self)
        return super().on_touch_down(touch)
