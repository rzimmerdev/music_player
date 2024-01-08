import curses

from src.views import Window
from src.views.menus.content import ContentMenu


def main(stdscr):
    content_menu = ContentMenu()
    window = Window(stdscr, content_menu)

    try:
        while True:
            window.render()
            key = stdscr.getch()
            window.update(key)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    curses.wrapper(main)
