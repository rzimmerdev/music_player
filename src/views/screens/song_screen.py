import curses

from src.views.screens.screen import Screen
from ...player import Song
from ...utils import AsciiImage


class SongScreen(Screen):
    def __init__(self, song: Song):
        self.song = song
        self.song_image = AsciiImage(song.thumbnail_path) if song.thumbnail_path is not None else None

    def draw(self, stdscr: curses.window):
        stdscr.addstr(0, 0, str(self.song))
        if self.song_image is not None:
            stdscr.addstr(1, 0, str(self.song_image))
        else:
            stdscr.addstr(1, 0, "No image found\n")

    def update(self, key):
        return None
