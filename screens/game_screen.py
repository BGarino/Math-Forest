"""
Game Screen - math question screen.
Shows the animal emoji, the question, and 4 multiple-choice answers.
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.app import App
from data.lang import get_text


CHOICE_COLORS = [
    (0.15, 0.45, 0.80, 1),   # blue
    (0.80, 0.35, 0.10, 1),   # orange
    (0.18, 0.62, 0.25, 1),   # green
    (0.62, 0.18, 0.62, 1),   # purple
]


class RoundButton(Button):
    """A Button with a rounded colored background drawn on canvas."""

    def __init__(self, btn_color=(0.3, 0.3, 0.3, 1), **kwargs):
        self._btn_color = btn_color
        self._flash_color = None
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.color = (1, 1, 1, 1)
        self.bold = True
        self.bind(pos=self._redraw, size=self._redraw)

    def _redraw(self, *_):
        self.canvas.before.clear()
        c = self._flash_color if self._flash_color else self._btn_color
        with self.canvas.before:
            Color(*c)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(16)])

    def flash(self, correct: bool):
        self._flash_color = (0.1, 0.85, 0.1, 1) if correct else (0.85, 0.1, 0.1, 1)
        self._redraw()
        Clock.schedule_once(self._clear_flash, 0.5)

    def _clear_flash(self, *_):
        self._flash_color = None
        self._redraw()

    def on_press(self):
        Animation(
            size=(self.width * 0.93, self.height * 0.93), duration=0.06
        ).start(self)

    def on_release(self):
        Animation(
            size=(self.width / 0.93, self.height / 0.93), duration=0.06
        ).start(self)


class GameScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._root = FloatLayout()
        self.add_widget(self._root)

    # ------------------------------------------------------------------ #
    #  Lifecycle
    # ------------------------------------------------------------------ #
    def on_enter(self):
        self._root.clear_widgets()
        self._answered = False
        Clock.schedule_once(self._build, 0.05)

    # ------------------------------------------------------------------ #
    #  Build UI
    # ------------------------------------------------------------------ #
    def _build(self, *_):
        app = App.get_running_app()
        save = app.save
        lang = save.get('language', 'en')
        q_data = getattr(app, '_pending_question', {})
        animal_emoji = getattr(app, '_pending_animal_emoji', '🐾')

        root = self._root
        W = root.width or Window.width
        H = root.height or Window.height

        # ── Background ──────────────────────────────────────────────────
        with root.canvas.before:
            Color(0.06, 0.06, 0.18, 1)
            self._bg = Rectangle(pos=(0, 0), size=(W, H))
        root.bind(size=self._on_resize, pos=self._on_resize)

        # ── Animal emoji (large, centered top) ──────────────────────────
        root.add_widget(Label(
            text=animal_emoji,
            font_size=dp(80),
            size_hint=(None, None),
            size=(dp(110), dp(110)),
            pos=(int(W / 2 - dp(55)), int(H * 0.78)),
        ))

        # ── Question text ────────────────────────────────────────────────
        q_text = q_data.get('question', '?')
        q_lbl = Label(
            text=f'[b]{q_text}[/b]',
            markup=True,
            font_size=dp(28),
            color=(1.0, 1.0, 0.55, 1),
            size_hint=(None, None),
            size=(int(W * 0.88), int(dp(80))),
            pos=(int(W * 0.06), int(H * 0.64)),
            halign='center',
            valign='middle',
        )
        q_lbl.bind(size=lambda w, s: setattr(w, 'text_size', s))
        root.add_widget(q_lbl)

        # ── Answer choices ───────────────────────────────────────────────
        choices = q_data.get('choices', ['1', '2', '3', '4'])
        correct = str(q_data.get('answer', choices[0]))
        self._lang = lang

        btn_w = int(W * 0.80)
        btn_h = int(dp(54))
        btn_x = int(W * 0.10)
        gap   = int(dp(14))
        start_y = int(H * 0.56)

        self._choice_btns = []
        for i, choice in enumerate(choices[:4]):
            by = start_y - i * (btn_h + gap)
            btn = RoundButton(
                btn_color=CHOICE_COLORS[i % 4],
                text=str(choice),
                font_size=dp(22),
                size_hint=(None, None),
                size=(btn_w, btn_h),
                pos=(btn_x, by),
            )
            btn.bind(on_release=self._make_answer(btn, choice, correct))
            root.add_widget(btn)
            self._choice_btns.append(btn)

        # ── Feedback label ───────────────────────────────────────────────
        self._fb_lbl = Label(
            text='',
            font_size=dp(22),
            bold=True,
            color=(0.5, 1.0, 0.5, 1),
            size_hint=(None, None),
            size=(int(W * 0.9), int(dp(40))),
            pos=(int(W * 0.05), int(dp(18))),
            halign='center',
        )
        self._fb_lbl.bind(size=lambda w, s: setattr(w, 'text_size', s))
        root.add_widget(self._fb_lbl)

    # ------------------------------------------------------------------ #
    #  Answer handling
    # ------------------------------------------------------------------ #
    def _make_answer(self, btn_widget, choice, correct):
        def _answer(*_):
            if self._answered:
                return
            self._answered = True

            is_correct = str(choice) == str(correct)
            btn_widget.flash(is_correct)

            # Disable all buttons
            for b in self._choice_btns:
                b.disabled = True

            if is_correct:
                self._fb_lbl.text = '✅ ' + get_text(self._lang, 'correct')
                self._fb_lbl.color = (0.3, 1.0, 0.3, 1)
            else:
                self._fb_lbl.text = (
                    '❌ ' + get_text(self._lang, 'wrong')
                    + f'  →  {correct}'
                )
                self._fb_lbl.color = (1.0, 0.35, 0.35, 1)

            Clock.schedule_once(lambda *_: self._return(is_correct), 1.2)
        return _answer

    def _return(self, correct: bool):
        app = App.get_running_app()
        cb = getattr(app, '_maze_callback', None)
        if cb:
            cb(correct)
        self.manager.current = 'maze'

    # ------------------------------------------------------------------ #
    #  Resize
    # ------------------------------------------------------------------ #
    def _on_resize(self, *_):
        root = self._root
        self._bg.size = root.size
        self._bg.pos = root.pos
