from .screen import Screen
from ..player import Player


class Window:
    def __init__(self, stdscr, starting_screen: Screen = None):
        self.stdscr = stdscr
        self.stdscr.nodelay(1)

        self.previous_menus = []
        self.screen = starting_screen
        self.size = self.stdscr.getmaxyx()
        self.player = Player()

    def render(self):
        self.stdscr.erase()
        self.screen.draw(self.stdscr)
        self.stdscr.refresh()

    def tick(self, key):
        self.size = self.stdscr.getmaxyx()
        self.screen = self.screen.tick(key)

    @property
    def alive(self):
        return self.screen is not None
