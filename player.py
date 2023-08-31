import pyaudio
import threading
from pydub import AudioSegment


class AudioStream:
    def __init__(self, file_path, segment_duration_ms=1000, sample_rate=44100):
        self.file_path = file_path
        self.segment_duration_ms = segment_duration_ms
        self.sample_rate = sample_rate
        self.audio = pyaudio.PyAudio()
        self.segments = self._create_audio_segments()
        self.playing = threading.Event()
        self.thread = None

    def _create_audio_segments(self):
        audio = AudioSegment.from_mp3(self.file_path)
        segments = [audio[i:i + self.segment_duration_ms] for i in range(0, len(audio), self.segment_duration_ms)]
        return segments

    def _stream_loop(self):
        stream = self.audio.open(format=self.audio.get_format_from_width(self.segments[0].sample_width),
                                 channels=self.segments[0].channels,
                                 rate=self.sample_rate,
                                 output=True)

        for segment in self.segments:
            if not self.playing.is_set():
                break
            stream.write(segment.raw_data)

        stream.stop_stream()
        stream.close()

    def start(self):
        if not self.playing.is_set():
            self.playing.set()
            self.thread = threading.Thread(target=self._stream_loop)
            self.thread.start()

    def stop(self):
        if self.playing.is_set():
            self.playing.clear()
            self.thread.join()
            self.thread = None
            self.audio.terminate()


if __name__ == "__main__":
    player = AudioStream("songs/The_Curse.mp3")
    player.start()
    input("Press Enter to stop playback...\n")
    player.stop()

