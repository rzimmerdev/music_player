from enum import Enum
from .screens import Screen


class Header(Screen):
    def __init__(self, title, *args, **kwargs):
        self.title = title
        self.style = args, kwargs

    def draw(self, stdscr):
        stdscr.addstr(self.title, *self.style[0], **self.style[1])


class Footer(Screen):
    def __init__(self):
        self.controls = MusicControl()
        self.volume = VolumeBar()
        self.progress = ProgressBar()

    def draw(self, stdscr):
        self.progress.draw(stdscr)
        self.controls.draw(stdscr)
        self.volume.draw(stdscr)


class MusicControl(Screen):
    class Controls(Enum):
        PLAY = "P"
        PAUSE = "p"
        NEXT = "N"
        PREVIOUS = "n"
        VOLUME_UP = "V"
        VOLUME_DOWN = "v"

    def __init__(self):
        self.playing = False

    def draw(self, stdscr):
        stdscr.addstr(1, 0, f"Playing: {self.playing}")

        stdscr.addstr(4, 0, f"Controls:")
        stdscr.addstr(5, 0, f"Play/Pause: {self.Controls.PLAY.value}/{self.Controls.PAUSE.value}")
        stdscr.addstr(6, 0, f"Next/Previous: {self.Controls.NEXT.value}/{self.Controls.PREVIOUS.value}")
        stdscr.addstr(7, 0, f"Volume Up/Down: {self.Controls.VOLUME_UP.value}/{self.Controls.VOLUME_DOWN.value}")


class VolumeBar(Screen):
    class Volume(Enum):
        ZERO = "🔇"
        ONE = "🔈"
        TWO = "🔉"
        THREE = "🔊"

    def __init__(self, max_volume=3):
        self._volume = 0
        self.max_volume = max_volume

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value):
        self._volume = value
        self.cap()

    def cap(self):
        if self.volume > self.max_volume:
            self.volume = self.max_volume
        elif self.volume < 0:
            self.volume = 0

    def draw(self, stdscr):
        stdscr.addstr(1, 0, f"Volume: {self.Volume(self.volume).value}")


class ProgressBar(Screen):
    class Progress(Enum):
        EMPTY = "_"
        FILLED = "#"

    def __init__(self, bar_length=10):
        self.bar_length = bar_length
        self._progress = 0

        self.filled_length = 0
        self.empty_length = bar_length

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value):
        self._progress = value
        self.cap()
        self.update()

    def update(self):
        self.filled_length = int(self.progress / 100 * self.bar_length)
        self.empty_length = self.bar_length - self.filled_length

    def cap(self):
        if self.progress > 100:
            self.progress = 100
        elif self.progress < 0:
            self.progress = 0

    def draw(self, stdscr):
        stdscr.addstr(1, 0, "[")
        stdscr.addstr(1, 1, self.Progress.FILLED.value * self.filled_length)
        stdscr.addstr(1, self.filled_length + 1, self.Progress.EMPTY.value * self.empty_length)
        stdscr.addstr(1, self.bar_length + 1, "]")
