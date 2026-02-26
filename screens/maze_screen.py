"""
Maze Screen - canvas-drawn sprites (no emoji), fixed movement bug,
map does NOT end after first animal defeat.
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import (Color, Rectangle, RoundedRectangle,
                            Ellipse, Line, Triangle)
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.app import App
import random

from logic.maze_gen import MazeGenerator
from logic.question_gen import QuestionGenerator
from logic.reward_system import RewardSystem
from data.lang import get_text
from data.levels_config import get_theme_for_level, diamonds_for_level

CELL = int(dp(36))

THEMES = {
    'forest':   {'wall': (0.08, 0.24, 0.08, 1), 'floor': (0.50, 0.72, 0.36, 1), 'bg': (0.04, 0.15, 0.04, 1)},
    'cave':     {'wall': (0.18, 0.14, 0.10, 1), 'floor': (0.42, 0.36, 0.28, 1), 'bg': (0.08, 0.06, 0.04, 1)},
    'clearing': {'wall': (0.18, 0.48, 0.18, 1), 'floor': (0.78, 0.90, 0.58, 1), 'bg': (0.10, 0.32, 0.10, 1)},
    'night':    {'wall': (0.05, 0.05, 0.20, 1), 'floor': (0.22, 0.22, 0.46, 1), 'bg': (0.02, 0.02, 0.12, 1)},
    'default':  {'wall': (0.12, 0.28, 0.12, 1), 'floor': (0.60, 0.78, 0.46, 1), 'bg': (0.06, 0.18, 0.06, 1)},
}

# Animal shape colours (cycling)
ANIMAL_COLORS = [
    (0.90, 0.40, 0.10, 1),  # orange fox
    (0.60, 0.20, 0.70, 1),  # purple
    (0.15, 0.55, 0.85, 1),  # blue
    (0.85, 0.70, 0.10, 1),  # yellow
    (0.20, 0.72, 0.40, 1),  # green
    (0.85, 0.20, 0.30, 1),  # red
]
ANIMAL_LETTERS = ['F', 'W', 'B', 'O', 'R', 'D', 'C', 'S', 'L', 'G']


# ── Canvas-drawn player sprite ────────────────────────────────────────────
class PlayerWidget(Widget):
    def __init__(self, gender='princess', **kwargs):
        super().__init__(**kwargs)
        self.gender = gender
        self.size_hint = (None, None)
        self.size = (CELL, CELL)
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *_):
        self.canvas.clear()
        x, y = int(self.x), int(self.y)
        cx = x + CELL // 2
        pad = int(dp(3))
        with self.canvas:
            # Body
            if self.gender == 'princess':
                Color(0.95, 0.50, 0.75, 1)
            else:
                Color(0.30, 0.50, 0.95, 1)
            RoundedRectangle(
                pos=(cx - int(dp(7)), y + pad),
                size=(int(dp(14)), int(dp(16))),
                radius=[int(dp(3))]
            )
            # Head
            Color(0.98, 0.84, 0.68, 1)
            Ellipse(
                pos=(cx - int(dp(7)), y + int(dp(17))),
                size=(int(dp(14)), int(dp(14)))
            )
            # Hair/crown
            if self.gender == 'princess':
                Color(1.0, 0.80, 0.10, 1)
                RoundedRectangle(
                    pos=(cx - int(dp(7)), y + int(dp(29))),
                    size=(int(dp(14)), int(dp(5))),
                    radius=[int(dp(2))]
                )
            else:
                Color(0.35, 0.20, 0.08, 1)
                RoundedRectangle(
                    pos=(cx - int(dp(7)), y + int(dp(28))),
                    size=(int(dp(14)), int(dp(6))),
                    radius=[int(dp(2))]
                )
            # Eyes
            Color(0.05, 0.05, 0.05, 1)
            Ellipse(pos=(cx - int(dp(4)), y + int(dp(21))), size=(int(dp(3)), int(dp(3))))
            Ellipse(pos=(cx + int(dp(1)), y + int(dp(21))), size=(int(dp(3)), int(dp(3))))

    def move_to(self, px, py):
        Animation(x=px, y=py, duration=0.15).start(self)


# ── Canvas-drawn animal sprite ────────────────────────────────────────────
class AnimalWidget(Widget):
    def __init__(self, gx, gy, color, letter, ox, oy, **kwargs):
        super().__init__(**kwargs)
        self.gx = gx
        self.gy = gy
        self._color = color
        self._letter = letter
        self.size_hint = (None, None)
        self.size = (CELL, CELL)
        self.pos = (ox + gx * CELL, oy + gy * CELL)
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *_):
        self.canvas.clear()
        x, y = int(self.x), int(self.y)
        pad = int(dp(3))
        cx = x + CELL // 2
        cy = y + CELL // 2
        r = CELL // 2 - pad
        with self.canvas:
            # Circle body
            Color(*self._color)
            Ellipse(pos=(x + pad, y + pad), size=(CELL - pad * 2, CELL - pad * 2))
            # Ears (two small circles top)
            Color(*self._color)
            ear_r = int(dp(4))
            Ellipse(pos=(cx - r + int(dp(2)), cy + r - int(dp(2))), size=(ear_r * 2, ear_r * 2))
            Ellipse(pos=(cx + r - ear_r * 2 - int(dp(2)), cy + r - int(dp(2))), size=(ear_r * 2, ear_r * 2))
            # Letter label on body
            Color(1, 1, 1, 1)

    def add_letter_label(self, parent):
        """Add a text label on top (canvas can't render text)."""
        self._lbl = Label(
            text=self._letter,
            font_size=dp(14),
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(CELL, CELL),
            pos=self.pos,
        )
        self.bind(pos=lambda *_: setattr(self._lbl, 'pos', self.pos))
        parent.add_widget(self._lbl)
        return self._lbl

    def defeat_anim(self, root):
        """Animate defeat and remove from parent."""
        anim = Animation(size=(CELL * 2, CELL * 2),
                         pos=(self.x - CELL // 2, self.y - CELL // 2),
                         opacity=0, duration=0.4)
        def _remove(*_):
            if self.parent:
                self.parent.remove_widget(self)
            if hasattr(self, '_lbl') and self._lbl.parent:
                self._lbl.parent.remove_widget(self._lbl)
        anim.bind(on_complete=_remove)
        anim.start(self)


# ── Exit gate drawn on canvas ─────────────────────────────────────────────
class ExitWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (CELL, CELL)
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *_):
        self.canvas.clear()
        x, y = int(self.x), int(self.y)
        pad = int(dp(2))
        with self.canvas:
            # Gold background
            Color(1.0, 0.82, 0.0, 1)
            RoundedRectangle(pos=(x + pad, y + pad),
                             size=(CELL - pad * 2, CELL - pad * 2),
                             radius=[int(dp(4))])
            # Door frame
            Color(0.6, 0.35, 0.05, 1)
            door_w = int(dp(10))
            door_h = int(dp(18))
            Line(rectangle=(x + CELL // 2 - door_w // 2,
                             y + pad + int(dp(2)),
                             door_w, door_h), width=dp(1.5))
            # Arrow pointing right
            Color(0.15, 0.15, 0.15, 1)
            mx = x + CELL // 2
            my = y + pad + int(dp(22))
            Line(points=[mx - int(dp(4)), my, mx + int(dp(4)), my], width=dp(1.5))
            Line(points=[mx + int(dp(1)), my - int(dp(3)),
                         mx + int(dp(4)), my,
                         mx + int(dp(1)), my + int(dp(3))], width=dp(1.5))


# ── Main screen ───────────────────────────────────────────────────────────
class MazeScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._root = FloatLayout()
        self.add_widget(self._root)

    def on_enter(self):
        self._root.clear_widgets()
        self._animals = {}       # (gx,gy) -> AnimalWidget
        self._defeated = set()   # set of (gx,gy)
        self._char_gx = 1
        self._char_gy = 1
        self._lives = 3
        self._correct = 0
        self._total = 0
        self._pending_pos = None
        self._answering = False
        Clock.schedule_once(self._build, 0.05)

    # ── Build ─────────────────────────────────────────────────────────────
    def _build(self, *_):
        app = App.get_running_app()
        save = app.save
        self._lang = save.get('language', 'en')
        self._level = getattr(app, '_selected_level', 1)
        age_group = save.get('age_group', '8-10')
        self._gender = save.get('gender', 'princess')
        companion_id = save.get('equipped_companion', 'comp_none')

        raw_theme = get_theme_for_level(self._level)
        tname = raw_theme.get('name', 'default') if isinstance(raw_theme, dict) else 'default'
        self._theme = THEMES.get(tname, THEMES['default'])

        root = self._root
        W = root.width or Window.width
        H = root.height or Window.height

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
        self._animal_cells = list(gen.animal_positions)
        self._end_pos = gen.end_pos

        self._qgen = QuestionGenerator(age_group)

        # Centre maze
        maze_px_w = self._cols * CELL
        maze_px_h = self._rows * CELL
        self._ox = int((W - maze_px_w) / 2)
        self._oy = int((H - maze_px_h) / 2) + int(dp(24))

        # Draw tiles
        self._draw_maze()

        # Exit widget
        ex, ey = self._end_pos
        exit_w = ExitWidget(pos=(self._ox + ex * CELL, self._oy + ey * CELL))
        root.add_widget(exit_w)

        # Animal widgets
        color_cycle = ANIMAL_COLORS * 4
        letter_cycle = ANIMAL_LETTERS * 4
        random.shuffle(color_cycle)
        for i, (ax, ay) in enumerate(self._animal_cells):
            aw = AnimalWidget(
                gx=ax, gy=ay,
                color=color_cycle[i % len(color_cycle)],
                letter=letter_cycle[i % len(letter_cycle)],
                ox=self._ox, oy=self._oy,
            )
            lbl = aw.add_letter_label(root)
            self._animals[(ax, ay)] = (aw, lbl)
            root.add_widget(aw)

        # Player
        self._player = PlayerWidget(
            gender=self._gender,
            pos=(self._ox + self._char_gx * CELL,
                 self._oy + self._char_gy * CELL),
        )
        root.add_widget(self._player)

        # HUD
        self._hud_lbl = Label(
            text=self._hud_text(),
            font_size=dp(15),
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(int(W - dp(100)), int(dp(34))),
            pos=(int(dp(100)), int(H - dp(36))),
            halign='center', valign='middle',
        )
        self._hud_lbl.bind(size=lambda w, s: setattr(w, 'text_size', s))
        root.add_widget(self._hud_lbl)

        # Back button
        back_btn = Button(
            text='< ' + get_text(self._lang, 'home'),
            font_size=dp(13),
            background_normal='',
            background_color=(0.25, 0.25, 0.25, 0.92),
            size_hint=(None, None), size=(int(dp(90)), int(dp(34))),
            pos=(int(dp(4)), int(H - dp(38))),
        )
        back_btn.bind(on_release=lambda *_: setattr(self.manager, 'current', 'main_menu'))
        root.add_widget(back_btn)

        # D-pad
        self._add_dpad(W, H)

    # ── Maze tiles ────────────────────────────────────────────────────────
    def _draw_maze(self):
        root = self._root
        wc = self._theme['wall']
        fc = self._theme['floor']
        with root.canvas:
            for row in range(self._rows):
                for col in range(self._cols):
                    cx = self._ox + col * CELL
                    cy = self._oy + row * CELL
                    val = self._grid[row][col]
                    if val == MazeGenerator.WALL:
                        Color(*wc)
                    else:
                        Color(*fc)
                    Rectangle(pos=(cx + 1, cy + 1), size=(CELL - 2, CELL - 2))

    # ── D-pad ─────────────────────────────────────────────────────────────
    def _add_dpad(self, W, H):
        root = self._root
        cx = int(W / 2)
        cy = int(dp(68))
        step = int(dp(58))
        dirs = [
            ('  ^  ', ( 0,  1), (cx,        cy + step)),
            ('  v  ', ( 0, -1), (cx,        cy - step)),
            (' <  ', (-1,  0), (cx - step, cy)),
            ('  > ', ( 1,  0), (cx + step, cy)),
        ]
        for txt, (dx, dy), (bx, by) in dirs:
            btn = Button(
                text=txt, font_size=dp(22), bold=True,
                background_normal='',
                background_color=(0.16, 0.52, 0.16, 0.92),
                size_hint=(None, None),
                size=(int(dp(52)), int(dp(52))),
                pos=(int(bx - dp(26)), int(by - dp(26))),
            )
            btn.bind(on_release=self._make_move(dx, dy))
            root.add_widget(btn)

    # ── Movement ──────────────────────────────────────────────────────────
    def _make_move(self, dx, dy):
        def _move(*_):
            if self._answering:
                return
            nx = self._char_gx + dx
            ny = self._char_gy + dy
            if not (0 <= nx < self._cols and 0 <= ny < self._rows):
                return
            if self._grid[ny][nx] == MazeGenerator.WALL:
                return
            self._char_gx = nx
            self._char_gy = ny
            self._player.move_to(
                self._ox + nx * CELL,
                self._oy + ny * CELL,
            )
            self._check_cell(nx, ny)
        return _move

    def _check_cell(self, gx, gy):
        ex, ey = self._end_pos
        if (gx, gy) == (ex, ey):
            # Only complete if all animals defeated OR player reached exit
            Clock.schedule_once(lambda *_: self._level_complete(), 0.25)
        elif (gx, gy) in self._animals and (gx, gy) not in self._defeated:
            self._answering = True
            self._pending_pos = (gx, gy)
            Clock.schedule_once(lambda *_: self._show_question(), 0.20)

    # ── Question ──────────────────────────────────────────────────────────
    def _show_question(self):
        app = App.get_running_app()
        q = self._qgen.generate(level=self._level)
        app._pending_question = q
        # Pass the letter of the animal as "emoji"
        pos = self._pending_pos
        if pos and pos in self._animals:
            aw, _ = self._animals[pos]
            app._pending_animal_emoji = aw._letter
        else:
            app._pending_animal_emoji = '?'
        app._maze_callback = self._on_answer
        self.manager.current = 'game'

    def _on_answer(self, correct: bool):
        # IMPORTANT: always reset _answering so player can move again
        self._answering = False
        self._total += 1

        if correct:
            self._correct += 1
            pos = self._pending_pos
            self._pending_pos = None
            if pos and pos in self._animals:
                aw, lbl = self._animals.pop(pos)
                self._defeated.add(pos)
                # Clear grid cell so player can walk through
                gx, gy = pos
                self._grid[gy][gx] = MazeGenerator.PATH
                # Remove letter label
                if lbl.parent:
                    lbl.parent.remove_widget(lbl)
                # Animate animal out
                aw.defeat_anim(self._root)
        else:
            self._pending_pos = None
            self._lives -= 1
            if self._lives <= 0:
                Clock.schedule_once(lambda *_: self._game_over(), 0.1)
                return

        self._hud_lbl.text = self._hud_text()

    # ── HUD ───────────────────────────────────────────────────────────────
    def _hud_text(self):
        hearts = 'v' * self._lives + '.' * (3 - self._lives)
        return (f'{get_text(self._lang, "level")} {self._level}  '
                f'[{hearts}]  * {self._correct}/{max(self._total, 1)}')

    # ── Level complete ────────────────────────────────────────────────────
    def _level_complete(self):
        app = App.get_running_app()
        diamonds = RewardSystem.calculate(
            self._level, self._correct, max(self._total, 1))
        stars = RewardSystem.stars(self._correct, max(self._total, 1))
        app.save.complete_level(self._level, stars)
        app.save.add_diamonds(diamonds)
        self._show_popup(
            f'LEVEL COMPLETE!\n<> +{diamonds}   * {stars}/3',
            ok_label='OK',
            on_ok=lambda: setattr(self.manager, 'current', 'level_select'),
        )

    # ── Game over ─────────────────────────────────────────────────────────
    def _game_over(self):
        self._show_popup(
            'GAME OVER\n' + get_text(self._lang, 'try_again'),
            ok_label=get_text(self._lang, 'retry'),
            on_ok=self.on_enter,
        )

    # ── Popup ─────────────────────────────────────────────────────────────
    def _show_popup(self, message, ok_label='OK', on_ok=None):
        root = self._root
        W = root.width or Window.width
        H = root.height or Window.height
        overlay = FloatLayout(size=(W, H), pos=(0, 0), size_hint=(None, None))
        with overlay.canvas.before:
            Color(0, 0, 0, 0.68)
            Rectangle(pos=(0, 0), size=(W, H))
        bw, bh = int(dp(280)), int(dp(180))
        bx = int((W - bw) / 2)
        by = int((H - bh) / 2)
        with overlay.canvas:
            Color(0.10, 0.28, 0.10, 1)
            RoundedRectangle(pos=(bx, by), size=(bw, bh), radius=[dp(18)])
        lbl = Label(
            text=f'[b]{message}[/b]', markup=True,
            font_size=dp(19), color=(1, 1, 0.55, 1),
            size_hint=(None, None), size=(bw - int(dp(20)), int(dp(90))),
            pos=(bx + int(dp(10)), by + int(dp(76))),
            halign='center', valign='middle',
        )
        lbl.bind(size=lambda w, s: setattr(w, 'text_size', s))
        overlay.add_widget(lbl)
        ok_btn = Button(
            text=ok_label, font_size=dp(18), bold=True,
            background_normal='', background_color=(0.16, 0.65, 0.20, 1),
            size_hint=(None, None), size=(int(dp(120)), int(dp(46))),
            pos=(int(W / 2 - dp(60)), by + int(dp(14))),
        )
        def _ok(*_):
            root.remove_widget(overlay)
            if on_ok:
                on_ok()
        ok_btn.bind(on_release=_ok)
        overlay.add_widget(ok_btn)
        root.add_widget(overlay)

    # ── Resize ────────────────────────────────────────────────────────────
    def _on_resize(self, *_):
        root = self._root
        self._bg_rect.size = root.size
        self._bg_rect.pos = root.pos
