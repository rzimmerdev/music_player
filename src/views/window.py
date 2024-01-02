import curses

from .menus import Menu


class Window:
    def __init__(self, stdscr, starting_menu: Menu):
        self.stdscr = stdscr
        self.stdscr.nodelay(1)

        self.previous_menus = []
        self.current_menu = starting_menu

    def render(self):
        self.stdscr.erase()
        self.current_menu.draw(self.stdscr)
        self.stdscr.refresh()

    def go_back(self):
        if len(self.previous_menus) > 0:
            self.current_menu = self.previous_menus.pop()

    def go_to(self, menu):
        self.previous_menus.append(self.current_menu)
        self.current_menu = menu

    def update(self, key):
        if key == curses.KEY_BACKSPACE or key == curses.KEY_LEFT:
            self.go_back()
        else:
            new_menu = self.current_menu.update(key)
            if new_menu is not None:
                self.go_to(new_menu)
