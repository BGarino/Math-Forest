"""
Maze Screen - renders the procedural maze, character movement,
animal encounters, companion display, and gate opening.
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.app import App
from kivy.core.window import Window

from logic.maze_gen import MazeGenerator
from logic.question_gen import QuestionGenerator
from logic.reward_system import RewardSystem
from data.lang import get_text
from data.levels_config import get_theme_for_level, get_animals_for_level, ANIMALS_PER_SET
import random

CELL = dp(36)

THEME_COLORS = {
    'forest':     {'wall': (0.10, 0.35, 0.10, 1), 'path': (0.55, 0.80, 0.40, 1), 'bg': (0.07, 0.22, 0.07, 1)},
    'cave':       {'wall': (0.18, 0.14, 0.10, 1), 'path': (0.45, 0.38, 0.28, 1), 'bg': (0.10, 0.08, 0.05, 1)},
    'clearing':   {'wall': (0.30, 0.55, 0.15, 1), 'path': (0.85, 0.95, 0.60, 1), 'bg': (0.50, 0.75, 0.25, 1)},
    'night':      {'wall': (0.05, 0.05, 0.18, 1), 'path': (0.15, 0.15, 0.40, 1), 'bg': (0.02, 0.02, 0.12, 1)},
    'underwater': {'wall': (0.03, 0.20, 0.50, 1), 'path': (0.20, 0.60, 0.85, 1), 'bg': (0.02, 0.12, 0.35, 1)},
    'volcano':    {'wall': (0.45, 0.10, 0.02, 1), 'path': (0.80, 0.35, 0.05, 1), 'bg': (0.25, 0.05, 0.02, 1)},
    'snow':       {'wall': (0.55, 0.70, 0.80, 1), 'path': (0.90, 0.95, 1.00, 1), 'bg': (0.65, 0.80, 0.90, 1)},
    'cloud':      {'wall': (0.55, 0.70, 0.90, 1), 'path': (0.90, 0.95, 1.00, 1), 'bg': (0.60, 0.80, 1.00, 1)},
    'desert':     {'wall': (0.70, 0.50, 0.15, 1), 'path': (0.95, 0.85, 0.55, 1), 'bg': (0.80, 0.65, 0.25, 1)},
    'haunted':    {'wall': (0.10, 0.05, 0.15, 1), 'path': (0.25, 0.12, 0.35, 1), 'bg': (0.06, 0.03, 0.10, 1)},
}

ANIMAL_EMOJIS = ['🐰','🦊','🦌','🐻','🦉','🐺','🐿','🦔','🦝','🦫','🦦','🦨','🫎','🐱','🦅']


class MazeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._root = FloatLayout()
        self.add_widget(self._root)
        self._maze_gen = None
        self._grid = []
        self._char_pos = [1, 1]
        self._animals_remaining = set()
        self._animals_done = set()
        self._question_active = False
        self._current_animal = None
        self._correct = 0
        self._total = 0

    def on_enter(self):
        self._root.clear_widgets()
        self._setup_level()

    def _setup_level(self):
        app = App.get_running_app()
        self._level = getattr(app, '_selected_level', 1)
        self._save = app.save
        self._lang = self._save.get('language', 'en')
        self._age = self._save.get('age_group', '8-10')
        self._theme = get_theme_for_level(self._level)
        self._colors = THEME_COLORS.get(self._theme['id'], THEME_COLORS['forest'])
        self._question_gen = QuestionGenerator(self._age)
        self._correct = 0
        self._total = 0
        self._animals_done = set()

        mg = MazeGenerator(level=self._level)
        self._grid = mg.generate()
        self._maze_w = mg.width
        self._maze_h = mg.height
        self._animal_positions = set(map(tuple, mg.animal_positions))
        self._animals_remaining = set(map(tuple, mg.animal_positions))
        self._char_pos = [1, 1]
        self._question_active = False

        self._draw_all()

    def _draw_all(self):
        root = self._root
        root.clear_widgets()
        root.canvas.before.clear()

        bg = self._colors['bg']
        with root.canvas.before:
            Color(*bg)
            self._bg_rect = Rectangle(pos=root.pos, size=root.size)
        root.bind(size=self._on_resize, pos=self._on_resize)

        # HUD
        self._hud_lbl = Label(
            text=self._hud_text(),
            markup=True,
            font_size=dp(14),
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=dp(36),
            pos_hint={'center_x': 0.5, 'top': 1.0}
        )
        root.add_widget(self._hud_lbl)

        # Maze canvas widget
        self._maze_widget = FloatLayout(
            size_hint=(None, None),
            size=(self._maze_w * CELL, self._maze_h * CELL),
        )
        self._maze_widget.pos_hint = {'center_x': 0.5, 'center_y': 0.50}
        root.add_widget(self._maze_widget)
        self._draw_maze()

        # D-pad
        self._add_dpad()

        # Back
        back = Button(
            text='🏠', font_size=dp(20),
            background_normal='', background_color=(0.3,0.3,0.3,0.8),
            size_hint=(None,None), size=(dp(44),dp(44)),
            pos_hint={'x':0.02,'top':0.99}
        )
        back.bind(on_release=lambda *_: setattr(self.manager,'current','main_menu'))
        root.add_widget(back)

        # Companion
        comp_id = self._save.get('equipped_companion','comp_none')
        if comp_id != 'comp_none':
            comp_emojis = {'comp_fox':'🦊','comp_owl':'🦉','comp_bunny':'🐰',
                           'comp_dragon':'🐲','comp_cat':'🐱','comp_fairy':'🧚','comp_wolf':'🐺'}
            comp_lbl = Label(
                text=comp_emojis.get(comp_id,'🐾'),
                font_size=dp(36),
                size_hint=(None,None), size=(dp(50),dp(50)),
                pos_hint={'right':0.95,'y':0.18}
            )
            root.add_widget(comp_lbl)
            # Idle bob
            bob = Animation(pos_hint={'right':0.95,'y':0.20},duration=1.0) + \
                  Animation(pos_hint={'right':0.95,'y':0.18},duration=1.0)
            bob.repeat = True
            bob.start(comp_lbl)

    def _draw_maze(self):
        mw = self._maze_widget
        mw.canvas.clear()
        wall_c = self._colors['wall']
        path_c = self._colors['path']
        with mw.canvas:
            for y in range(self._maze_h):
                for x in range(self._maze_w):
                    cell = self._grid[y][x]
                    if cell == MazeGenerator.WALL:
                        Color(*wall_c)
                    else:
                        Color(*path_c)
                    Rectangle(pos=(x*CELL, (self._maze_h-1-y)*CELL),
                               size=(CELL, CELL))
                    # Animal
                    if cell == MazeGenerator.ANIMAL and (x,y) in self._animals_remaining:
                        Color(1,1,1,1)
                    # End gate
                    if cell == MazeGenerator.END:
                        Color(0.9,0.7,0.1,1)
                        Rectangle(pos=(x*CELL+dp(4),(self._maze_h-1-y)*CELL+dp(4)),
                                  size=(CELL-dp(8),CELL-dp(8)))

        # Animal labels
        animals = get_animals_for_level(self._level)
        for idx, (ax, ay) in enumerate(self._animals_remaining):
            emoji = ANIMAL_EMOJIS[idx % len(ANIMAL_EMOJIS)]
            lbl = Label(
                text=emoji, font_size=dp(22),
                size_hint=(None,None), size=(CELL,CELL),
                pos=(ax*CELL, (self._maze_h-1-ay)*CELL)
            )
            mw.add_widget(lbl)

        # Character
        cx, cy = self._char_pos
        gender = self._save.get('gender','princess')
        char_emoji = '👸' if gender == 'princess' else '🤴'
        self._char_lbl = Label(
            text=char_emoji, font_size=dp(26),
            size_hint=(None,None), size=(CELL,CELL),
            pos=(cx*CELL, (self._maze_h-1-cy)*CELL)
        )
        mw.add_widget(self._char_lbl)

    def _add_dpad(self):
        root = self._root
        dirs = [
            ('⬆', ( 0,-1), {'center_x':0.50,'top':0.22}),
            ('⬇', ( 0, 1), {'center_x':0.50,'top':0.13}),
            ('⬅', (-1, 0), {'center_x':0.35,'top':0.175}),
            ('➡', ( 1, 0), {'center_x':0.65,'top':0.175}),
        ]
        for label, delta, ph in dirs:
            btn = Button(
                text=label, font_size=dp(24),
                background_normal='', background_color=(0.15,0.15,0.15,0.85),
                size_hint=(None,None), size=(dp(52),dp(52)),
                pos_hint=ph
            )
            btn.bind(on_release=lambda b, d=delta: self._move(d))
            root.add_widget(btn)

    def _move(self, delta):
        if self._question_active:
            return
        dx, dy = delta
        nx = self._char_pos[0] + dx
        ny = self._char_pos[1] + dy
        if 0 <= nx < self._maze_w and 0 <= ny < self._maze_h:
            cell = self._grid[ny][nx]
            if cell != MazeGenerator.WALL:
                self._char_pos = [nx, ny]
                # Animate
                if self._char_lbl:
                    anim = Animation(
                        pos=(nx*CELL,(self._maze_h-1-ny)*CELL),
                        duration=0.15
                    )
                    anim.start(self._char_lbl)
                # Check animal
                if (nx, ny) in self._animals_remaining:
                    Clock.schedule_once(lambda dt: self._trigger_question(nx,ny), 0.2)
                # Check end
                elif cell == MazeGenerator.END:
                    if not self._animals_remaining:
                        Clock.schedule_once(lambda dt: self._level_complete(), 0.3)

    def _trigger_question(self, ax, ay):
        self._question_active = True
        self._current_animal = (ax, ay)
        q = self._question_gen.generate(level=self._level)
        self._show_question_popup(q, ax, ay)

    def _show_question_popup(self, q, ax, ay):
        root = self._root
        # Dim overlay
        overlay = FloatLayout(
            size_hint=(1,1),
            pos_hint={'center_x':0.5,'center_y':0.5}
        )
        with overlay.canvas.before:
            Color(0,0,0,0.65)
            Rectangle(pos=(0,0), size=Window.size)

        lang = self._lang
        # Card
        card = FloatLayout(
            size_hint=(0.85, None),
            height=dp(320),
            pos_hint={'center_x':0.5,'center_y':0.55}
        )
        with card.canvas.before:
            Color(0.12, 0.28, 0.12, 1)
            RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(18)])
        card.bind(pos=lambda w,*_: self._redraw_card(w),
                  size=lambda w,*_: self._redraw_card(w))
        self._card_widget = card

        animals = get_animals_for_level(self._level)
        idx = list(self._animals_remaining).index((ax,ay)) if (ax,ay) in self._animals_remaining else 0
        emoji = ANIMAL_EMOJIS[idx % len(ANIMAL_EMOJIS)]

        card.add_widget(Label(
            text=emoji, font_size=dp(48),
            size_hint=(None,None), size=(dp(70),dp(70)),
            pos_hint={'center_x':0.5,'top':0.98}
        ))
        card.add_widget(Label(
            text=f'[b]{q["question"]}[/b]', markup=True,
            font_size=dp(18), color=(1,1,0.7,1),
            size_hint=(1, None), height=dp(60),
            pos_hint={'center_x':0.5,'top':0.72},
            text_size=(dp(280),None), halign='center'
        ))

        # Choices
        choice_tops = [0.52, 0.40, 0.28, 0.16]
        for ch, ct in zip(q['choices'], choice_tops):
            cbtn = Button(
                text=str(ch), font_size=dp(16), bold=True,
                background_normal='', background_color=(0.20,0.55,0.25,1),
                size_hint=(0.75, None), height=dp(40),
                pos_hint={'center_x':0.5,'top':ct}
            )
            cbtn.bind(on_release=lambda b, ans=str(q['answer']), chosen=str(ch): \
                      self._answer(ans, chosen, ax, ay))
            card.add_widget(cbtn)

        overlay.add_widget(card)
        root.add_widget(overlay)
        self._question_overlay = overlay

        # Entrance animation
        card.opacity = 0
        Animation(opacity=1, duration=0.3).start(card)

    def _redraw_card(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(0.12, 0.28, 0.12, 1)
            RoundedRectangle(pos=w.pos, size=w.size, radius=[dp(18)])

    def _answer(self, correct, chosen, ax, ay):
        self._total += 1
        lang = self._lang
        if chosen == correct:
            self._correct += 1
            self._animals_remaining.discard((ax, ay))
            self._animals_done.add((ax, ay))
            # Award card
            animals = get_animals_for_level(self._level)
            theme_idx = (self._level-1)//30
            card_id = f'set{theme_idx+1}_{ax}_{ay}'
            self._save.add_card(card_id)
            feedback = get_text(lang, 'correct')
            fb_color = (0.2, 0.9, 0.2, 1)
        else:
            feedback = get_text(lang, 'wrong')
            fb_color = (0.9, 0.2, 0.2, 1)

        # Show feedback then close
        if self._question_overlay:
            lbl = Label(
                text=feedback, font_size=dp(22), bold=True,
                color=fb_color,
                size_hint=(1,None), height=dp(50),
                pos_hint={'center_x':0.5,'center_y':0.5}
            )
            self._question_overlay.add_widget(lbl)
            def _close(dt):
                self._root.remove_widget(self._question_overlay)
                self._question_overlay = None
                self._question_active = False
                self._hud_lbl.text = self._hud_text()
                self._draw_maze()
            Clock.schedule_once(_close, 1.0)

    def _hud_text(self):
        lang = self._lang
        remaining = len(self._animals_remaining)
        done = len(self._animals_done)
        diamonds = self._save.get('diamonds', 0)
        return (f'[b]{get_text(lang,"level")} {self._level}[/b]  '
                f'🐾 {done}/{done+remaining}  💎 {diamonds}')

    def _level_complete(self):
        lang = self._lang
        diamonds = RewardSystem.calculate(
            self._level, self._correct, max(self._total,1)
        )
        stars = RewardSystem.stars(self._correct, max(self._total,1))
        self._save.add_diamonds(diamonds)
        self._save.complete_level(self._level, stars)

        overlay = FloatLayout(size_hint=(1,1))
        with overlay.canvas.before:
            Color(0,0,0,0.75)
            Rectangle(pos=(0,0), size=Window.size)

        overlay.add_widget(Label(
            text=f'[b]{get_text(lang,"level_complete")}[/b]\n'
                 f'{get_text(lang,"gate_open")}\n'
                 f'💎 +{diamonds}  ⭐{"★"*stars}',
            markup=True, font_size=dp(22),
            color=(1,1,0.5,1),
            size_hint=(0.8,None), height=dp(160),
            pos_hint={'center_x':0.5,'center_y':0.60},
            halign='center'
        ))

        next_btn = Button(
            text=get_text(lang,'next'), font_size=dp(18), bold=True,
            background_normal='', background_color=(0.2,0.68,0.25,1),
            size_hint=(0.5,None), height=dp(52),
            pos_hint={'center_x':0.5,'center_y':0.38}
        )
        def _go_next(*_):
            self._root.remove_widget(overlay)
            app = App.get_running_app()
            app._selected_level = self._level + 1
            self.on_enter()
        next_btn.bind(on_release=_go_next)
        overlay.add_widget(next_btn)

        menu_btn = Button(
            text=get_text(lang,'home'), font_size=dp(15),
            background_normal='', background_color=(0.4,0.4,0.4,1),
            size_hint=(0.4,None), height=dp(42),
            pos_hint={'center_x':0.5,'center_y':0.28}
        )
        menu_btn.bind(on_release=lambda *_: setattr(self.manager,'current','main_menu'))
        overlay.add_widget(menu_btn)
        self._root.add_widget(overlay)

    def _on_resize(self, *_):
        self._bg_rect.size = self._root.size
