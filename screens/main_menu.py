"""
Main Menu Screen - no emoji icons (Kivy emoji support unreliable).
Uses colored shapes and text labels instead.
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle, Rectangle, Ellipse, Line
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
import random
import math

from data.lang import get_text


# ── Animated background star ─────────────────────────────────────────────
class StarWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        sz = random.randint(3, 8)
        self.size = (sz, sz)
        self.pos = (random.uniform(0, Window.width),
                    random.uniform(Window.height * 0.35, Window.height))
        self._alpha = random.uniform(0.2, 1.0)
        self._dir = random.choice([-1, 1])
        with self.canvas:
            self._color = Color(1, 1, 0.85, self._alpha)
            self._rect = Ellipse(pos=self.pos, size=self.size)
        Clock.schedule_interval(self._twinkle, random.uniform(0.5, 2.0))

    def _twinkle(self, dt):
        self._alpha += self._dir * 0.08
        if self._alpha >= 1.0:
            self._alpha = 1.0
            self._dir = -1
        elif self._alpha <= 0.1:
            self._alpha = 0.1
            self._dir = 1
        self._color.a = self._alpha


# ── Falling leaf ─────────────────────────────────────────────────────────
class LeafWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (int(dp(12)), int(dp(12)))
        self._reset()
        with self.canvas:
            Color(0.3, 0.85, 0.3, 0.7)
            self._shape = Ellipse(pos=self.pos, size=self.size)
        Clock.schedule_interval(self._update, 1 / 30)

    def _reset(self):
        self.x = random.uniform(0, Window.width)
        self.y = Window.height + dp(20)
        self._speed = random.uniform(dp(0.8), dp(2.0))
        self._drift = random.uniform(-dp(0.4), dp(0.4))
        self._wobble = random.uniform(0, math.pi * 2)

    def _update(self, dt):
        self._wobble += dt * 1.5
        self.x += self._drift + math.sin(self._wobble) * dp(0.4)
        self.y -= self._speed
        self._shape.pos = self.pos
        if self.y < -dp(20):
            self._reset()
            self._shape.pos = self.pos


# ── Rounded menu button ───────────────────────────────────────────────────
class MenuButton(Button):
    def __init__(self, btn_color=(0.2, 0.7, 0.3, 1), **kwargs):
        self._btn_color = btn_color
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.color = (1, 1, 1, 1)
        self.bold = True
        self.font_size = dp(18)
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self._btn_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(26)])

    def on_press(self):
        Animation(size=(self.width * 0.95, self.height * 0.95),
                  duration=0.08).start(self)

    def on_release(self):
        Animation(size=(self.width / 0.95, self.height / 0.95),
                  duration=0.08).start(self)


# ── Character drawn with canvas (no emoji) ────────────────────────────────
class CharacterWidget(Widget):
    def __init__(self, gender='princess', **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (int(dp(60)), int(dp(80)))
        self.gender = gender
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *_):
        self.canvas.clear()
        x, y = self.pos
        w, h = self.size
        cx = x + w / 2
        with self.canvas:
            # Body color
            if self.gender == 'princess':
                Color(0.95, 0.55, 0.75, 1)   # pink dress
            else:
                Color(0.35, 0.55, 0.95, 1)   # blue outfit
            # Body (rounded rect)
            RoundedRectangle(pos=(cx - dp(14), y), size=(dp(28), dp(38)), radius=[dp(8)])
            # Head
            Color(0.98, 0.85, 0.70, 1)
            Ellipse(pos=(cx - dp(14), y + dp(38)), size=(dp(28), dp(28)))
            # Hair / crown
            if self.gender == 'princess':
                Color(0.90, 0.65, 0.10, 1)
                RoundedRectangle(pos=(cx - dp(14), y + dp(60)), size=(dp(28), dp(10)), radius=[dp(4)])
                # Crown points
                Color(1.0, 0.85, 0.0, 1)
                for ox in [-dp(10), 0, dp(10)]:
                    RoundedRectangle(pos=(cx + ox - dp(3), y + dp(68)),
                                     size=(dp(6), dp(10)), radius=[dp(3)])
            else:
                Color(0.40, 0.25, 0.10, 1)
                RoundedRectangle(pos=(cx - dp(14), y + dp(58)), size=(dp(28), dp(12)), radius=[dp(4)])
            # Eyes
            Color(0.1, 0.1, 0.1, 1)
            Ellipse(pos=(cx - dp(8), y + dp(48)), size=(dp(5), dp(5)))
            Ellipse(pos=(cx + dp(3), y + dp(48)), size=(dp(5), dp(5)))
            # Smile
            Color(0.6, 0.2, 0.2, 1)
            Line(circle=(cx, y + dp(43), dp(5), 200, 340), width=dp(1.2))


# ── Main screen ───────────────────────────────────────────────────────────
class MainMenuScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._layout = FloatLayout()
        self.add_widget(self._layout)
        Clock.schedule_once(self._build_ui, 0.05)

    def _build_ui(self, *_):
        lay = self._layout
        W = lay.width or Window.width
        H = lay.height or Window.height

        # Background
        with lay.canvas.before:
            Color(0.06, 0.22, 0.06, 1)
            self._bg = Rectangle(pos=(0, 0), size=(W, H))
        lay.bind(size=self._on_resize, pos=self._on_resize)

        # Stars
        for _ in range(20):
            lay.add_widget(StarWidget())

        # Falling leaves
        for _ in range(5):
            lay.add_widget(LeafWidget())

        # Title
        title = Label(
            text='[b]* Math-Forest *[/b]',
            markup=True,
            font_size=dp(32),
            color=(0.85, 1.0, 0.45, 1),
            size_hint=(None, None),
            size=(int(W * 0.9), int(dp(60))),
            pos=(int(W * 0.05), int(H * 0.88)),
            halign='center',
            valign='middle',
        )
        title.bind(size=lambda w, s: setattr(w, 'text_size', s))
        lay.add_widget(title)
        anim = (Animation(font_size=dp(35), duration=1.1) +
                Animation(font_size=dp(32), duration=1.1))
        anim.repeat = True
        anim.start(title)

        # Character widget (drawn, no emoji)
        try:
            from kivy.app import App
            gender = App.get_running_app().save.get('gender', 'princess')
        except Exception:
            gender = 'princess'

        self._char_widget = CharacterWidget(
            gender=gender,
            pos=(int(W / 2 - dp(30)), int(H * 0.68)),
        )
        lay.add_widget(self._char_widget)

        # Bob animation on character
        base_y = int(H * 0.68)
        bob = (Animation(y=base_y + int(dp(8)), duration=1.1) +
               Animation(y=base_y, duration=1.1))
        bob.repeat = True
        bob.start(self._char_widget)

        # Buttons
        btn_data = [
            ('play',     (0.18, 0.65, 0.22, 1)),
            ('cards',    (0.15, 0.48, 0.72, 1)),
            ('shop',     (0.78, 0.42, 0.10, 1)),
            ('settings', (0.48, 0.22, 0.68, 1)),
        ]
        callbacks = [self._on_play, self._on_cards,
                     self._on_shop, self._on_settings]
        btn_w = int(W * 0.72)
        btn_h = int(dp(52))
        btn_x = int((W - btn_w) / 2)
        start_y = int(H * 0.57)
        gap = int(dp(62))

        for i, ((key, color), cb) in enumerate(zip(btn_data, callbacks)):
            btn = MenuButton(
                btn_color=color,
                text=self._t(key).upper(),
                size_hint=(None, None),
                size=(btn_w, btn_h),
                pos=(btn_x, start_y - i * gap),
            )
            btn.bind(on_release=cb)
            lay.add_widget(btn)

        # Diamonds counter (top right)
        self._diamond_lbl = Label(
            text='',
            font_size=dp(16),
            color=(1.0, 0.88, 0.2, 1),
            size_hint=(None, None),
            size=(int(dp(120)), int(dp(34))),
            pos=(int(W - dp(126)), int(H - dp(36))),
            halign='right',
        )
        lay.add_widget(self._diamond_lbl)

    def on_enter(self):
        self._refresh_diamonds()

    def _refresh_diamonds(self):
        try:
            from kivy.app import App
            d = App.get_running_app().save.get('diamonds', 0)
            self._diamond_lbl.text = f'<>  {d}'
        except Exception:
            pass

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

    def _on_resize(self, *_):
        lay = self._layout
        self._bg.size = lay.size
        self._bg.pos = lay.pos
