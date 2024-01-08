import curses

from .menu import Menu
from ..components import Header, Footer


class HomeMenu(Menu):
    def __init__(self):
        super().__init__("Main menu", ["Songs", "Playlists", "Search", "Settings"], 0)

    def draw(self, stdscr: curses.window):
        super().draw(stdscr)


class ContentMenu(Menu):
    def __init__(self):
        super().__init__()
        self.header = Header("Zimbafy!\n")
        self.current_menu = HomeMenu()
        self.footer = Footer()

    def draw(self, stdscr: curses.window):
        self.header.draw(stdscr)
        self.current_menu.draw(stdscr)
        # self.footer.draw(stdscr)

    def update(self, key):
        new_menu = self.current_menu.update(key)
        if new_menu is not None:
            self.current_menu = new_menu
        return None
