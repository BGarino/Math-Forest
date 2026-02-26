"""
Companion widget - renders the equipped companion on the maze screen.
The companion sits quietly in the corner, with a subtle idle animation.
"""
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.clock import Clock


COMPANION_DATA = {
    'comp_none':   {'emoji': '',     'name': ''},
    'comp_fox':    {'emoji': '🦊',  'name': 'Fox'},
    'comp_owl':    {'emoji': '🦉',  'name': 'Owl'},
    'comp_bunny':  {'emoji': '🐰',  'name': 'Bunny'},
    'comp_dragon': {'emoji': '🐉',  'name': 'Dragon'},
    'comp_cat':    {'emoji': '🐱',  'name': 'Magic Cat'},
    'comp_fairy':  {'emoji': '🧚',  'name': 'Fairy'},
    'comp_wolf':   {'emoji': '🐺',  'name': 'Wolf Pup'},
}


class CompanionWidget(FloatLayout):
    """
    Displays the companion with name label and idle bounce animation.
    Parameters:
        companion_id (str): key from COMPANION_DATA
        size_dp (int): base size in dp units
    """
    def __init__(self, companion_id='comp_fox', size_dp=48, **kwargs):
        super().__init__(**kwargs)
        data = COMPANION_DATA.get(companion_id, COMPANION_DATA['comp_none'])
        self.size_hint = (None, None)
        self.size = (dp(size_dp + 10), dp(size_dp + 24))

        if not data['emoji']:
            return

        self._emoji_lbl = Label(
            text=data['emoji'],
            font_size=dp(size_dp * 0.75),
            size_hint=(1, None),
            height=dp(size_dp),
            pos_hint={'center_x': 0.5, 'top': 1.0}
        )
        self.add_widget(self._emoji_lbl)

        self._name_lbl = Label(
            text=data['name'],
            font_size=dp(9),
            color=(1, 1, 0.8, 0.85),
            size_hint=(1, None),
            height=dp(16),
            pos_hint={'center_x': 0.5, 'y': 0.0},
            halign='center'
        )
        self.add_widget(self._name_lbl)

        Clock.schedule_once(lambda *_: self._start_idle(), 0.5)

    def _start_idle(self):
        """Gentle bounce - companion is alive but not distracting."""
        if not hasattr(self, '_emoji_lbl'):
            return
        anim = (
            Animation(pos_hint={'center_x': 0.5, 'top': 1.04}, duration=0.9) +
            Animation(pos_hint={'center_x': 0.5, 'top': 1.00}, duration=0.9)
        )
        anim.repeat = True
        anim.start(self._emoji_lbl)

    def set_companion(self, companion_id: str):
        """Hot-swap companion (e.g. after shop purchase)."""
        data = COMPANION_DATA.get(companion_id, COMPANION_DATA['comp_none'])
        if hasattr(self, '_emoji_lbl'):
            self._emoji_lbl.text = data['emoji']
        if hasattr(self, '_name_lbl'):
            self._name_lbl.text = data['name']
