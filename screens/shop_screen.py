"""
Shop Screen - buy outfits, accessories, companions with diamonds.
Equipped items are highlighted. Character preview updates live.
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp
from kivy.app import App
from kivy.animation import Animation
from data.lang import get_text
import json, os


CATEGORY_EMOJIS = {
    'outfits': '👗',
    'accessories': '👑',
    'companions': '🦊',
}


class ShopItemCard(Button):
    def __init__(self, item, category, owned, equipped, lang, on_action, **kwargs):
        super().__init__(**kwargs)
        self._item = item
        self._category = category
        self._owned = owned
        self._equipped = equipped
        self._lang = lang
        self._on_action = on_action
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.size_hint = (None, None)
        self.size = (dp(100), dp(120))
        self.bind(pos=self._draw, size=self._draw)
        self.bind(on_release=self._action)

    def _draw(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            if self._equipped:
                Color(0.85, 0.65, 0.10, 1)
            elif self._owned:
                Color(0.20, 0.55, 0.25, 1)
            else:
                Color(0.18, 0.18, 0.28, 1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(14)])

        self.canvas.clear()
        with self.canvas:
            # Item emoji
            pass

        price = self._item.get('price', 0)
        name = self._item.get('name', '')
        if self._equipped:
            sub = get_text(self._lang, 'equipped')
        elif self._owned:
            sub = get_text(self._lang, 'equipped').replace('Equipped', 'Equip')
        else:
            sub = f'💎 {price}'
        self.text = f'{name}\n{sub}'
        self.font_size = dp(12)
        self.halign = 'center'
        self.color = (1, 1, 1, 1)

    def _action(self, *_):
        self._on_action(self._item, self._category)


class ShopScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._root = FloatLayout()
        self.add_widget(self._root)
        self._current_tab = 'outfits'

    def on_enter(self):
        self._root.clear_widgets()
        self._build()

    def _build(self):
        app = App.get_running_app()
        self._app = app
        save = app.save
        self._lang = save.get('language', 'en')
        root = self._root

        with root.canvas.before:
            Color(0.08, 0.06, 0.16, 1)
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(size=lambda *_: setattr(self._bg, 'size', root.size))

        # Title + diamonds
        self._diamond_lbl = Label(
            text=f'[b]{get_text(self._lang, "shop")}[/b]   💎 {save.get("diamonds", 0)}',
            markup=True, font_size=dp(20),
            color=(0.9, 1.0, 0.5, 1),
            size_hint=(1, None), height=dp(44),
            pos_hint={'center_x': 0.5, 'top': 0.99}
        )
        root.add_widget(self._diamond_lbl)

        # Back
        back = Button(
            text=get_text(self._lang, 'back'), font_size=dp(14),
            background_normal='', background_color=(0.3, 0.3, 0.3, 1),
            size_hint=(None, None), size=(dp(80), dp(34)),
            pos_hint={'x': 0.02, 'top': 0.99}
        )
        back.bind(on_release=lambda *_: setattr(self.manager, 'current', 'main_menu'))
        root.add_widget(back)

        # Character preview
        gender = save.get('gender', 'princess')
        self._preview = Label(
            text='👸' if gender == 'princess' else '🤴',
            font_size=dp(56),
            size_hint=(None, None), size=(dp(80), dp(80)),
            pos_hint={'center_x': 0.5, 'top': 0.88}
        )
        root.add_widget(self._preview)

        # Tab buttons
        tab_box = BoxLayout(
            size_hint=(0.95, None), height=dp(42),
            pos_hint={'center_x': 0.5, 'top': 0.73},
            spacing=dp(6)
        )
        for cat in ['outfits', 'accessories', 'companions']:
            btn = Button(
                text=f'{CATEGORY_EMOJIS[cat]} {get_text(self._lang, cat)}',
                font_size=dp(13), bold=True,
                background_normal='', background_color=(
                    (0.25, 0.65, 0.30, 1) if cat == self._current_tab
                    else (0.25, 0.25, 0.35, 1)
                ),
                size_hint=(1, 1)
            )
            btn.bind(on_release=self._make_tab(cat))
            tab_box.add_widget(btn)
        root.add_widget(tab_box)

        # Item grid
        self._scroll_area = FloatLayout(
            size_hint=(1, None),
            height=root.height * 0.56,
            pos_hint={'center_x': 0.5, 'top': 0.68}
        )
        root.add_widget(self._scroll_area)
        self._render_tab()

    def _make_tab(self, cat):
        def switch(*_):
            self._current_tab = cat
            self._root.clear_widgets()
            self._build()
        return switch

    def _render_tab(self):
        area = self._scroll_area
        area.clear_widgets()
        app = self._app
        save = app.save
        cat = self._current_tab

        try:
            path = os.path.join('data', 'shop_items.json')
            with open(path, 'r', encoding='utf-8') as f:
                shop_data = json.load(f)
        except Exception:
            shop_data = {'outfits': [], 'accessories': [], 'companions': []}

        items = shop_data.get(cat, [])
        owned_key = f'owned_{cat}'
        equipped_key = f'equipped_{cat.rstrip("s")}'
        owned = save.get(owned_key, [])
        equipped = save.get(equipped_key, '')

        scroll = ScrollView(size_hint=(1, 1))
        grid = GridLayout(cols=3, spacing=dp(8), padding=dp(10),
                          size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        for item in items:
            card = ShopItemCard(
                item=item,
                category=cat,
                owned=(item['id'] in owned),
                equipped=(item['id'] == equipped),
                lang=self._lang,
                on_action=self._handle_action
            )
            grid.add_widget(card)

        scroll.add_widget(grid)
        area.add_widget(scroll)

    def _handle_action(self, item, category):
        app = self._app
        save = app.save
        item_id = item['id']
        price = item.get('price', 0)
        owned_key = f'owned_{category}'
        cat_single = category.rstrip('s')  # outfits->outfit
        equipped_key = f'equipped_{cat_single}'

        if item_id in save.get(owned_key, []):
            # Equip it
            save.equip_item(item_id, cat_single)
            self._refresh_preview(item_id, category)
            self._render_tab()
        else:
            # Buy
            if save.spend_diamonds(price):
                save.buy_item(item_id, category)
                save.equip_item(item_id, cat_single)
                self._diamond_lbl.text = (
                    f'[b]{get_text(self._lang, "shop")}[/b]   '
                    f'💎 {save.get("diamonds", 0)}'
                )
                self._refresh_preview(item_id, category)
                self._render_tab()
            else:
                self._flash_not_enough()

    def _refresh_preview(self, item_id, category):
        OUTFIT_EMOJIS = {
            'outfit_default': '👸', 'outfit_fairy': '🧚',
            'outfit_knight': '🦸', 'outfit_mage': '🧙',
            'outfit_ninja': '🥷', 'outfit_explorer': '🧕',
            'outfit_royal': '👑', 'outfit_star': '⭐',
        }
        app = self._app
        gender = app.save.get('gender', 'princess')
        base = '👸' if gender == 'princess' else '🤴'
        if category == 'outfits':
            self._preview.text = OUTFIT_EMOJIS.get(item_id, base)

    def _flash_not_enough(self):
        msg = Label(
            text=get_text(self._lang, 'not_enough'),
            font_size=dp(16), color=(1, 0.3, 0.3, 1),
            size_hint=(1, None), height=dp(36),
            pos_hint={'center_x': 0.5, 'top': 0.12}
        )
        self._root.add_widget(msg)
        anim = Animation(opacity=0, duration=1.5)
        anim.bind(on_complete=lambda *_: self._root.remove_widget(msg))
        anim.start(msg)
