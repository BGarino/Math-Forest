"""
Maze Screen - fully rewritten for correct movement, visible player,
proper maze rendering and working D-pad controls.
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import (Color, Rectangle, RoundedRectangle,
                            Ellipse, Line, PushMatrix, PopMatrix,
                            Translate, Rotate)
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.app import App
from kivy.core.window import Window
import random

from logic.maze_gen import MazeGenerator
from logic.question_gen import QuestionGenerator
from logic.reward_system import RewardSystem
from data.lang import get_text
from data.levels_config import get_theme_for_level, get_animals_for_level, diamonds_for_level

# Cell size in pixels
CELL = int(dp(36))

# Theme colours for walls/floors
THEMES = {
    'forest':    {'wall': (0.10, 0.28, 0.10, 1), 'floor': (0.55, 0.75, 0.40, 1), 'bg': (0.05, 0.18, 0.05, 1)},
    'cave':      {'wall': (0.18, 0.15, 0.12, 1), 'floor': (0.40, 0.35, 0.28, 1), 'bg': (0.08, 0.06, 0.04, 1)},
    'clearing':  {'wall': (0.20, 0.50, 0.20, 1), 'floor': (0.80, 0.90, 0.60, 1), 'bg': (0.10, 0.35, 0.10, 1)},
    'night':     {'wall': (0.05, 0.05, 0.20, 1), 'floor': (0.20, 0.20, 0.45, 1), 'bg': (0.02, 0.02, 0.12, 1)},
    'default':   {'wall': (0.15, 0.30, 0.15, 1), 'floor': (0.65, 0.80, 0.50, 1), 'bg': (0.07, 0.20, 0.07, 1)},
}

ANIMAL_EMOJIS = [
    '🦊','🐺','🦌','🐻','🦉','🐰','🐿','🦔',
    '🦝','🦫','🐸','🦋','🐝','🦜','🐧',
]


class MazeScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._root = FloatLayout()
        self.add_widget(self._root)
        self._built = False

    # ------------------------------------------------------------------ #
    #  Lifecycle
    # ------------------------------------------------------------------ #
    def on_enter(self):
        self._root.clear_widgets()
        self._animals = {}          # (gx,gy) -> emoji label
        self._defeated = set()      # (gx,gy) defeated animals
        self._char_gx = 1
        self._char_gy = 1
        self._lives = 3
        self._correct = 0
        self._total = 0
        self._pending_pos = None
        self._answering = False
        Clock.schedule_once(self._build, 0.05)

    # ------------------------------------------------------------------ #
    #  Build
    # ------------------------------------------------------------------ #
    def _build(self, *_):
        app = App.get_running_app()
        save = app.save
        self._lang = save.get('language', 'en')
        self._level = getattr(app, '_selected_level', 1)
        age_group = save.get('age_group', '8-10')
        self._gender = save.get('gender', 'princess')
        companion_id = save.get('equipped_companion', 'comp_none')

        # Theme
        raw_theme = get_theme_for_level(self._level)
        tname = raw_theme.get('name', 'default') if isinstance(raw_theme, dict) else 'default'
        self._theme = THEMES.get(tname, THEMES['default'])

        root = self._root
        W, H = root.width or Window.width, root.height or Window.height

        # Background
        with root.canvas.before:
            Color(*self._theme['bg'])
            self._bg_rect = Rectangle(pos=(0, 0), size=(W, H))
        root.bind(size=self._on_resize, pos=self._on_resize)

        # Generate maze
        gen = MazeGenerator(level=self._level)
        self._grid = gen.generate()
        self._cols = gen.width
        self._rows = gen.height
        self._animal_cells = list(gen.animal_positions)   # list of (gx, gy)
        self._end_pos = gen.end_pos if hasattr(gen, 'end_pos') else (self._cols - 2, self._rows - 2)

        # Question generator
        self._qgen = QuestionGenerator(age_group)

        # Centre the maze
        maze_px_w = self._cols * CELL
        maze_px_h = self._rows * CELL
        self._ox = int((W - maze_px_w) / 2)
        self._oy = int((H - maze_px_h) / 2) + int(dp(20))

        # Draw maze tiles
        self._draw_maze()

        # Place animals
        rng_emojis = ANIMAL_EMOJIS[:]
        random.shuffle(rng_emojis)
        for i, (ax, ay) in enumerate(self._animal_cells):
            emoji = rng_emojis[i % len(rng_emojis)]
            lbl = Label(
                text=emoji,
                font_size=dp(26),
                size_hint=(None, None),
                size=(CELL, CELL),
                pos=(self._ox + ax * CELL, self._oy + ay * CELL),
            )
            self._animals[(ax, ay)] = lbl
            root.add_widget(lbl)

        # Exit marker
        ex, ey = self._end_pos
        exit_lbl = Label(
            text='🚪',
            font_size=dp(26),
            size_hint=(None, None),
            size=(CELL, CELL),
            pos=(self._ox + ex * CELL, self._oy + ey * CELL),
        )
        root.add_widget(exit_lbl)

        # Character sprite
        char_emoji = '👸' if self._gender == 'princess' else '🤴'
        self._char_lbl = Label(
            text=char_emoji,
            font_size=dp(30),
            size_hint=(None, None),
            size=(CELL, CELL),
            pos=(self._ox + self._char_gx * CELL,
                 self._oy + self._char_gy * CELL),
        )
        root.add_widget(self._char_lbl)

        # Companion (bottom-right corner)
        COMPANION_MAP = {
            'comp_fox': '🦊', 'comp_owl': '🦉', 'comp_bunny': '🐰',
            'comp_dragon': '🐉', 'comp_cat': '🐱', 'comp_fairy': '🧚',
            'comp_wolf': '🐺',
        }
        if companion_id in COMPANION_MAP:
            root.add_widget(Label(
                text=COMPANION_MAP[companion_id],
                font_size=dp(28),
                size_hint=(None, None), size=(dp(44), dp(44)),
                pos=(W - dp(50), dp(10)),
            ))

        # HUD bar
        self._hud_lbl = Label(
            text=self._hud_text(),
            font_size=dp(15),
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(W - dp(20), dp(36)),
            pos=(dp(10), H - dp(40)),
            halign='center',
            valign='middle',
        )
        self._hud_lbl.bind(size=lambda w, s: setattr(w, 'text_size', s))
        root.add_widget(self._hud_lbl)

        # Back button
        back_btn = Button(
            text='🏠 ' + get_text(self._lang, 'home'),
            font_size=dp(13),
            background_normal='',
            background_color=(0.25, 0.25, 0.25, 0.92),
            size_hint=(None, None), size=(dp(90), dp(34)),
            pos=(dp(6), H - dp(40)),
        )
        back_btn.bind(on_release=lambda *_: setattr(self.manager, 'current', 'main_menu'))
        root.add_widget(back_btn)

        # D-pad
        self._add_dpad(W, H)

    # ------------------------------------------------------------------ #
    #  Maze drawing
    # ------------------------------------------------------------------ #
    def _draw_maze(self):
        root = self._root
        wall_c = self._theme['wall']
        floor_c = self._theme['floor']
        ex, ey = self._end_pos
        with root.canvas:
            for row in range(self._rows):
                for col in range(self._cols):
                    cx = self._ox + col * CELL
                    cy = self._oy + row * CELL
                    val = self._grid[row][col]
                    if val == MazeGenerator.WALL:
                        Color(*wall_c)
                        Rectangle(pos=(cx + 1, cy + 1),
                                  size=(CELL - 2, CELL - 2))
                    else:
                        Color(*floor_c)
                        Rectangle(pos=(cx + 1, cy + 1),
                                  size=(CELL - 2, CELL - 2))
            # Highlight exit cell
            Color(1.0, 0.85, 0.0, 0.55)
            Rectangle(pos=(self._ox + ex * CELL + 1,
                           self._oy + ey * CELL + 1),
                      size=(CELL - 2, CELL - 2))

    # ------------------------------------------------------------------ #
    #  D-pad
    # ------------------------------------------------------------------ #
    def _add_dpad(self, W, H):
        root = self._root
        pad_cx = W / 2
        pad_cy = int(dp(70))
        step = int(dp(58))

        directions = [
            ('▲', ( 0,  1), (pad_cx,          pad_cy + step)),
            ('▼', ( 0, -1), (pad_cx,          pad_cy - step)),
            ('◀', (-1,  0), (pad_cx - step,   pad_cy)),
            ('▶', ( 1,  0), (pad_cx + step,   pad_cy)),
        ]
        for symbol, (dx, dy), (bx, by) in directions:
            btn = Button(
                text=symbol,
                font_size=dp(28),
                bold=True,
                background_normal='',
                background_color=(0.18, 0.55, 0.18, 0.90),
                size_hint=(None, None),
                size=(int(dp(52)), int(dp(52))),
                pos=(int(bx - dp(26)), int(by - dp(26))),
            )
            btn.bind(on_release=self._make_move(dx, dy))
            root.add_widget(btn)

    # ------------------------------------------------------------------ #
    #  Movement
    # ------------------------------------------------------------------ #
    def _make_move(self, dx, dy):
        def _move(*_):
            if self._answering:
                return
            nx = self._char_gx + dx
            ny = self._char_gy + dy
            # Bounds check
            if not (0 <= nx < self._cols and 0 <= ny < self._rows):
                return
            # Wall check  (grid is [row][col] = [y][x])
            if self._grid[ny][nx] == MazeGenerator.WALL:
                return
            # Move accepted
            self._char_gx = nx
            self._char_gy = ny
            # Animate character label
            target_x = self._ox + nx * CELL
            target_y = self._oy + ny * CELL
            Animation(x=target_x, y=target_y, duration=0.15).start(self._char_lbl)
            # Check what we landed on
            self._check_cell(nx, ny)
        return _move

    def _check_cell(self, gx, gy):
        ex, ey = self._end_pos
        if (gx, gy) == (ex, ey):
            Clock.schedule_once(lambda *_: self._level_complete(), 0.2)
        elif (gx, gy) in self._animals and (gx, gy) not in self._defeated:
            self._answering = True
            self._pending_pos = (gx, gy)
            Clock.schedule_once(lambda *_: self._show_question(), 0.25)

    # ------------------------------------------------------------------ #
    #  Question flow
    # ------------------------------------------------------------------ #
    def _show_question(self):
        app = App.get_running_app()
        q = self._qgen.generate(level=self._level)
        app._pending_question = q
        app._pending_animal_emoji = self._animals.get(
            self._pending_pos, Label(text='🐾')).text
        app._maze_callback = self._on_answer
        self.manager.current = 'game'

    def _on_answer(self, correct: bool):
        self._answering = False
        self._total += 1
        if correct:
            self._correct += 1
            pos = self._pending_pos
            if pos and pos in self._animals:
                lbl = self._animals.pop(pos)
                self._defeated.add(pos)
                anim = Animation(font_size=dp(40), opacity=0, duration=0.45)
                anim.bind(on_complete=lambda *_:
                          self._root.remove_widget(lbl) if lbl.parent else None)
                anim.start(lbl)
                # Clear animal cell in grid
                gx, gy = pos
                self._grid[gy][gx] = MazeGenerator.PATH
            self._pending_pos = None
        else:
            self._lives -= 1
            self._hud_lbl.text = self._hud_text()
            if self._lives <= 0:
                Clock.schedule_once(lambda *_: self._game_over(), 0.1)
                return
        self._hud_lbl.text = self._hud_text()

    # ------------------------------------------------------------------ #
    #  HUD
    # ------------------------------------------------------------------ #
    def _hud_text(self):
        lives_str = '❤️' * self._lives + '🖤' * (3 - self._lives)
        return (f'  {get_text(self._lang, "level")} {self._level}   '
                f'{lives_str}   ⭐ {self._correct}/{max(self._total,1)}  ')

    # ------------------------------------------------------------------ #
    #  Level complete / game over
    # ------------------------------------------------------------------ #
    def _level_complete(self):
        app = App.get_running_app()
        diamonds = RewardSystem.calculate(self._level, self._correct,
                                          max(self._total, 1))
        stars = RewardSystem.stars(self._correct, max(self._total, 1))
        app.save.complete_level(self._level, stars)
        app.save.add_diamonds(diamonds)
        self._show_popup(
            f'🎉 {get_text(self._lang, "level_complete")}\n'
            f'💎 +{diamonds}   ⭐ {stars}/3',
            ok_label='OK',
            on_ok=lambda: setattr(self.manager, 'current', 'level_select'),
        )

    def _game_over(self):
        self._show_popup(
            '💀 Game Over!\n' + get_text(self._lang, 'try_again'),
            ok_label=get_text(self._lang, 'retry'),
            on_ok=self.on_enter,
        )

    # ------------------------------------------------------------------ #
    #  Popup
    # ------------------------------------------------------------------ #
    def _show_popup(self, message, ok_label='OK', on_ok=None):
        root = self._root
        W = root.width or Window.width
        H = root.height or Window.height

        overlay = FloatLayout(size=(W, H), pos=(0, 0), size_hint=(None, None))
        with overlay.canvas.before:
            Color(0, 0, 0, 0.70)
            Rectangle(pos=(0, 0), size=(W, H))

        box_w, box_h = int(dp(280)), int(dp(170))
        box_x = int((W - box_w) / 2)
        box_y = int((H - box_h) / 2)
        with overlay.canvas:
            Color(0.12, 0.30, 0.12, 1)
            RoundedRectangle(pos=(box_x, box_y), size=(box_w, box_h),
                             radius=[dp(18)])

        lbl = Label(
            text=f'[b]{message}[/b]', markup=True,
            font_size=dp(20), color=(1, 1, 0.6, 1),
            size_hint=(None, None), size=(box_w - dp(20), dp(90)),
            pos=(box_x + dp(10), box_y + dp(70)),
            halign='center', valign='middle',
        )
        lbl.bind(size=lambda w, s: setattr(w, 'text_size', s))
        overlay.add_widget(lbl)

        ok_btn = Button(
            text=ok_label, font_size=dp(18), bold=True,
            background_normal='', background_color=(0.18, 0.68, 0.22, 1),
            size_hint=(None, None), size=(int(dp(120)), int(dp(46))),
            pos=(int(W / 2 - dp(60)), box_y + int(dp(12))),
        )
        def _ok(*_):
            root.remove_widget(overlay)
            if on_ok:
                on_ok()
        ok_btn.bind(on_release=_ok)
        overlay.add_widget(ok_btn)
        root.add_widget(overlay)

    # ------------------------------------------------------------------ #
    #  Resize
    # ------------------------------------------------------------------ #
    def _on_resize(self, *_):
        root = self._root
        self._bg_rect.size = root.size
        self._bg_rect.pos = root.pos
