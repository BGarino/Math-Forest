"""Math-Forest – Main entry point"""
import os
os.environ.setdefault('KIVY_NO_ENV_CONFIG', '1')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.utils import platform

from screens.main_menu import MainMenuScreen
from screens.settings_screen import SettingsScreen
from screens.game_screen import GameScreen
from screens.maze_screen import MazeScreen
from screens.card_screen import CardScreen
from screens.shop_screen import ShopScreen
from screens.level_select import LevelSelectScreen
from logic.save_system import SaveSystem

if platform in ('win', 'linux', 'macosx'):
    Window.size = (400, 720)


class MathForestApp(App):
    title = 'Math-Forest'
    icon = 'assets/images/icon.png'

    def build(self):
        self.save = SaveSystem()
        self.save.load()

        self.sm = ScreenManager(transition=FadeTransition(duration=0.4))
        self.sm.add_widget(MainMenuScreen(name='main_menu'))
        self.sm.add_widget(SettingsScreen(name='settings'))
        self.sm.add_widget(LevelSelectScreen(name='level_select'))
        self.sm.add_widget(GameScreen(name='game'))
        self.sm.add_widget(MazeScreen(name='maze'))
        self.sm.add_widget(CardScreen(name='cards'))
        self.sm.add_widget(ShopScreen(name='shop'))

        self._load_bg_music()
        return self.sm

    def _load_bg_music(self):
        try:
            sound = SoundLoader.load('assets/sounds/menu_music.ogg')
            if sound:
                sound.loop = True
                sound.volume = 0.5
                sound.play()
        except Exception:
            pass

    def on_pause(self):
        return True

    def on_resume(self):
        pass

    def on_stop(self):
        self.save.save()


if __name__ == '__main__':
    MathForestApp().run()
