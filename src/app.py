import os

import curses
import signal

from .player import AudioStream


def extract_name(file_path):
    return os.path.splitext(os.path.basename(file_path))[0]


def get_music(directory_path):
    _local_songs = {directory_path: {}}

    for filename in os.listdir(directory_path):
        if filename.endswith(".mp3"):
            name = extract_name(filename)
            url = os.path.join(directory_path, filename)
            _local_songs[directory_path][name] = url
        elif os.path.isdir(os.path.join(directory_path, filename)):
            _local_songs[filename] = {}

            for file in os.listdir(os.path.join(directory_path, filename)):
                if file.endswith(".mp3"):
                    name = extract_name(file)
                    url = os.path.join(directory_path, filename, file)
                    _local_songs[filename][name] = url

    return _local_songs


def draw_menu(stdscr, available_music, selected_playlist):
    stdscr.clear()
    stdscr.addstr("Select a playlist:\n")

    for playlist_name in available_music:
        if playlist_name == selected_playlist:
            stdscr.addstr(f"-> {playlist_name}\n", curses.A_REVERSE)
        else:
            stdscr.addstr(f"   {playlist_name}\n")

    stdscr.refresh()


def draw_songs(stdscr, available_music, selected_playlist, selected_song):
    stdscr.clear()
    stdscr.addstr(f"Playlist: {selected_playlist}\n")
    stdscr.addstr("Select a song:\n")

    selected_playlist_music = available_music[selected_playlist]

    for song_name, url in selected_playlist_music.items():
        if song_name == selected_song:
            stdscr.addstr(f"-> {song_name}\n", curses.A_REVERSE)
        else:
            stdscr.addstr(f"   {song_name}\n")

    stdscr.refresh()


class App:
    def __init__(self, stdscr, directory_path):
        self.music = get_music(directory_path)

        self.current_playlist = list(self.music.keys())[0]
        self.current_song = None
        self.audio_stream = None
        self.is_selecting_playlist = True

        self.stdscr = stdscr
        self.stdscr.nodelay(1)
        curses.curs_set(0)

        signal.signal(signal.SIGINT, self.handle_interrupt)

    def load_song(self, song):
        self.current_song = song
        self.is_selecting_playlist = False

    def render(self):
        if self.is_selecting_playlist:
            draw_menu(self.stdscr, self.music, self.current_playlist)
        else:
            draw_songs(self.stdscr, self.music, self.current_playlist, self.current_song)

    def handle_interrupt(self, signum, frame):
        raise KeyboardInterrupt

    def run(self):
        try:
            while True:
                self.render()
                key = self.stdscr.getch()
                if key != -1:
                    pass
                if key == curses.KEY_BACKSPACE or key == 8 or key == ord(" "):
                    if self.audio_stream:
                        self.audio_stream.stop()
                if self.is_selecting_playlist:
                    if key == curses.KEY_DOWN:
                        self.current_playlist = list(self.music.keys())[
                            (list(self.music.keys()).index(self.current_playlist) + 1) % len(self.music)]
                    elif key == curses.KEY_UP:
                        self.current_playlist = list(self.music.keys())[
                            (list(self.music.keys()).index(self.current_playlist) - 1) % len(self.music)]
                    elif key == ord('\n') or key == curses.KEY_RIGHT:
                        self.is_selecting_playlist = False
                        self.current_song = list(self.music[self.current_playlist].keys())[0]
                else:
                    if key == curses.KEY_DOWN:
                        self.current_song = list(self.music[self.current_playlist].keys())[
                            (list(self.music[self.current_playlist].keys()).index(self.current_song) + 1) % len(
                                self.music[self.current_playlist])]
                    elif key == curses.KEY_UP:
                        self.current_song = list(self.music[self.current_playlist].keys())[
                            (list(self.music[self.current_playlist].keys()).index(self.current_song) - 1) % len(
                                self.music[self.current_playlist])]
                    elif key == curses.KEY_LEFT:
                        self.is_selecting_playlist = True
                    elif key == ord('\n') or key == curses.KEY_RIGHT:
                        if self.audio_stream:
                            self.audio_stream.stop()
                        url = self.music[self.current_playlist][self.current_song]
                        self.audio_stream = AudioStream(url)
                        self.audio_stream.start()

        except KeyboardInterrupt:
            if self.audio_stream:
                self.audio_stream.stop()
            print("Exiting...")
