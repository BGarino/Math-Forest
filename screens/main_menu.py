"""
Main Menu Screen with animated background, floating leaves,
twinkling stars, and interactive buttons.
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.graphics import Color, RoundedRectangle, Ellipse
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.metrics import dp
from kivy.properties import NumericProperty
import random
import math

from data.lang import get_text, LANG_NAMES


class FloatingLeaf(Image):
    angle = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.source = 'assets/images/ui/leaf.png'
        self.size_hint = (None, None)
        self.size = (dp(28), dp(28))
        self._reset()
        Clock.schedule_interval(self._update, 1 / 60)

    def _reset(self):
        self.x = random.randint(0, int(Window.width))
        self.y = Window.height + dp(30)
        self._speed = random.uniform(dp(0.5), dp(1.5))
        self._drift = random.uniform(-dp(0.3), dp(0.3))
        self._wobble = random.uniform(0, math.pi * 2)

    def _update(self, dt):
        self._wobble += dt * 2
        self.x += self._drift + math.sin(self._wobble) * dp(0.5)
        self.y -= self._speed
        self.angle = math.degrees(math.sin(self._wobble)) * 20
        if self.y < -dp(40):
            self._reset()


class TwinkleStar(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = '✦'
        self.font_size = dp(random.randint(8, 18))
        self.color = (1, 1, 0.8, 0)
        self.pos_hint = {
            'x': random.uniform(0, 0.95),
            'top': random.uniform(0.3, 1.0)
        }
        self._twinkle()

    def _twinkle(self):
        target = random.uniform(0.3, 1.0)
        dur = random.uniform(0.5, 2.0)
        anim = Animation(color=(1, 1, 0.8, target), duration=dur) + \
               Animation(color=(1, 1, 0.8, 0), duration=dur)
        anim.bind(on_complete=lambda *_: self._twinkle())
        anim.start(self)


class MenuButton(Button):
    def __init__(self, **kwargs):
        # Extract custom property BEFORE passing kwargs to super
        self._color = kwargs.pop('btn_color', (0.2, 0.7, 0.3, 1))
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.font_size = dp(18)
        self.bold = True
        self.size_hint = (0.65, None)
        self.height = dp(52)
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self._color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(26)])

    def on_press(self):
        Animation(size=(self.width * 0.95, self.height * 0.95),
                  duration=0.08).start(self)

    def on_release(self):
        Animation(size=(self.width / 0.95, self.height / 0.95),
                  duration=0.08).start(self)


class MainMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._layout = FloatLayout()
        self.add_widget(self._layout)
        Clock.schedule_once(self._build_ui, 0)

    def _build_ui(self, *_):
        lay = self._layout
        # Background gradient via colored rectangles
        with lay.canvas.before:
            Color(0.07, 0.25, 0.07, 1)
            self._bg = RoundedRectangle(pos=lay.pos, size=lay.size, radius=[0])
        lay.bind(size=lambda *_: setattr(self._bg, 'size', lay.size))

        # Stars (night-forest feel top area)
        for _ in range(18):
            lay.add_widget(TwinkleStar())

        # Floating leaves
        for _ in range(6):
            lay.add_widget(FloatingLeaf())

        # Title
        title = Label(
            text='[b]🌲 Math-Forest 🌲[/b]',
            markup=True,
            font_size=dp(34),
            color=(0.9, 1.0, 0.5, 1),
            size_hint=(1, None),
            height=dp(70),
            pos_hint={'center_x': 0.5, 'top': 0.95},
        )
        lay.add_widget(title)
        # Pulse animation on title
        anim = Animation(font_size=dp(37), duration=1.0) + \
               Animation(font_size=dp(34), duration=1.0)
        anim.repeat = True
        anim.start(title)

        # Character image placeholder
        char = Label(
            text='👸',
            font_size=dp(72),
            size_hint=(None, None),
            size=(dp(100), dp(100)),
            pos_hint={'center_x': 0.5, 'center_y': 0.72},
        )
        lay.add_widget(char)
        # Bob animation
        bob = Animation(pos_hint={'center_x': 0.5, 'center_y': 0.74}, duration=1.2) + \
              Animation(pos_hint={'center_x': 0.5, 'center_y': 0.72}, duration=1.2)
        bob.repeat = True
        bob.start(char)

        # Buttons
        btn_data = [
            ('play',         (0.20, 0.68, 0.25, 1), self._on_play),
            ('cards',        (0.15, 0.50, 0.70, 1), self._on_cards),
            ('shop',         (0.75, 0.45, 0.10, 1), self._on_shop),
            ('settings',     (0.45, 0.25, 0.65, 1), self._on_settings),
        ]
        tops = [0.58, 0.48, 0.38, 0.28]
        for (key, color, cb), top in zip(btn_data, tops):
            btn = MenuButton(
                text=self._t(key).upper(),
                btn_color=color,
                pos_hint={'center_x': 0.5, 'top': top},
            )
            btn.bind(on_release=cb)
            lay.add_widget(btn)

        # Diamonds display
        self._diamond_lbl = Label(
            text='',
            font_size=dp(16),
            color=(0.9, 0.85, 0.2, 1),
            size_hint=(None, None),
            size=(dp(130), dp(36)),
            pos_hint={'right': 0.98, 'top': 0.99},
        )
        lay.add_widget(self._diamond_lbl)

    def on_enter(self):
        self._refresh_diamonds()
        self._refresh_char()

    def _refresh_diamonds(self):
        try:
            from kivy.app import App
            d = App.get_running_app().save.get('diamonds', 0)
            self._diamond_lbl.text = f'💎 {d}'
        except Exception:
            pass

    def _refresh_char(self):
        try:
            from kivy.app import App
            g = App.get_running_app().save.get('gender', 'princess')
        except Exception:
            g = 'princess'

    def _t(self, key):
        try:
            from kivy.app import App
            lang = App.get_running_app().save.get('language', 'en')
        except Exception:
            lang = 'en'
        return get_text(lang, key)

    def _on_play(self, *_):
        self.manager.current = 'level_select'

    def _on_cards(self, *_):
        self.manager.current = 'cards'

    def _on_shop(self, *_):
        self.manager.current = 'shop'

    def _on_settings(self, *_):
        self.manager.current = 'settings'
