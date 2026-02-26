"""
Game Screen - standalone question/answer interface
(used when entering from level select directly without maze).
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.app import App

from logic.question_gen import QuestionGenerator
from logic.reward_system import RewardSystem
from data.lang import get_text


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
        self._save = app.save
        self._lang = self._save.get('language', 'en')
        self._age = self._save.get('age_group', '8-10')
        self._level = getattr(app, '_selected_level', 1)
        self._qgen = QuestionGenerator(self._age)
        self._score = 0
        self._total = 0
        self._max_q = 10
        self._root.canvas.before.clear()
        root = self._root
        with root.canvas.before:
            Color(0.06, 0.15, 0.06, 1)
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(size=lambda *_: setattr(self._bg, 'size', root.size))
        self._next_question()

    def _next_question(self):
        if self._total >= self._max_q:
            self._show_result()
            return
        self._root.clear_widgets()
        root = self._root
        lang = self._lang
        q = self._qgen.generate(level=self._level)
        self._current_q = q

        # Progress
        root.add_widget(Label(
            text=f'{get_text(lang,"level")} {self._level}  |  {self._total+1}/{self._max_q}  💎{self._save.get("diamonds",0)}',
            font_size=dp(14), color=(1,1,1,0.9),
            size_hint=(1,None), height=dp(36),
            pos_hint={'center_x':0.5,'top':0.99}
        ))

        # Question card
        card = FloatLayout(size_hint=(0.88,None), height=dp(370),
                           pos_hint={'center_x':0.5,'center_y':0.55})
        with card.canvas.before:
            Color(0.10, 0.26, 0.14, 1)
            RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(20)])
        card.bind(pos=lambda w,*_: self._redraw_card(w),
                  size=lambda w,*_: self._redraw_card(w))

        card.add_widget(Label(
            text='🌲', font_size=dp(40),
            size_hint=(None,None), size=(dp(60),dp(60)),
            pos_hint={'center_x':0.5,'top':0.98}
        ))
        card.add_widget(Label(
            text=f'[b]{q["question"]}[/b]', markup=True,
            font_size=dp(20), color=(1,1,0.7,1),
            size_hint=(1,None), height=dp(80),
            pos_hint={'center_x':0.5,'top':0.80},
            text_size=(dp(300),None), halign='center'
        ))

        tops = [0.60, 0.47, 0.34, 0.21]
        for ch, top in zip(q['choices'], tops):
            cbtn = Button(
                text=str(ch), font_size=dp(17), bold=True,
                background_normal='', background_color=(0.18,0.52,0.22,1),
                size_hint=(0.78,None), height=dp(44),
                pos_hint={'center_x':0.5,'top':top}
            )
            cbtn.bind(on_release=lambda b, ans=str(q['answer']),
                      chosen=str(ch): self._check(ans, chosen, b))
            card.add_widget(cbtn)

        root.add_widget(card)
        card.opacity = 0
        Animation(opacity=1, duration=0.25).start(card)

        back = Button(
            text=get_text(lang,'back'), font_size=dp(14),
            background_normal='', background_color=(0.35,0.35,0.35,1),
            size_hint=(0.35,None), height=dp(38),
            pos_hint={'center_x':0.5,'top':0.10}
        )
        back.bind(on_release=lambda *_: setattr(self.manager,'current','maze'))
        root.add_widget(back)

    def _redraw_card(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(0.10, 0.26, 0.14, 1)
            RoundedRectangle(pos=w.pos, size=w.size, radius=[dp(20)])

    def _check(self, correct, chosen, btn):
        self._total += 1
        lang = self._lang
        if chosen == correct:
            self._score += 1
            btn.background_color = (0.1, 0.8, 0.2, 1)
            feedback = get_text(lang, 'correct')
        else:
            btn.background_color = (0.8, 0.1, 0.1, 1)
            feedback = get_text(lang, 'wrong')
        Clock.schedule_once(lambda dt: self._next_question(), 0.9)

    def _show_result(self):
        self._root.clear_widgets()
        lang = self._lang
        diamonds = RewardSystem.calculate(self._level, self._score, self._total)
        stars = RewardSystem.stars(self._score, self._total)
        self._save.add_diamonds(diamonds)
        root = self._root
        root.add_widget(Label(
            text=f'[b]{get_text(lang,"level_complete")}[/b]\n'
                 f'⭐{"★"*stars}  {self._score}/{self._total}\n'
                 f'💎 +{diamonds}',
            markup=True, font_size=dp(24), color=(1,1,0.5,1),
            size_hint=(1,None), height=dp(160),
            pos_hint={'center_x':0.5,'center_y':0.60},
            halign='center'
        ))
        btn = Button(
            text=get_text(lang,'home'), font_size=dp(18),
            background_normal='', background_color=(0.2,0.68,0.25,1),
            size_hint=(0.5,None), height=dp(52),
            pos_hint={'center_x':0.5,'center_y':0.35}
        )
        btn.bind(on_release=lambda *_: setattr(self.manager,'current','main_menu'))
        root.add_widget(btn)
