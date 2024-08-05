import os
import curses

from src.views import Window, MainMenuScreen, MenuHistory


def main(stdscr):
    # create songs/ and thumb/ directories
    os.makedirs("songs", exist_ok=True)
    os.makedirs("thumb", exist_ok=True)
    window = Window(stdscr)
    window.screen = MenuHistory(MainMenuScreen(window))

    try:
        while window.alive:
            window.render()
            key = stdscr.getch()
            window.tick(key)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    curses.wrapper(main)
