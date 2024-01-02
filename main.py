import curses

from src import App


def main(stdscr):
    app = App(stdscr, "music")
    app.run()


if __name__ == "__main__":
    curses.wrapper(main)
