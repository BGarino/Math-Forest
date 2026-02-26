"""
Settings Screen - choose age group, gender, language.
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.app import App
from data.lang import get_text, LANG_NAMES


class ToggleBtn(Button):
    def __init__(self, active=False, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.font_size = dp(15)
        self.size_hint_y = None
        self.height = dp(46)
        self.active = active
        self.bind(pos=self._draw, size=self._draw)
        self._draw()

    def set_active(self, val):
        self.active = val
        self._draw()

    def _draw(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            if self.active:
                Color(0.20, 0.68, 0.25, 1)
            else:
                Color(0.25, 0.25, 0.25, 0.85)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(22)])


class SettingsScreen(Screen):
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
        root = self._root

        # Background
        with root.canvas.before:
            Color(0.08, 0.18, 0.08, 1)
            self._bg = RoundedRectangle(pos=root.pos, size=root.size, radius=[0])
        root.bind(size=lambda *_: setattr(self._bg, 'size', root.size))

        # Title
        root.add_widget(Label(
            text=f'[b]{get_text(lang, "settings")}[/b]',
            markup=True, font_size=dp(26),
            color=(0.9, 1.0, 0.5, 1),
            size_hint=(1, None), height=dp(50),
            pos_hint={'center_x': 0.5, 'top': 0.97}
        ))

        # --- Gender ---
        root.add_widget(Label(
            text=get_text(lang, 'choose_gender'),
            font_size=dp(16), color=(1, 1, 1, 0.9),
            size_hint=(1, None), height=dp(30),
            pos_hint={'center_x': 0.5, 'top': 0.87}
        ))
        gender_box = BoxLayout(size_hint=(0.8, None), height=dp(50),
                               pos_hint={'center_x': 0.5, 'top': 0.82},
                               spacing=dp(10))
        cur_gender = save.get('gender', 'princess')
        self._g_btns = {}
        for g, key in [('prince', 'prince'), ('princess', 'princess')]:
            btn = ToggleBtn(text=f'🤴 {get_text(lang, key)}' if g == 'prince' else f'👸 {get_text(lang, key)}',
                           active=(cur_gender == g))
            btn.bind(on_release=lambda b, gv=g: self._set_gender(gv))
            self._g_btns[g] = btn
            gender_box.add_widget(btn)
        root.add_widget(gender_box)

        # --- Age group ---
        root.add_widget(Label(
            text=get_text(lang, 'choose_age'),
            font_size=dp(16), color=(1, 1, 1, 0.9),
            size_hint=(1, None), height=dp(30),
            pos_hint={'center_x': 0.5, 'top': 0.72}
        ))
        age_box = BoxLayout(size_hint=(0.9, None), height=dp(50),
                            pos_hint={'center_x': 0.5, 'top': 0.67},
                            spacing=dp(6))
        cur_age = save.get('age_group', '8-10')
        self._a_btns = {}
        for ag, key in [('5-7','age_5_7'),('8-10','age_8_10'),
                        ('11-13','age_11_13'),('14+','age_14')]:
            btn = ToggleBtn(text=get_text(lang, key), active=(cur_age == ag),
                           font_size=dp(13))
            btn.bind(on_release=lambda b, av=ag: self._set_age(av))
            self._a_btns[ag] = btn
            age_box.add_widget(btn)
        root.add_widget(age_box)

        # --- Language ---
        root.add_widget(Label(
            text=get_text(lang, 'choose_language'),
            font_size=dp(16), color=(1, 1, 1, 0.9),
            size_hint=(1, None), height=dp(30),
            pos_hint={'center_x': 0.5, 'top': 0.57}
        ))
        cur_lang = lang
        self._l_btns = {}
        langs = [('en','English'),('hu','Magyar'),('es','Español'),
                 ('pt','Português'),('de','Deutsch'),('tl','Tagalog')]
        row1 = BoxLayout(size_hint=(0.9, None), height=dp(46),
                         pos_hint={'center_x': 0.5, 'top': 0.52}, spacing=dp(6))
        row2 = BoxLayout(size_hint=(0.9, None), height=dp(46),
                         pos_hint={'center_x': 0.5, 'top': 0.44}, spacing=dp(6))
        for i, (lc, ln) in enumerate(langs):
            btn = ToggleBtn(text=ln, active=(cur_lang == lc), font_size=dp(13))
            btn.bind(on_release=lambda b, lv=lc: self._set_lang(lv))
            self._l_btns[lc] = btn
            (row1 if i < 3 else row2).add_widget(btn)
        root.add_widget(row1)
        root.add_widget(row2)

        # Save / Back
        save_btn = Button(
            text=get_text(lang, 'save'),
            font_size=dp(18), bold=True,
            background_normal='', background_color=(0.20, 0.68, 0.25, 1),
            size_hint=(0.55, None), height=dp(52),
            pos_hint={'center_x': 0.5, 'top': 0.25}
        )
        save_btn.bind(on_release=self._on_save)
        root.add_widget(save_btn)

        back_btn = Button(
            text=get_text(lang, 'back'),
            font_size=dp(15),
            background_normal='', background_color=(0.4, 0.4, 0.4, 1),
            size_hint=(0.40, None), height=dp(42),
            pos_hint={'center_x': 0.5, 'top': 0.14}
        )
        back_btn.bind(on_release=lambda *_: setattr(self.manager, 'current', 'main_menu'))
        root.add_widget(back_btn)

    def _set_gender(self, val):
        for k, b in self._g_btns.items():
            b.set_active(k == val)
        App.get_running_app().save.set('gender', val)

    def _set_age(self, val):
        for k, b in self._a_btns.items():
            b.set_active(k == val)
        App.get_running_app().save.set('age_group', val)

    def _set_lang(self, val):
        for k, b in self._l_btns.items():
            b.set_active(k == val)
        App.get_running_app().save.set('language', val)

    def _on_save(self, *_):
        App.get_running_app().save.save()
        self.manager.current = 'main_menu'
