import curses
from typing import Callable

from src.views.screens.screen import Screen


class Menu(Screen):
    def __init__(self, title, options, selected_option):
        self.title = title
        self.options = options
        self.selected_option = selected_option
        self.draw_content: None or Callable = None

    def draw(self, stdscr: curses.window):
        stdscr.addstr(0, 0, self.title)

        if self.draw_content is not None:
            self.draw_content(stdscr)

        for index, option in enumerate(self.options):
            if index == self.selected_option:
                stdscr.addstr(f"-> {option}\n", curses.A_REVERSE)
            else:
                stdscr.addstr(f"   {option}\n")

    def update(self, key):
        if key == curses.KEY_DOWN:
            self.selected_option = (self.selected_option + 1) % len(self.options)
        elif key == curses.KEY_UP:
            self.selected_option = (self.selected_option - 1) % len(self.options)
        elif key == ord('\n') or key == curses.KEY_RIGHT:
            return self.selected_option
