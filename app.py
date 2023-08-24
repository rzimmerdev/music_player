import curses
import sounddevice as sd
import librosa
import threading


playlists = {
    "name1": {
        "song1": {"name": "Baby", "url": "songs/The_Curse.mp3"},
        "song2": {"name": "Song 2", "url": "songs/song2.mp3"}
    },
    "name2": {
        "song3": {"name": "Song 3", "url": "songs/song3.mp3"},
        "song4": {"name": "Song 4", "url": "songs/song4.mp3"}
    }
}


def draw_menu(stdscr, selected_playlist):
    stdscr.clear()
    stdscr.addstr("Select a playlist:\n")

    for playlist_name in playlists.keys():
        if playlist_name == selected_playlist:
            stdscr.addstr(f"-> {playlist_name}\n", curses.A_REVERSE)
        else:
            stdscr.addstr(f"   {playlist_name}\n")

    stdscr.refresh()


def draw_songs(stdscr, playlist_name, selected_song):
    stdscr.clear()
    stdscr.addstr(f"Playlist: {playlist_name}\n")
    stdscr.addstr("Select a song:\n")

    songs = playlists[playlist_name]
    for song_name, song_data in songs.items():
        if song_name == selected_song:
            stdscr.addstr(f"-> {song_data['name']}\n", curses.A_REVERSE)
        else:
            stdscr.addstr(f"   {song_data['name']}\n")

    stdscr.refresh()


def main(stdscr):
    curses.curs_set(0)
    current_playlist = list(playlists.keys())[0]
    current_song = None
    is_selecting_playlist = True

    try:

        while True:
            if is_selecting_playlist:
                draw_menu(stdscr, current_playlist)
            else:
                draw_songs(stdscr, current_playlist, current_song)

            key = stdscr.getch()

            if is_selecting_playlist:
                if key == curses.KEY_DOWN:
                    current_playlist = list(playlists.keys())[
                        (list(playlists.keys()).index(current_playlist) + 1) % len(playlists)]
                elif key == curses.KEY_UP:
                    current_playlist = list(playlists.keys())[
                        (list(playlists.keys()).index(current_playlist) - 1) % len(playlists)]
                elif key == ord('\n'):
                    is_selecting_playlist = False
                    current_song = list(playlists[current_playlist].keys())[0]
            else:
                if key == curses.KEY_DOWN:
                    current_song = list(playlists[current_playlist].keys())[
                        (list(playlists[current_playlist].keys()).index(current_song) + 1) % len(
                            playlists[current_playlist])]
                elif key == curses.KEY_UP:
                    current_song = list(playlists[current_playlist].keys())[
                        (list(playlists[current_playlist].keys()).index(current_song) - 1) % len(
                            playlists[current_playlist])]
                elif key == ord('\n'):
                    song_url = playlists[current_playlist][current_song]['url']
                    stdscr.addstr(f"Playing: {playlists[current_playlist][current_song]['name']}\n")
                    stdscr.addstr("Press Enter to stop playback...\n")
                    playback_thread = threading.Thread(target=play_audio, args=(song_url,))
                    playback_thread.start()
                    stdscr.getch()
                    stop_audio()
                    playback_thread.join()
                    stdscr.refresh()
                    stdscr.getch()
    except KeyboardInterrupt:
        print("Exiting...")


def play_audio(file_path):
    data, sr = librosa.load(file_path, sr=None)
    sd.play(data, sr)


def stop_audio():
    sd.stop()


if __name__ == "__main__":
    curses.wrapper(main)
