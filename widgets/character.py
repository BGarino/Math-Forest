"""
Character widget - renders the prince or princess with
equipped outfit and accessory overlaid as emoji layers.
"""
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.app import App
from kivy.clock import Clock


OUTFIT_EMOJIS = {
    'princess': {
        'outfit_default':  '👸',
        'outfit_fairy':    '🧚',
        'outfit_knight':   '🦸‍♀️',
        'outfit_mage':     '🧙‍♀️',
        'outfit_ninja':    '🥷',
        'outfit_explorer': '🧕',
        'outfit_royal':    '👑',
        'outfit_star':     '⭐',
    },
    'prince': {
        'outfit_default':  '🤴',
        'outfit_fairy':    '🧙‍♂️',
        'outfit_knight':   '🦸‍♂️',
        'outfit_mage':     '🧙‍♂️',
        'outfit_ninja':    '🥷',
        'outfit_explorer': '🧔',
        'outfit_royal':    '👑',
        'outfit_star':     '⭐',
    }
}

ACCESSORY_EMOJIS = {
    'acc_none':   '',
    'acc_crown':  '👑',
    'acc_hat':    '🧢',
    'acc_wings':  '🪺',
    'acc_shield': '🛡️',
    'acc_wand':   '🪄',
    'acc_bow':    '🏹',
    'acc_lantern':'🏮',
}


class CharacterWidget(FloatLayout):
    """
    Full character display used in menus and shop preview.
    Reads current gender, outfit and accessory from save.
    """
    def __init__(self, size_dp=96, **kwargs):
        super().__init__(**kwargs)
        self._size_dp = size_dp
        self.size_hint = (None, None)
        self.size = (dp(size_dp), dp(size_dp + 20))

        self._body = Label(
            font_size=dp(size_dp * 0.65),
            size_hint=(1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.add_widget(self._body)

        self._acc = Label(
            font_size=dp(size_dp * 0.30),
            size_hint=(None, None),
            size=(dp(size_dp * 0.4), dp(size_dp * 0.4)),
            pos_hint={'right': 1.0, 'top': 1.0}
        )
        self.add_widget(self._acc)

        Clock.schedule_once(lambda *_: self.refresh(), 0)

    def refresh(self):
        try:
            save = App.get_running_app().save
            gender = save.get('gender', 'princess')
            outfit = save.get('equipped_outfit', 'outfit_default')
            accessory = save.get('equipped_accessory', 'acc_none')
        except Exception:
            gender, outfit, accessory = 'princess', 'outfit_default', 'acc_none'

        self._body.text = OUTFIT_EMOJIS.get(gender, {}).get(outfit, '👸')
        self._acc.text = ACCESSORY_EMOJIS.get(accessory, '')

    def animate_idle(self):
        """Gentle floating idle animation."""
        anim = (
            Animation(pos_hint={'center_x': 0.5, 'center_y': 0.52}, duration=1.2) +
            Animation(pos_hint={'center_x': 0.5, 'center_y': 0.48}, duration=1.2)
        )
        anim.repeat = True
        anim.start(self._body)

    def animate_victory(self):
        anim = (
            Animation(font_size=dp(self._size_dp * 0.75), duration=0.15) +
            Animation(font_size=dp(self._size_dp * 0.65), duration=0.15)
        ) * 3
        anim.start(self._body)
