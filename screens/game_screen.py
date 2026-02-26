"""
Game Screen - shows the math question for the current animal.
Multiple choice layout with animated feedback.
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.app import App
from data.lang import get_text
import random


CHOICE_COLORS = [
    (0.15, 0.50, 0.75, 1),
    (0.75, 0.35, 0.10, 1),
    (0.20, 0.60, 0.25, 1),
    (0.60, 0.20, 0.60, 1),
]


class ChoiceButton(Button):
    def __init__(self, color, **kwargs):
        super().__init__(**kwargs)
        self._color = color
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.font_size = dp(20)
        self.bold = True
        self.color = (1, 1, 1, 1)
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self._color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(18)])

    def flash(self, correct: bool):
        fc = (0.1, 0.85, 0.1, 1) if correct else (0.85, 0.1, 0.1, 1)
        orig = self._color
        self._color = fc
        self._draw()
        Clock.schedule_once(lambda *_: self._restore(orig), 0.4)

    def _restore(self, orig):
        self._color = orig
        self._draw()

    def on_press(self):
        Animation(size=(self.width * 0.94, self.height * 0.94), duration=0.07).start(self)

    def on_release(self):
        Animation(size=(self.width / 0.94, self.height / 0.94), duration=0.07).start(self)


class GameScreen(Screen):
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
        question_data = getattr(app, '_pending_question', {})
        root = self._root

        # Background
        with root.canvas.before:
            Color(0.07, 0.07, 0.18, 1)
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(size=lambda *_: setattr(self._bg, 'size', root.size))

        # Animal emoji display
        animal_emoji = getattr(app, '_pending_animal_emoji', '🐾')
        root.add_widget(Label(
            text=animal_emoji,
            font_size=dp(72),
            size_hint=(None, None), size=(dp(100), dp(100)),
            pos_hint={'center_x': 0.5, 'top': 0.95}
        ))

        # Question box
        q_text = question_data.get('question', '?')
        q_lbl = Label(
            text=f'[b]{q_text}[/b]',
            markup=True,
            font_size=dp(26),
            color=(1, 1, 0.6, 1),
            size_hint=(0.9, None),
            height=dp(90),
            pos_hint={'center_x': 0.5, 'top': 0.76},
            halign='center',
            text_size=(None, None)
        )
        root.add_widget(q_lbl)
        Clock.schedule_once(lambda *_: setattr(
            q_lbl, 'text_size', (q_lbl.width, None)), 0.1)

        # Choices
        choices = question_data.get('choices', ['1', '2', '3', '4'])
        correct = str(question_data.get('answer', choices[0]))
        self._answered = False

        grid = BoxLayout(
            orientation='vertical',
            spacing=dp(12),
            size_hint=(0.85, None),
            height=dp(240),
            pos_hint={'center_x': 0.5, 'top': 0.58}
        )
        for i, choice in enumerate(choices[:4]):
            btn = ChoiceButton(
                color=CHOICE_COLORS[i % len(CHOICE_COLORS)],
                text=str(choice),
                size_hint=(1, None),
                height=dp(54)
            )
            btn.bind(on_release=self._make_answer(choice, correct, lang))
            grid.add_widget(btn)
        root.add_widget(grid)

        # Feedback label
        self._fb_lbl = Label(
            text='',
            font_size=dp(22),
            color=(0.5, 1.0, 0.5, 1),
            size_hint=(1, None), height=dp(40),
            pos_hint={'center_x': 0.5, 'top': 0.15}
        )
        root.add_widget(self._fb_lbl)

    def _make_answer(self, choice, correct, lang):
        def answer(btn_widget):
            if self._answered:
                return
            self._answered = True
            is_correct = str(choice) == str(correct)
            btn_widget.flash(is_correct)
            if is_correct:
                self._fb_lbl.text = get_text(lang, 'correct')
                self._fb_lbl.color = (0.3, 1.0, 0.3, 1)
            else:
                self._fb_lbl.text = f'{get_text(lang, "wrong")} ({correct})'
                self._fb_lbl.color = (1.0, 0.3, 0.3, 1)
            Clock.schedule_once(lambda *_: self._return(is_correct), 1.0)
        return answer

    def _return(self, correct: bool):
        app = App.get_running_app()
        cb = getattr(app, '_maze_callback', None)
        if cb:
            cb(correct)
        self.manager.current = 'maze'
