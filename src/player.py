import os

import vlc

os.environ['VLC_VERBOSE'] = '-1'


class Player:
    def __init__(self, url=None):
        self.url = url
        self.player = None

    def set(self, url):
        self.url = url
        self.player = vlc.MediaPlayer(url)
        return self

    def start(self):
        self.player.play()

    def stop(self):
        self.player.stop()

    def pause(self):
        self.player.pause()

    def restart(self):
        self.player.stop()
        self.player.play()

    @property
    def length(self):
        return self.player.get_length()

    @property
    def time(self):
        return self.player.get_time()

    @property
    def playing(self):
        return self.player.is_playing()

    @time.setter
    def time(self, time):
        self.player.set_time(time)

    @property
    def volume(self):
        return self.player.audio_get_volume()

    @volume.setter
    def volume(self, volume):
        self.player.audio_set_volume(volume)


if __name__ == "__main__":
    player = Player("songs/The_Curse.mp3")
    player.start()
    input("Press Enter to stop playback...\n")
    player.stop()

