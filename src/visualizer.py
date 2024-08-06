import threading

import pyaudio
import numpy as np


class Visualizer:
    def __init__(self, rows, cols):
        self.chunk = 1024
        self.rate = 44100
        self.channels = 2
        self.audio = None
        self.stream = None
        self.thread = None
        self.running = threading.Event()
        self.paused = threading.Event()
        self.paused.set()

        self.rows = rows
        self.cols = cols
        self._visual = np.full((rows, cols), ' ', dtype='<U1')

    def transform(self, data):
        rows, cols = self.rows, self.cols

        audio_data = np.frombuffer(data, dtype=np.int16)
        chunk_size = len(audio_data) // (cols * 2)
        visualizer = np.zeros(cols // 2 + 1, dtype=int)

        for j in range(cols // 2):
            start = j * chunk_size
            end = start + chunk_size

            if end > len(audio_data):
                end = len(audio_data)

            segment = audio_data[start:end]
            segment = segment.astype(np.float32)
            # remove nans
            segment = segment[~np.isnan(segment)]
            volume = np.sqrt(np.mean(np.square(segment)))
            if volume == 0 or np.isnan(volume):
                volume = 0
            bars = int((volume / 1000) * rows)
            visualizer[j] = max(min(rows, bars), 0)

        center = cols // 2
        self._visual = np.full((rows, cols), ' ', dtype='<U1')
        for j in range(cols // 2):
            bars = visualizer[j]
            for i in range(rows - 1, rows - bars - 1, -1):
                self._visual[i, center + j] = '|'
                self._visual[i, center - j] = '|'

    def visual(self):
        return '\n'.join('|' + ''.join(row) + '|' for row in self._visual)

    def _listen(self):
        while self.running.is_set():
            data = self.stream.read(self.chunk, exception_on_overflow=False)
            if self.paused.is_set():
                continue
            self.transform(data)

    def start(self, stdscr):
        # listen to desktop
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=pyaudio.paInt16,
                                      channels=2,
                                      rate=44100,
                                      input=True,
                                      frames_per_buffer=self.chunk)
        # requires clearing the screen
        self.running.set()
        self.thread = threading.Thread(target=self._listen)
        self.thread.start()
        stdscr.clear()

    def toggle(self):
        if self.paused.is_set():
            self.paused.clear()
        else:
            self.paused.set()

    def stop(self):
        self.running.clear()
        self.thread.join()
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

    def restart(self, stdscr):
        self.stop()
        self.start(stdscr)
