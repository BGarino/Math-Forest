"""
Maze Screen - the main gameplay screen.
Shows the procedurally generated maze, the character,
animals as obstacles, and the companion.
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
from kivy.vector import Vector
import random

from logic.maze_gen import MazeGenerator
from logic.question_gen import QuestionGenerator
from logic.reward_system import RewardSystem
from data.lang import get_text
from data.levels_config import get_theme_for_level, get_animals_for_level, diamonds_for_level


CELL = dp(32)

ANIMAL_EMOJIS = [
    '🦊','🐺','🦌','🐻','🦉','🐰','🐿','🦔','🦝','🦫',
    '🦦','🐸','🐢','🦋','🐝','🦎','🐍','🦜','🐧','🦈',
]


class CharacterSprite(Label):
    def __init__(self, gender='princess', **kwargs):
        super().__init__(**kwargs)
        self.gender = gender
        self.font_size = dp(28)
        self.size_hint = (None, None)
        self.size = (CELL, CELL)
        self._update_emoji()

    def _update_emoji(self):
        self.text = '👸' if self.gender == 'princess' else '🤴'

    def move_to(self, gx, gy, maze_origin):
        ox, oy = maze_origin
        target_x = ox + gx * CELL
        target_y = oy + gy * CELL
        anim = Animation(x=target_x, y=target_y, duration=0.18)
        anim.start(self)


class AnimalSprite(Label):
    def __init__(self, gx, gy, emoji, maze_origin, **kwargs):
        super().__init__(**kwargs)
        self.gx = gx
        self.gy = gy
        self.emoji = emoji
        self.text = emoji
        self.font_size = dp(24)
        self.size_hint = (None, None)
        self.size = (CELL, CELL)
        ox, oy = maze_origin
        self.pos = (ox + gx * CELL, oy + gy * CELL)
        self.defeated = False

    def defeat(self):
        self.defeated = True
        anim = Animation(font_size=dp(36), opacity=0, duration=0.5)
        anim.bind(on_complete=lambda *_: self.parent.remove_widget(self) if self.parent else None)
        anim.start(self)


class CompanionSprite(Label):
    def __init__(self, companion_id, **kwargs):
        super().__init__(**kwargs)
        COMPANION_EMOJIS = {
            'comp_fox': '🦊', 'comp_owl': '🦉', 'comp_bunny': '🐰',
            'comp_dragon': '🐉', 'comp_cat': '🐱', 'comp_fairy': '🧚',
            'comp_wolf': '🐺', 'comp_none': ''
        }
        self.text = COMPANION_EMOJIS.get(companion_id, '')
        self.font_size = dp(22)
        self.size_hint = (None, None)
        self.size = (dp(36), dp(36))


class MazeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._root = FloatLayout()
        self.add_widget(self._root)
        self._char = None
        self._animals = []
        self._char_pos = [1, 1]
        self._pending_animal = None

    def on_enter(self):
        self._root.clear_widgets()
        self._animals = []
        self._char_pos = [1, 1]
        self._build()

    def _build(self):
        app = App.get_running_app()
        save = app.save
        lang = save.get('language', 'en')
        level = getattr(app, '_selected_level', 1)
        age_group = save.get('age_group', '8-10')
        gender = save.get('gender', 'princess')
        companion_id = save.get('equipped_companion', 'comp_none')
        theme = get_theme_for_level(level)
        root = self._root

        # Background
        with root.canvas.before:
            Color(*theme['bg_color'])
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(size=self._on_resize, pos=self._on_resize)

        # HUD
        self._lives = 3
        self._correct = 0
        self._total = 0
        self._level = level
        self._lang = lang
        self._age_group = age_group

        self._hud_lbl = Label(
            text=self._hud_text(),
            font_size=dp(14),
            color=(1, 1, 1, 1),
            size_hint=(1, None), height=dp(36),
            pos_hint={'center_x': 0.5, 'top': 1.0},
            halign='center'
        )
        root.add_widget(self._hud_lbl)

        # Back button
        back = Button(
            text=get_text(lang, 'home'),
            font_size=dp(13),
            background_normal='', background_color=(0.3, 0.3, 0.3, 0.9),
            size_hint=(None, None), size=(dp(70), dp(32)),
            pos_hint={'x': 0.02, 'top': 1.0}
        )
        back.bind(on_release=lambda *_: setattr(self.manager, 'current', 'main_menu'))
        root.add_widget(back)

        # Generate maze
        gen = MazeGenerator(level=level)
        self._grid = gen.generate()
        self._maze_w = gen.width
        self._maze_h = gen.height
        self._animal_positions = list(gen.animal_positions)

        # Question generator
        self._qgen = QuestionGenerator(age_group)

        # Draw maze
        maze_pixel_w = self._maze_w * CELL
        maze_pixel_h = self._maze_h * CELL
        ox = (root.width - maze_pixel_w) / 2
        oy = (root.height - maze_pixel_h) / 2 + dp(20)
        self._maze_origin = (ox, oy)
        self._draw_maze(ox, oy)

        # Character
        self._char = CharacterSprite(gender=gender)
        self._char.pos = (ox + CELL, oy + CELL)
        root.add_widget(self._char)

        # Animals
        animal_list = get_animals_for_level(level)
        for i, (ax, ay) in enumerate(self._animal_positions):
            emoji = ANIMAL_EMOJIS[i % len(ANIMAL_EMOJIS)]
            sprite = AnimalSprite(ax, ay, emoji, (ox, oy))
            self._animals.append(sprite)
            root.add_widget(sprite)

        # Companion
        if companion_id != 'comp_none':
            comp = CompanionSprite(companion_id)
            comp.pos_hint = {'right': 0.98, 'y': 0.02}
            root.add_widget(comp)

        # D-pad controls
        self._add_dpad()

    def _draw_maze(self, ox, oy):
        root = self._root
        with root.canvas:
            for row in range(self._maze_h):
                for col in range(self._maze_w):
                    cell = self._grid[row][col]
                    cx = ox + col * CELL
                    cy = oy + row * CELL
                    if cell == MazeGenerator.WALL:
                        Color(0.1, 0.1, 0.1, 1)
                        Rectangle(pos=(cx, cy), size=(CELL, CELL))
                    elif cell == MazeGenerator.END:
                        Color(0.9, 0.7, 0.1, 1)
                        Rectangle(pos=(cx, cy), size=(CELL, CELL))
                        Color(1, 1, 1, 1)
                    elif cell in (MazeGenerator.PATH, MazeGenerator.ANIMAL,
                                   MazeGenerator.START):
                        Color(0.85, 0.80, 0.65, 0.25)
                        Rectangle(pos=(cx, cy), size=(CELL, CELL))

    def _add_dpad(self):
        root = self._root
        dpad_data = [
            ('▲', (0, 1),  {'center_x': 0.5, 'top': 0.22}),
            ('▼', (0, -1), {'center_x': 0.5, 'top': 0.10}),
            ('◀', (-1, 0), {'center_x': 0.35, 'top': 0.16}),
            ('▶', (1, 0),  {'center_x': 0.65, 'top': 0.16}),
        ]
        for symbol, direction, ph in dpad_data:
            btn = Button(
                text=symbol, font_size=dp(26), bold=True,
                background_normal='', background_color=(0.2, 0.6, 0.2, 0.85),
                size_hint=(None, None), size=(dp(54), dp(54)),
                pos_hint=ph
            )
            btn.bind(on_release=self._make_move(direction))
            root.add_widget(btn)

    def _make_move(self, direction):
        def move(*_):
            dx, dy = direction
            nx = self._char_pos[0] + dx
            ny = self._char_pos[1] + dy
            if 0 <= nx < self._maze_w and 0 <= ny < self._maze_h:
                cell = self._grid[ny][nx]
                if cell != MazeGenerator.WALL:
                    self._char_pos = [nx, ny]
                    self._char.move_to(nx, ny, self._maze_origin)
                    self._check_cell(nx, ny, cell)
        return move

    def _check_cell(self, cx, cy, cell):
        if cell == MazeGenerator.END:
            self._level_complete()
        elif cell == MazeGenerator.ANIMAL:
            for animal in self._animals:
                if animal.gx == cx and animal.gy == cy and not animal.defeated:
                    self._pending_animal = animal
                    self._show_question()
                    break

    def _show_question(self):
        app = App.get_running_app()
        level = getattr(app, '_selected_level', 1)
        q = self._qgen.generate(level=level)
        app._pending_question = q
        app._maze_callback = self._on_answer
        self.manager.current = 'game'

    def _on_answer(self, correct: bool):
        self._total += 1
        if correct:
            self._correct += 1
            if self._pending_animal:
                self._pending_animal.defeat()
                self._grid[self._pending_animal.gy][self._pending_animal.gx] = MazeGenerator.PATH
                self._pending_animal = None
        else:
            self._lives -= 1
            if self._lives <= 0:
                self._game_over()
                return
        self._hud_lbl.text = self._hud_text()

    def _hud_text(self):
        lang = getattr(self, '_lang', 'en')
        lives_str = '❤️' * getattr(self, '_lives', 3)
        lvl = getattr(self, '_level', 1)
        score = getattr(self, '_correct', 0)
        return f'{get_text(lang, "level")} {lvl}   {lives_str}   ⭐ {score}'

    def _level_complete(self):
        app = App.get_running_app()
        level = getattr(app, '_selected_level', 1)
        correct = getattr(self, '_correct', 0)
        total = getattr(self, '_total', 1)
        diamonds = RewardSystem.calculate(level, correct, max(total, 1))
        stars = RewardSystem.stars(correct, max(total, 1))
        app.save.complete_level(level, stars)
        app.save.add_diamonds(diamonds)
        # Show completion popup
        lang = getattr(self, '_lang', 'en')
        self._show_popup(
            f'{get_text(lang, "level_complete")}\n'
            f'💎 +{diamonds}  ⭐ {stars}/3',
            on_ok=lambda: setattr(self.manager, 'current', 'level_select')
        )

    def _game_over(self):
        lang = getattr(self, '_lang', 'en')
        self._show_popup(
            '💀 Game Over!',
            on_ok=lambda: self.on_enter()
        )

    def _show_popup(self, message, on_ok=None):
        root = self._root
        overlay = FloatLayout(size_hint=(1, 1), pos_hint={'x': 0, 'y': 0})
        with overlay.canvas.before:
            Color(0, 0, 0, 0.65)
            Rectangle(pos=overlay.pos, size=overlay.size)
        lbl = Label(
            text=f'[b]{message}[/b]', markup=True,
            font_size=dp(22), color=(1, 1, 0.5, 1),
            size_hint=(0.8, None), height=dp(100),
            pos_hint={'center_x': 0.5, 'center_y': 0.58},
            halign='center'
        )
        overlay.add_widget(lbl)
        ok_btn = Button(
            text='OK', font_size=dp(20),
            background_normal='', background_color=(0.2, 0.7, 0.25, 1),
            size_hint=(None, None), size=(dp(110), dp(50)),
            pos_hint={'center_x': 0.5, 'center_y': 0.44}
        )
        def _ok(*_):
            root.remove_widget(overlay)
            if on_ok:
                on_ok()
        ok_btn.bind(on_release=_ok)
        overlay.add_widget(ok_btn)
        root.add_widget(overlay)

    def _on_resize(self, *_):
        root = self._root
        self._bg.pos = root.pos
        self._bg.size = root.size
