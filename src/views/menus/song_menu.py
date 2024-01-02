import curses

from src.views.menus.menu import Menu
from ..screens.song_screen import SongScreen


class SongMenu(Menu):
    def __init__(self, song):
        super().__init__(song.title, ["Play", "Add to queue", "Add to playlist"], 0)
        self.song_screen = SongScreen(song)
        self.draw_content = self.song_screen.draw

    def update(self, key):
        if key == ord('\n') or key == curses.KEY_RIGHT:
            pass
        else:
            return super().update(key)
