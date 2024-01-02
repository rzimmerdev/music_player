import curses

from src.player import Song
from src.views import Window, SongMenu


def main(stdscr):
    starting_menu = SongMenu(Song("test", "test"))
    window = Window(stdscr, starting_menu)

    try:
        while True:
            window.render()
            key = stdscr.getch()
            window.update(key)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    curses.wrapper(main)
