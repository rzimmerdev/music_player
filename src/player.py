import os

import vlc

os.environ['VLC_VERBOSE'] = '-1'


class Player:
    def __init__(self, url=None):
        self.url = url
        self.media = None

    def set(self, url):
        self.url = url
        self.media = vlc.MediaPlayer(url)
        return self

    def start(self):
        self.media.play()

    def stop(self):
        self.media.stop()

    def pause(self):
        self.media.pause()

    def restart(self):
        self.media.stop()
        self.media.play()

    @property
    def length(self):
        return self.media.get_length()

    @property
    def time(self):
        return self.media.get_time()

    @property
    def playing(self):
        return self.media.is_playing()

    @time.setter
    def time(self, time):
        self.media.set_time(time)

    @property
    def volume(self):
        return self.media.audio_get_volume()

    @volume.setter
    def volume(self, volume):
        self.media.audio_set_volume(volume)

    def waveform(self, width=100, height=10):
        return ""


if __name__ == "__main__":
    player = Player("songs/The_Curse.mp3")
    player.start()
    input("Press Enter to stop playback...\n")
    player.stop()

