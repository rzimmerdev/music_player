import curses
import threading
import time
from abc import abstractmethod, ABC
from tkinter import Menu

from ..song import Song
from ..visualizer import Visualizer
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
    def __init__(self, song: Song, window):
        super().__init__()
        self.song = song
        self.window = window

        self.player = window.player
        self.player.set(Remote.get_stream(song.url))

        self.visualizer = Visualizer(5, 41)
        self.visualizer.start(self.window.stdscr)

    def draw(self, stdscr) -> None:
        stdscr.addstr(0, 0, f"{self.visualizer.thread}")
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

        self.visualizer.rows = len(image) - 8
        self.visualizer.cols = self.visualizer.rows * 5
        visual = self.visualizer.visual()
        for i, line in enumerate(visual.split("\n")):
            # clear waveform row
            stdscr.addstr(i + 8, j, line)

    def tick(self, key):
        # space or enter
        if key == ord(" ") or key == ord("\n"):
            if self.player.playing:
                self.player.pause()
                self.visualizer.toggle()
            else:
                self.player.start()
                self.visualizer.toggle()
        elif key == ord("t") or key == ord("T") or do_return(key):
            self.player.stop()
            self.visualizer.stop()
        elif key == ord("r"):
            self.player.restart()
            self.visualizer.restart(self.window.stdscr)
        if key == curses.KEY_RIGHT:
            self.player.time = min(self.player.length, self.player.time + 5000)
        elif key == curses.KEY_LEFT:
            self.player.time = max(0, self.player.time - 5000)
        elif key == curses.KEY_UP:
            self.player.volume = min(200, self.player.volume + 10)
        elif key == curses.KEY_DOWN:
            self.player.volume = max(0, self.player.volume - 10)
        return None


class ResettableTimer:
    def __init__(self, interval, callback, dt=1e-3):
        self.remaining = 0
        self.starting_time = interval
        self.dt = dt
        self.callback = callback
        self.thread = None

    def run(self):
        while self.remaining > 0:
            time.sleep(self.dt)
            self.remaining -= self.dt
        self.callback()

    def reset(self):
        if self.remaining <= 0:
            self.remaining = self.starting_time
            self.thread = threading.Thread(target=self.run)
            self.thread.start()
        else:
            self.remaining = self.starting_time

    def stop(self):
        self.remaining = 0


class SearchScreen(Screen):
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.selected = 0
        self.results = []
        self.query = ""
        self.youtube = Remote()
        self.stdscr = None
        self.timer = ResettableTimer(0.2, self.search)

    def draw(self, stdscr) -> None:
        stdscr.addstr(0, 0, "ZimbaFY")
        stdscr.addstr(1, 0, f"Search: {self.query}")
        for i, video in enumerate(self.results):
            if i == self.selected:
                stdscr.addstr(i + 2, 0, f"> {video.title} - {video.author}")
            else:
                stdscr.addstr(i + 2, 0, f"  {video.title} - {video.author}")

    def search(self):
        self.results = self.youtube.search(self.query, n=5)
        self.selected = 0

    def tick(self, key):
        if key == -1:
            return None
        elif key == ord("\n"):
            if self.selected < len(self.results):
                return SongScreen(self.results[self.selected].to_song(self.window), self.window)
        elif key == curses.KEY_UP:
            self.selected = max(0, self.selected - 1)
        elif key == curses.KEY_DOWN:
            self.selected = min(len(self.results) - 1, self.selected + 1)
        elif key == 127:
            self.query = self.query[:-1]
            self.timer.reset()
        elif 32 <= key <= 126:
            self.query += chr(key)
            self.timer.reset()
        elif key == 263:
            # backspace
            self.query = self.query[:-1] if self.query else ""
            self.timer.reset()
        return None
