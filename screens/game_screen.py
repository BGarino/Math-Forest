"""
Game Screen - math question popup.
Canvas-drawn animal (no emoji), clean answer buttons, proper feedback.
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle, Rectangle, Ellipse, Line
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.app import App
from data.lang import get_text

CHOICE_COLORS = [
    (0.15, 0.45, 0.82, 1),
    (0.82, 0.33, 0.10, 1),
    (0.16, 0.62, 0.24, 1),
    (0.62, 0.16, 0.62, 1),
]

ANIMAL_COLORS = [
    (0.90, 0.40, 0.10, 1),
    (0.60, 0.20, 0.70, 1),
    (0.15, 0.55, 0.85, 1),
    (0.85, 0.70, 0.10, 1),
    (0.20, 0.72, 0.40, 1),
    (0.85, 0.20, 0.30, 1),
]


# ── Canvas-drawn animal face ──────────────────────────────────────────────
class AnimalFace(Widget):
    def __init__(self, letter='A', color=(0.8, 0.4, 0.1, 1), **kwargs):
        super().__init__(**kwargs)
        self._letter = letter
        self._acolor = color
        self.size_hint = (None, None)
        self.size = (int(dp(90)), int(dp(90)))
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *_):
        self.canvas.clear()
        x, y = int(self.x), int(self.y)
        w, h = int(self.width), int(self.height)
        cx = x + w // 2
        cy = y + h // 2
        r = min(w, h) // 2 - int(dp(4))
        with self.canvas:
            # Body circle
            Color(*self._acolor)
            Ellipse(pos=(cx - r, cy - r), size=(r * 2, r * 2))
            # Ears
            ear = int(dp(10))
            Color(*self._acolor)
            Ellipse(pos=(cx - r - ear + int(dp(4)), cy + r - ear), size=(ear * 2, ear * 2))
            Ellipse(pos=(cx + r - ear - int(dp(4)), cy + r - ear), size=(ear * 2, ear * 2))
            # Face - white overlay for eyes area
            Color(1, 1, 1, 0.25)
            Ellipse(pos=(cx - r + int(dp(6)), cy - int(dp(4))),
                    size=(r * 2 - int(dp(12)), r - int(dp(4))))
            # Eyes
            Color(0.05, 0.05, 0.05, 1)
            eye_r = int(dp(5))
            Ellipse(pos=(cx - int(dp(12)), cy + int(dp(6))),
                    size=(eye_r * 2, eye_r * 2))
            Ellipse(pos=(cx + int(dp(2)), cy + int(dp(6))),
                    size=(eye_r * 2, eye_r * 2))
            # Nose
            Color(0.6, 0.2, 0.2, 1)
            Ellipse(pos=(cx - int(dp(4)), cy - int(dp(2))),
                    size=(int(dp(8)), int(dp(6))))
            # Smile
            Color(0.3, 0.1, 0.1, 1)
            Line(circle=(cx, cy - int(dp(8)), int(dp(8)), 200, 340),
                 width=dp(1.5))


# ── Rounded answer button ─────────────────────────────────────────────────
class AnswerButton(Button):
    def __init__(self, btn_color=(0.3, 0.3, 0.8, 1), **kwargs):
        self._btn_color = btn_color
        self._flash = None
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.color = (1, 1, 1, 1)
        self.bold = True
        self.bind(pos=self._redraw, size=self._redraw)

    def _redraw(self, *_):
        self.canvas.before.clear()
        c = self._flash if self._flash else self._btn_color
        with self.canvas.before:
            Color(*c)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(14)])

    def flash(self, correct: bool):
        self._flash = (0.1, 0.88, 0.1, 1) if correct else (0.88, 0.1, 0.1, 1)
        self._redraw()
        Clock.schedule_once(self._unflash, 0.5)

    def _unflash(self, *_):
        self._flash = None
        self._redraw()

    def on_press(self):
        Animation(size=(self.width * 0.94, self.height * 0.94),
                  duration=0.07).start(self)

    def on_release(self):
        Animation(size=(self.width / 0.94, self.height / 0.94),
                  duration=0.07).start(self)


# ── Game screen ───────────────────────────────────────────────────────────
class GameScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._root = FloatLayout()
        self.add_widget(self._root)

    def on_enter(self):
        self._root.clear_widgets()
        self._answered = False
        self._choice_btns = []
        Clock.schedule_once(self._build, 0.05)

    def _build(self, *_):
        app = App.get_running_app()
        save = app.save
        lang = save.get('language', 'en')
        self._lang = lang
        q_data = getattr(app, '_pending_question', {})
        animal_letter = getattr(app, '_pending_animal_emoji', 'A')

        root = self._root
        W = root.width or Window.width
        H = root.height or Window.height

        # Background
        with root.canvas.before:
            Color(0.06, 0.06, 0.18, 1)
            self._bg = Rectangle(pos=(0, 0), size=(W, H))
        root.bind(size=self._on_resize, pos=self._on_resize)

        # Pick animal colour from letter
        idx = ord(animal_letter[0]) % len(ANIMAL_COLORS) if animal_letter else 0
        acolor = ANIMAL_COLORS[idx]

        # Animal face widget
        face = AnimalFace(
            letter=animal_letter,
            color=acolor,
            pos=(int(W / 2 - dp(45)), int(H * 0.76)),
        )
        root.add_widget(face)

        # Animal letter label (on top of face)
        root.add_widget(Label(
            text=f'[b]{animal_letter}[/b]',
            markup=True,
            font_size=dp(28),
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(int(dp(90)), int(dp(90))),
            pos=(int(W / 2 - dp(45)), int(H * 0.76)),
            halign='center', valign='middle',
        ))

        # Question text
        q_text = q_data.get('question', '?')
        q_lbl = Label(
            text=f'[b]{q_text}[/b]',
            markup=True,
            font_size=dp(26),
            color=(1.0, 1.0, 0.50, 1),
            size_hint=(None, None),
            size=(int(W * 0.88), int(dp(70))),
            pos=(int(W * 0.06), int(H * 0.63)),
            halign='center', valign='middle',
        )
        q_lbl.bind(size=lambda w, s: setattr(w, 'text_size', s))
        root.add_widget(q_lbl)

        # Divider line
        with root.canvas:
            Color(0.4, 0.4, 0.6, 0.5)
            Line(points=[int(W * 0.1), int(H * 0.61),
                         int(W * 0.9), int(H * 0.61)], width=dp(1))

        # Answer buttons
        choices = q_data.get('choices', ['1', '2', '3', '4'])
        correct = str(q_data.get('answer', choices[0]))

        btn_w = int(W * 0.80)
        btn_h = int(dp(52))
        btn_x = int(W * 0.10)
        gap = int(dp(14))
        start_y = int(H * 0.55)

        for i, choice in enumerate(choices[:4]):
            by = start_y - i * (btn_h + gap)
            btn = AnswerButton(
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

        # Feedback label
        self._fb_lbl = Label(
            text='',
            font_size=dp(20), bold=True,
            color=(0.5, 1.0, 0.5, 1),
            size_hint=(None, None),
            size=(int(W * 0.9), int(dp(38))),
            pos=(int(W * 0.05), int(dp(16))),
            halign='center',
        )
        self._fb_lbl.bind(size=lambda w, s: setattr(w, 'text_size', s))
        root.add_widget(self._fb_lbl)

    def _make_answer(self, btn_widget, choice, correct):
        def _answer(*_):
            if self._answered:
                return
            self._answered = True
            is_correct = str(choice) == str(correct)
            btn_widget.flash(is_correct)
            for b in self._choice_btns:
                b.disabled = True
            if is_correct:
                self._fb_lbl.text = '[b]' + get_text(self._lang, 'correct') + '![/b]'
                self._fb_lbl.markup = True
                self._fb_lbl.color = (0.2, 1.0, 0.2, 1)
            else:
                self._fb_lbl.text = (
                    get_text(self._lang, 'wrong') + '  ->  ' + str(correct)
                )
                self._fb_lbl.color = (1.0, 0.3, 0.3, 1)
            Clock.schedule_once(lambda *_: self._return(is_correct), 1.3)
        return _answer

    def _return(self, correct: bool):
        app = App.get_running_app()
        cb = getattr(app, '_maze_callback', None)
        if cb:
            cb(correct)
        self.manager.current = 'maze'

    def _on_resize(self, *_):
        root = self._root
        self._bg.size = root.size
        self._bg.pos = root.pos
