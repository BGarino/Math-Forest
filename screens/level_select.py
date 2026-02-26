"""
Level Select Screen - shows 300 levels grouped by theme (30 each).
Locked levels are shown as grayed out.
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.app import App
from data.lang import get_text
from data.levels_config import THEMES, get_theme_for_level


class LevelBtn(Button):
    def __init__(self, level_num, unlocked, completed, **kwargs):
        super().__init__(**kwargs)
        self.level_num = level_num
        self.unlocked = unlocked
        self.completed = completed
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.font_size = dp(14)
        self.bold = True
        self.text = str(level_num)
        self.color = (1, 1, 1, 1) if unlocked else (0.5, 0.5, 0.5, 1)
        if completed:
            self.text = f'★\n{level_num}'
        elif not unlocked:
            self.text = f'🔒\n{level_num}'
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            if self.completed:
                Color(0.85, 0.65, 0.10, 1)
            elif self.unlocked:
                Color(0.20, 0.60, 0.25, 1)
            else:
                Color(0.20, 0.20, 0.20, 0.7)
            RoundedRectangle(pos=(self.x + dp(2), self.y + dp(2)),
                             size=(self.width - dp(4), self.height - dp(4)),
                             radius=[dp(10)])


class LevelSelectScreen(Screen):
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
        unlocked = save.get('unlocked_levels', [1])
        completed = save.get('completed_levels', [])
        root = self._root

        with root.canvas.before:
            Color(0.06, 0.16, 0.06, 1)
            self._bg = RoundedRectangle(pos=root.pos, size=root.size, radius=[0])
        root.bind(size=lambda *_: setattr(self._bg, 'size', root.size))

        # Title
        root.add_widget(Label(
            text=f'[b]{get_text(lang, "level")} {get_text(lang, "play")}[/b]',
            markup=True, font_size=dp(22),
            color=(0.9, 1.0, 0.5, 1),
            size_hint=(1, None), height=dp(44),
            pos_hint={'center_x': 0.5, 'top': 0.99}
        ))

        # Back button
        back = Button(
            text=get_text(lang, 'back'),
            font_size=dp(14),
            background_normal='', background_color=(0.35, 0.35, 0.35, 1),
            size_hint=(None, None), size=(dp(80), dp(36)),
            pos_hint={'x': 0.02, 'top': 0.99}
        )
        back.bind(on_release=lambda *_: setattr(self.manager, 'current', 'main_menu'))
        root.add_widget(back)

        # Scrollable grid
        scroll = ScrollView(
            size_hint=(1, None),
            height=root.height * 0.88,
            pos_hint={'center_x': 0.5, 'top': 0.90}
        )
        grid = GridLayout(cols=5, spacing=dp(6), padding=dp(8),
                          size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        current_theme_id = None
        for lvl in range(1, 301):
            theme = get_theme_for_level(lvl)
            if theme['id'] != current_theme_id:
                current_theme_id = theme['id']
                # Theme header
                hdr = Label(
                    text=f'[b]{get_text(lang, theme["name_key"])}[/b]',
                    markup=True,
                    font_size=dp(13),
                    color=(0.9, 0.85, 0.3, 1),
                    size_hint_y=None, height=dp(30)
                )
                # Span full row
                hdr_wrapper = GridLayout(cols=1, size_hint_y=None, height=dp(30))
                hdr_wrapper.add_widget(hdr)
                # Trick: add 5 cells for the header row
                for ci in range(5):
                    if ci == 0:
                        grid.add_widget(Label(
                            text=f'[b]{get_text(lang, theme["name_key"])}[/b]',
                            markup=True, font_size=dp(12),
                            color=(1, 0.85, 0.2, 1),
                            size_hint_y=None, height=dp(28)
                        ))
                    else:
                        grid.add_widget(Label(
                            text='', size_hint_y=None, height=dp(28)
                        ))

            btn = LevelBtn(
                level_num=lvl,
                unlocked=(lvl in unlocked),
                completed=(lvl in completed),
                size_hint_y=None, height=dp(54)
            )
            if lvl in unlocked:
                btn.bind(on_release=self._make_go(lvl))
            grid.add_widget(btn)

        scroll.add_widget(grid)
        root.add_widget(scroll)

    def _make_go(self, level_num):
        def go(*_):
            app = App.get_running_app()
            app._selected_level = level_num
            self.manager.current = 'maze'
        return go
