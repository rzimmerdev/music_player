import curses
import threading
from abc import abstractmethod, ABC
from tkinter import Menu

from ..song import Song
from ..youtube import Remote


class Screen(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def draw(self, stdscr) -> None:
        pass

    @abstractmethod
    def tick(self, key):
        pass


def do_return(key):
    # esc
    return key == 27


class MenuHistory(Menu):
    def __init__(self, starting_screen: Screen = None):
        super().__init__()
        self.history = [starting_screen] if starting_screen else []

    def push(self, screen):
        self.history.append(screen)

    def pop(self):
        return self.history.pop()

    @property
    def current(self):
        return self.history[-1]

    def draw(self, stdscr):
        self.current.draw(stdscr)

    def tick(self, key):
        current_screen = self.current
        new_screen = current_screen.tick(key)

        # Backspace
        if do_return(key):
            if len(self.history) > 1:
                self.pop()
                return self
            return None

        if new_screen is not current_screen and new_screen is not None:
            self.push(new_screen)

        return self


class MainMenuScreen(Screen):
    def __init__(self, window):
        super().__init__()
        self.selected = 0
        self.window = window
        self.youtube = Remote()

    def draw(self, stdscr) -> None:
        # Draw currently selected option with a >
        options = ["Search", "Playlists", "Exit"]

        for i, option in enumerate(options):
            if i == self.selected:
                stdscr.addstr(i, 0, f"> {option}")
            else:
                stdscr.addstr(i, 0, f"  {option}")

    def tick(self, key):
        if key == curses.KEY_UP:
            self.selected = max(0, self.selected - 1)
        elif key == curses.KEY_DOWN:
            self.selected = min(2, self.selected + 1)
        elif key == ord("\n") or key == ord(" "):
            if self.selected == 0:
                return SearchScreen(self.window)
            elif self.selected == 1:
                return None
            elif self.selected == 2:
                raise KeyboardInterrupt
        return self


class SongScreen(Screen):
    def __init__(self, song: Song, player):
        super().__init__()
        self.song = song
        self.player = player
        stream = Remote.get_stream(song.url)
        self.player.set(stream)

    def draw(self, stdscr) -> None:
        stdscr.addstr(0, 0, "ZimbaFY")
        image = self.song.thumb_ascii.split("\n")
        for i, line in enumerate(image):
            stdscr.addstr(i + 1, 0, line)

        j = len(image[0]) + 1
        stdscr.addstr(0, j, f"Listening to: {self.song.title} - {self.song.author}")
        # current time (seconds / total time (seconds))
        # also show bar
        # [%%%%%%%%] 0:00 / 3:45 (max bar is 15 chars
        if self.player.length:
            bar = "-"
            percentage = self.player.time / self.player.length
            current_bar = f"[{bar * int(percentage * 15):15}] "
            stdscr.addstr(2, j, current_bar)
            time_spent = f"{self.player.time // 1000 // 60}:{self.player.time // 1000 % 60:02}"
            total_time = f"{self.player.length // 1000 // 60}:{self.player.length // 1000 % 60:02}"
            stdscr.addstr(2, j + 18, f"{time_spent} / {total_time}")

        controls = "⇆(S)ㅤ◁ㅤ ❚❚(Space) ㅤ▷ㅤ↻(R)"
        stdscr.addstr(3, j, controls)

        if self.player.volume:
            # max volume is 200
            bar = "▮"
            volume = self.player.volume
            current_bar = f"[{bar * int(volume / 10):20}] "
            stdscr.addstr(5, j, current_bar)
            stdscr.addstr(5, j + 22, f"{volume}%")

        volume_controls = "△(Up) ㅤ▽(Down)"
        stdscr.addstr(6, j, volume_controls)

    def tick(self, key):
        # space or enter
        if key == ord(" ") or key == ord("\n"):
            if self.player.playing:
                self.player.pause()
            else:
                self.player.start()
        elif key == ord("t") or key == ord("T") or do_return(key):
            self.player.stop()
        elif key == ord("r"):
            self.player.restart()
        if key == curses.KEY_RIGHT:
            self.player.time = min(self.player.length, self.player.time + 5000)
        elif key == curses.KEY_LEFT:
            self.player.time = max(0, self.player.time - 5000)
        elif key == curses.KEY_UP:
            self.player.volume = min(200, self.player.volume + 10)
        elif key == curses.KEY_DOWN:
            self.player.volume = max(0, self.player.volume - 10)
        return None


class SearchScreen(Screen):
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.selected = 0
        self.results = []
        self.query = ""
        self.youtube = Remote()
        self.search_delay = 0.1  # delay in seconds
        self.search_timer = None
        self.search_active = False

    def draw(self, stdscr) -> None:
        stdscr.addstr(0, 0, "ZimbaFY")
        stdscr.addstr(1, 0, f"Search: {self.query}")
        for i, video in enumerate(self.results):
            if i == self.selected:
                stdscr.addstr(i + 2, 0, f"> {video.title} - {video.author}")
            else:
                stdscr.addstr(i + 2, 0, f"  {video.title} - {video.author}")

    def search(self):
        if self.search_active:
            self.results = self.youtube.search(self.query, n=5)
            self.selected = 0

    def start_search_timer(self):
        self.search_active = False  # Deactivate the previous search
        if self.search_timer is not None:
            self.search_timer.cancel()
        self.search_active = True  # Activate the current search
        self.search_timer = threading.Timer(self.search_delay, self.search)
        self.search_timer.start()

    def tick(self, key):
        if key == -1:
            return None
        elif key == ord("\n"):
            if self.selected < len(self.results):
                return SongScreen(self.results[self.selected].to_song(self.window), self.window.player)
        elif key == curses.KEY_UP:
            self.selected = max(0, self.selected - 1)
        elif key == curses.KEY_DOWN:
            self.selected = min(len(self.results) - 1, self.selected + 1)
        elif key == 127:
            self.query = self.query[:-1]
            self.start_search_timer()
        elif 32 <= key <= 126:
            self.query += chr(key)
            self.start_search_timer()
        elif key == 263:
            # backspace
            self.query = self.query[:-1] if self.query else ""
            self.start_search_timer()
        return None
