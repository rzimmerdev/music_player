import curses
from abc import ABC, abstractmethod


class Screen(ABC):

    @abstractmethod
    def draw(self, stdscr: curses.window):
        pass
